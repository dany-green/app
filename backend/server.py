from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from models import (
    User, UserCreate, UserLogin, UserResponse, Token,
    Project, ProjectCreate, ProjectUpdate, ProjectStatus,
    InventoryItem, InventoryItemCreate, InventoryItemUpdate,
    EquipmentItem, EquipmentItemCreate, EquipmentItemUpdate,
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


# ============== EQUIPMENT ROUTES ==============

@api_router.get("/equipment", response_model=List[EquipmentItem])
async def get_equipment(current_user: TokenData = Depends(get_current_user)):
    """Get all equipment items"""
    equipment = await db.equipment.find({}, {"_id": 0}).to_list(1000)
    return [EquipmentItem(**deserialize_from_db(item)) for item in equipment]


@api_router.get("/equipment/{item_id}", response_model=EquipmentItem)
async def get_equipment_item(
    item_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get a single equipment item"""
    item = await db.equipment.find_one({"id": item_id}, {"_id": 0})
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment item not found"
        )
    
    return EquipmentItem(**deserialize_from_db(item))


@api_router.post("/equipment", response_model=EquipmentItem, status_code=status.HTTP_201_CREATED)
async def create_equipment_item(
    item_data: EquipmentItemCreate,
    current_user: TokenData = Depends(get_current_curator_or_admin)
):
    """Create a new equipment item (Curator or Admin)"""
    item = EquipmentItem(**item_data.model_dump())
    
    doc = serialize_for_db(item.model_dump())
    await db.equipment.insert_one(doc)
    
    # Log the action
    log = LogEntry(
        user_id=current_user.user_id,
        user_name=current_user.email,
        action="CREATE",
        entity_type="EQUIPMENT",
        entity_id=item.id,
        details={"name": item.name, "category": item.category}
    )
    await db.logs.insert_one(serialize_for_db(log.model_dump()))
    
    return item


@api_router.patch("/equipment/{item_id}", response_model=EquipmentItem)
async def update_equipment_item(
    item_id: str,
    item_data: EquipmentItemUpdate,
    current_user: TokenData = Depends(get_current_curator_or_admin)
):
    """Update equipment item (Curator or Admin)"""
    item = await db.equipment.find_one({"id": item_id}, {"_id": 0})
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment item not found"
        )
    
    # Update only provided fields
    update_data = item_data.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.equipment.update_one(
            {"id": item_id},
            {"$set": update_data}
        )
    
    # Log the action
    log = LogEntry(
        user_id=current_user.user_id,
        user_name=current_user.email,
        action="UPDATE",
        entity_type="EQUIPMENT",
        entity_id=item_id,
        details=update_data
    )
    await db.logs.insert_one(serialize_for_db(log.model_dump()))
    
    updated_item = await db.equipment.find_one({"id": item_id}, {"_id": 0})
    return EquipmentItem(**deserialize_from_db(updated_item))


@api_router.delete("/equipment/{item_id}")
async def delete_equipment_item(
    item_id: str,
    current_user: TokenData = Depends(get_current_admin_user)
):
    """Delete equipment item (Admin only)"""
    result = await db.equipment.delete_one({"id": item_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment item not found"
        )
    
    # Log the action
    log = LogEntry(
        user_id=current_user.user_id,
        user_name=current_user.email,
        action="DELETE",
        entity_type="EQUIPMENT",
        entity_id=item_id
    )
    await db.logs.insert_one(serialize_for_db(log.model_dump()))
    
    return {"message": "Equipment item deleted successfully"}


# Equipment Image Management
@api_router.post("/equipment/{item_id}/images")
async def upload_equipment_image(
    item_id: str,
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_curator_or_admin)
):
    """Upload an image for an equipment item"""
    # Check if item exists
    item = await db.equipment.find_one({"id": item_id}, {"_id": 0})
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment item not found"
        )
    
    # Validate file type
    allowed_extensions = storage_service.config['local_storage']['allowed_extensions']
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size
    max_size_mb = storage_service.config['local_storage']['max_file_size_mb']
    file_content = await file.read()
    file_size_mb = len(file_content) / (1024 * 1024)
    
    if file_size_mb > max_size_mb:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {max_size_mb}MB"
        )
    
    # Save image
    try:
        image_url = await storage_service.save_image(file_content, file.filename, item_id)
        
        # Update item's images array
        current_images = item.get('images', [])
        current_images.append(image_url)
        
        await db.equipment.update_one(
            {"id": item_id},
            {
                "$set": {
                    "images": current_images,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Log the action
        log = LogEntry(
            user_id=current_user.user_id,
            user_name=current_user.email,
            action="UPLOAD_IMAGE",
            entity_type="EQUIPMENT",
            entity_id=item_id,
            details={"filename": file.filename, "image_url": image_url}
        )
        await db.logs.insert_one(serialize_for_db(log.model_dump()))
        
        return {
            "message": "Image uploaded successfully",
            "image_url": image_url,
            "total_images": len(current_images)
        }
        
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image"
        )


@api_router.delete("/equipment/{item_id}/images")
async def delete_equipment_image(
    item_id: str,
    image_url: str,
    current_user: TokenData = Depends(get_current_curator_or_admin)
):
    """Delete an image from an equipment item"""
    # Check if item exists
    item = await db.equipment.find_one({"id": item_id}, {"_id": 0})
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment item not found"
        )
    
    # Remove image from array
    current_images = item.get('images', [])
    if image_url not in current_images:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found in item"
        )
    
    current_images.remove(image_url)
    
    # Update database
    await db.equipment.update_one(
        {"id": item_id},
        {
            "$set": {
                "images": current_images,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Delete physical file
    await storage_service.delete_image(image_url)
    
    # Log the action
    log = LogEntry(
        user_id=current_user.user_id,
        user_name=current_user.email,
        action="DELETE_IMAGE",
        entity_type="EQUIPMENT",
        entity_id=item_id,
        details={"image_url": image_url}
    )
    await db.logs.insert_one(serialize_for_db(log.model_dump()))
    
    return {
        "message": "Image deleted successfully",
        "remaining_images": len(current_images)
    }


# ============== LOGS ROUTES ==============

@api_router.get("/logs", response_model=List[LogEntry])
async def get_logs(
    limit: int = 100,
    current_user: TokenData = Depends(get_current_admin_user)
):
    """Get activity logs (Admin only)"""
    # Автоматически удалить логи старше 30 дней
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    await db.logs.delete_many({"timestamp": {"$lt": one_month_ago.isoformat()}})
    
    logs = await db.logs.find({}, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    return [LogEntry(**deserialize_from_db(log)) for log in logs]


@api_router.delete("/logs/cleanup")
async def cleanup_old_logs(
    current_user: TokenData = Depends(get_current_admin_user)
):
    """Manually delete logs older than 30 days (Admin only)"""
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    result = await db.logs.delete_many({"timestamp": {"$lt": one_month_ago.isoformat()}})
    
    return {
        "message": "Old logs deleted successfully",
        "deleted_count": result.deleted_count
    }


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


@api_router.post("/load-test-data")
async def load_test_data():
    """Load test data from testprevyou.json file"""
    import json
    
    try:
        # Read test data file
        test_data_path = Path(__file__).parent.parent / 'testprevyou.json'
        
        if not test_data_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test data file not found"
            )
        
        with open(test_data_path, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        # Clear existing data
        await db.users.delete_many({})
        await db.projects.delete_many({})
        await db.inventory.delete_many({})
        await db.equipment.delete_many({})
        await db.logs.delete_many({})
        
        stats = {
            "users": 0,
            "projects": 0,
            "inventory": 0,
            "equipment": 0
        }
        
        # Load users
        for user_data in test_data.get('users', []):
            password = user_data.pop('password', 'password123')
            user = User(
                **user_data,
                password_hash=get_password_hash(password),
                created_at=datetime.now(timezone.utc)
            )
            await db.users.insert_one(serialize_for_db(user.model_dump()))
            stats["users"] += 1
        
        # Load projects
        for project_data in test_data.get('projects', []):
            # Parse project_date if it's a string
            if isinstance(project_data.get('project_date'), str):
                project_data['project_date'] = datetime.fromisoformat(project_data['project_date'].replace('Z', '+00:00'))
            
            project = Project(
                **project_data,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            await db.projects.insert_one(serialize_for_db(project.model_dump()))
            stats["projects"] += 1
        
        # Load inventory
        for item_data in test_data.get('inventory', []):
            item = InventoryItem(
                **item_data,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            await db.inventory.insert_one(serialize_for_db(item.model_dump()))
            stats["inventory"] += 1
        
        # Load equipment
        for item_data in test_data.get('equipment', []):
            item = EquipmentItem(
                **item_data,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            await db.equipment.insert_one(serialize_for_db(item.model_dump()))
            stats["equipment"] += 1
        
        return {
            "message": "Test data loaded successfully",
            "stats": stats,
            "credentials": {
                "admin": {"email": "admin@sls1.com", "password": "admin123"},
                "decorator": {"email": "maria@sls1.com", "password": "maria123"},
                "florist": {"email": "anna@sls1.com", "password": "anna123"},
                "curator": {"email": "elena@sls1.com", "password": "elena123"}
            }
        }
        
    except Exception as e:
        logger.error(f"Error loading test data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load test data: {str(e)}"
        )


# ============== IMAGE UPLOAD ROUTES ==============

@api_router.post("/inventory/{item_id}/images")
async def upload_inventory_image(
    item_id: str,
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_curator_or_admin)
):
    """Upload an image for an inventory item"""
    # Check if item exists
    item = await db.inventory.find_one({"id": item_id}, {"_id": 0})
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    # Validate file type
    allowed_extensions = storage_service.config['local_storage']['allowed_extensions']
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size
    max_size_mb = storage_service.config['local_storage']['max_file_size_mb']
    file_content = await file.read()
    file_size_mb = len(file_content) / (1024 * 1024)
    
    if file_size_mb > max_size_mb:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {max_size_mb}MB"
        )
    
    # Save image
    try:
        image_url = await storage_service.save_image(file_content, file.filename, item_id)
        
        # Update item's images array
        current_images = item.get('images', [])
        current_images.append(image_url)
        
        await db.inventory.update_one(
            {"id": item_id},
            {
                "$set": {
                    "images": current_images,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Log the action
        log = LogEntry(
            user_id=current_user.user_id,
            user_name=current_user.email,
            action="UPLOAD_IMAGE",
            entity_type="INVENTORY",
            entity_id=item_id,
            details={"filename": file.filename, "image_url": image_url}
        )
        await db.logs.insert_one(serialize_for_db(log.model_dump()))
        
        return {
            "message": "Image uploaded successfully",
            "image_url": image_url,
            "total_images": len(current_images)
        }
        
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image"
        )


@api_router.delete("/inventory/{item_id}/images")
async def delete_inventory_image(
    item_id: str,
    image_url: str,
    current_user: TokenData = Depends(get_current_curator_or_admin)
):
    """Delete an image from an inventory item"""
    # Check if item exists
    item = await db.inventory.find_one({"id": item_id}, {"_id": 0})
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    # Remove image from array
    current_images = item.get('images', [])
    if image_url not in current_images:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found in item"
        )
    
    current_images.remove(image_url)
    
    # Update database
    await db.inventory.update_one(
        {"id": item_id},
        {
            "$set": {
                "images": current_images,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Delete physical file
    await storage_service.delete_image(image_url)
    
    # Log the action
    log = LogEntry(
        user_id=current_user.user_id,
        user_name=current_user.email,
        action="DELETE_IMAGE",
        entity_type="INVENTORY",
        entity_id=item_id,
        details={"image_url": image_url}
    )
    await db.logs.insert_one(serialize_for_db(log.model_dump()))
    
    return {
        "message": "Image deleted successfully",
        "remaining_images": len(current_images)
    }


@api_router.get("/uploads/{item_id}/{filename}")
async def get_image(item_id: str, filename: str):
    """Serve uploaded images"""
    file_path = Path(storage_service.upload_dir) / item_id / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    return FileResponse(file_path)


@api_router.get("/telegram/image/{file_id}")
async def get_telegram_image(file_id: str):
    """
    Get Telegram image direct URL
    Used when storage_mode is 'telegram'
    Returns redirect to Telegram CDN URL
    """
    if storage_service.mode != 'telegram':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram storage not enabled"
        )
    
    try:
        file_url = await storage_service.get_telegram_file_url(file_id)
        if not file_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Telegram file not found"
            )
        
        # Redirect to Telegram file URL
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=file_url)
        
    except Exception as e:
        logger.error(f"Error getting Telegram image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get image from Telegram"
        )


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