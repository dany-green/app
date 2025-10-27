from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone

from models import (
    User, UserCreate, UserLogin, UserResponse, Token,
    Project, ProjectCreate, ProjectUpdate, ProjectStatus,
    InventoryItem, InventoryItemCreate, InventoryItemUpdate,
    LogEntry, LogEntryCreate, UserRole, TokenData
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, get_current_admin_user, get_current_curator_or_admin
)
from storage_service import storage_service


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'sls1_db')]

# Create the main app without a prefix
app = FastAPI(title="SLS1 Organizational Platform API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Helper function to serialize datetime for MongoDB
def serialize_for_db(doc: dict) -> dict:
    """Convert datetime objects to ISO strings for MongoDB storage"""
    for key, value in doc.items():
        if isinstance(value, datetime):
            doc[key] = value.isoformat()
    return doc


def deserialize_from_db(doc: dict) -> dict:
    """Convert ISO string timestamps back to datetime objects"""
    for key, value in doc.items():
        if isinstance(value, str) and key.endswith(('_at', '_date', 'timestamp', 'last_login')):
            try:
                doc[key] = datetime.fromisoformat(value)
            except:
                pass
    return doc


# ============== AUTHENTICATION ROUTES ==============

@api_router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, current_user: TokenData = Depends(get_current_admin_user)):
    """Register a new user (Admin only)"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user
    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role
    )
    
    doc = serialize_for_db(user.model_dump())
    await db.users.insert_one(doc)
    
    # Log the action
    log = LogEntry(
        user_id=current_user.user_id,
        user_name=current_user.email,
        action="CREATE",
        entity_type="USER",
        entity_id=user.id,
        details={"user_name": user.name, "role": user.role.value}
    )
    await db.logs.insert_one(serialize_for_db(log.model_dump()))
    
    return UserResponse(**user.model_dump())


@api_router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login and get JWT token"""
    user_doc = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    
    if not user_doc or not verify_password(credentials.password, user_doc['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user_doc.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    await db.users.update_one(
        {"id": user_doc['id']},
        {"$set": {"last_login": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": user_doc['id'],
            "email": user_doc['email'],
            "role": user_doc['role']
        }
    )
    
    return Token(access_token=access_token)


@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """Get current user information"""
    user_doc = await db.users.find_one({"id": current_user.user_id}, {"_id": 0, "password_hash": 0})
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**deserialize_from_db(user_doc))


# ============== USER MANAGEMENT ROUTES ==============

@api_router.get("/users", response_model=List[UserResponse])
async def get_users(current_user: TokenData = Depends(get_current_admin_user)):
    """Get all users (Admin only)"""
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).to_list(1000)
    return [UserResponse(**deserialize_from_db(user)) for user in users]


@api_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: TokenData = Depends(get_current_admin_user)):
    """Get user by ID (Admin only)"""
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**deserialize_from_db(user_doc))


@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: TokenData = Depends(get_current_admin_user)):
    """Delete user (Admin only)"""
    result = await db.users.delete_one({"id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Log the action
    log = LogEntry(
        user_id=current_user.user_id,
        user_name=current_user.email,
        action="DELETE",
        entity_type="USER",
        entity_id=user_id
    )
    await db.logs.insert_one(serialize_for_db(log.model_dump()))
    
    return {"message": "User deleted successfully"}


# ============== PROJECT ROUTES ==============

@api_router.get("/projects", response_model=List[Project])
async def get_projects(current_user: TokenData = Depends(get_current_user)):
    """Get all projects"""
    projects = await db.projects.find({}, {"_id": 0}).to_list(1000)
    return [Project(**deserialize_from_db(project)) for project in projects]


@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str, current_user: TokenData = Depends(get_current_user)):
    """Get project by ID"""
    project_doc = await db.projects.find_one({"id": project_id}, {"_id": 0})
    
    if not project_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return Project(**deserialize_from_db(project_doc))


@api_router.post("/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(project_data: ProjectCreate, current_user: TokenData = Depends(get_current_user)):
    """Create a new project"""
    project = Project(
        **project_data.model_dump(),
        created_by=current_user.user_id
    )
    
    doc = serialize_for_db(project.model_dump())
    await db.projects.insert_one(doc)
    
    # Log the action
    log = LogEntry(
        user_id=current_user.user_id,
        user_name=current_user.email,
        action="CREATE",
        entity_type="PROJECT",
        entity_id=project.id,
        details={"title": project.title}
    )
    await db.logs.insert_one(serialize_for_db(log.model_dump()))
    
    return project


@api_router.patch("/projects/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """Update project"""
    # Get existing project
    existing_project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not existing_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update only provided fields
    update_data = {k: v for k, v in project_data.model_dump(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.projects.update_one(
        {"id": project_id},
        {"$set": serialize_for_db(update_data)}
    )
    
    # Log the action
    log = LogEntry(
        user_id=current_user.user_id,
        user_name=current_user.email,
        action="UPDATE",
        entity_type="PROJECT",
        entity_id=project_id,
        details=update_data
    )
    await db.logs.insert_one(serialize_for_db(log.model_dump()))
    
    # Get updated project
    updated_project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    return Project(**deserialize_from_db(updated_project))


@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str, current_user: TokenData = Depends(get_current_admin_user)):
    """Delete project (Admin only)"""
    result = await db.projects.delete_one({"id": project_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Log the action
    log = LogEntry(
        user_id=current_user.user_id,
        user_name=current_user.email,
        action="DELETE",
        entity_type="PROJECT",
        entity_id=project_id
    )
    await db.logs.insert_one(serialize_for_db(log.model_dump()))
    
    return {"message": "Project deleted successfully"}


# ============== INVENTORY ROUTES ==============

@api_router.get("/inventory", response_model=List[InventoryItem])
async def get_inventory(current_user: TokenData = Depends(get_current_user)):
    """Get all inventory items"""
    items = await db.inventory.find({}, {"_id": 0}).to_list(1000)
    return [InventoryItem(**deserialize_from_db(item)) for item in items]


@api_router.get("/inventory/{item_id}", response_model=InventoryItem)
async def get_inventory_item(item_id: str, current_user: TokenData = Depends(get_current_user)):
    """Get inventory item by ID"""
    item_doc = await db.inventory.find_one({"id": item_id}, {"_id": 0})
    
    if not item_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    return InventoryItem(**deserialize_from_db(item_doc))


@api_router.post("/inventory", response_model=InventoryItem, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    item_data: InventoryItemCreate,
    current_user: TokenData = Depends(get_current_curator_or_admin)
):
    """Create new inventory item (Curator or Admin only)"""
    item = InventoryItem(**item_data.model_dump())
    
    doc = serialize_for_db(item.model_dump())
    await db.inventory.insert_one(doc)
    
    # Log the action
    log = LogEntry(
        user_id=current_user.user_id,
        user_name=current_user.email,
        action="CREATE",
        entity_type="INVENTORY",
        entity_id=item.id,
        details={"name": item.name, "quantity": item.total_quantity}
    )
    await db.logs.insert_one(serialize_for_db(log.model_dump()))
    
    return item


@api_router.patch("/inventory/{item_id}", response_model=InventoryItem)
async def update_inventory_item(
    item_id: str,
    item_data: InventoryItemUpdate,
    current_user: TokenData = Depends(get_current_curator_or_admin)
):
    """Update inventory item (Curator or Admin only)"""
    existing_item = await db.inventory.find_one({"id": item_id}, {"_id": 0})
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    update_data = {k: v for k, v in item_data.model_dump(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.inventory.update_one(
        {"id": item_id},
        {"$set": serialize_for_db(update_data)}
    )
    
    # Log the action
    log = LogEntry(
        user_id=current_user.user_id,
        user_name=current_user.email,
        action="UPDATE",
        entity_type="INVENTORY",
        entity_id=item_id,
        details=update_data
    )
    await db.logs.insert_one(serialize_for_db(log.model_dump()))
    
    updated_item = await db.inventory.find_one({"id": item_id}, {"_id": 0})
    return InventoryItem(**deserialize_from_db(updated_item))


@api_router.delete("/inventory/{item_id}")
async def delete_inventory_item(
    item_id: str,
    current_user: TokenData = Depends(get_current_admin_user)
):
    """Delete inventory item (Admin only)"""
    result = await db.inventory.delete_one({"id": item_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    # Log the action
    log = LogEntry(
        user_id=current_user.user_id,
        user_name=current_user.email,
        action="DELETE",
        entity_type="INVENTORY",
        entity_id=item_id
    )
    await db.logs.insert_one(serialize_for_db(log.model_dump()))
    
    return {"message": "Inventory item deleted successfully"}


# ============== LOGS ROUTES ==============

@api_router.get("/logs", response_model=List[LogEntry])
async def get_logs(
    limit: int = 100,
    current_user: TokenData = Depends(get_current_admin_user)
):
    """Get activity logs (Admin only)"""
    logs = await db.logs.find({}, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    return [LogEntry(**deserialize_from_db(log)) for log in logs]


# ============== INIT ROUTE ==============

@api_router.post("/init")
async def initialize_database():
    """Initialize database with default admin user"""
    # Check if admin already exists
    existing_admin = await db.users.find_one({"role": UserRole.ADMIN.value}, {"_id": 0})
    
    if existing_admin:
        return {"message": "Database already initialized"}
    
    # Create default admin user
    admin = User(
        name="Administrator",
        email="admin@sls1.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN
    )
    
    doc = serialize_for_db(admin.model_dump())
    await db.users.insert_one(doc)
    
    # Create some sample inventory items
    sample_items = [
        InventoryItem(category="Вазы", name="Ваза стеклянная большая", total_quantity=10, visual_marker="🔴"),
        InventoryItem(category="Вазы", name="Ваза керамическая средняя", total_quantity=15, visual_marker="🔵"),
        InventoryItem(category="Текстиль", name="Скатерть белая 3x2м", total_quantity=20, visual_marker="🟢"),
        InventoryItem(category="Декор", name="Свечи декоративные", total_quantity=50, visual_marker="🟡"),
    ]
    
    for item in sample_items:
        await db.inventory.insert_one(serialize_for_db(item.model_dump()))
    
    return {
        "message": "Database initialized successfully",
        "admin_credentials": {
            "email": "admin@sls1.com",
            "password": "admin123"
        }
    }


# ============== GENERAL ROUTES ==============

@api_router.get("/")
async def root():
    return {
        "message": "SLS1 Organizational Platform API",
        "version": "1.0.0",
        "status": "operational"
    }


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()