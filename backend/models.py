from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid


# Enums
class UserRole(str, Enum):
    ADMIN = "Администратор"
    LEAD_DECORATOR = "Ведущий декоратор"
    FLORIST = "Флорист"
    CURATOR = "Куратор студии"


class ProjectStatus(str, Enum):
    CREATED = "Создан"
    PENDING_APPROVAL = "На согласовании"
    APPROVED = "Согласован"
    PROJECT_BUILD = "Сбор проекта"
    ASSEMBLY = "Монтаж"
    DISASSEMBLY = "Демонтаж"
    BREAKDOWN = "Разбор"


# User Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    password_hash: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: UserRole


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


# Project Models
class Project(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    lead_decorator: str
    project_date: datetime
    full_details: Optional[Dict[str, Any]] = None
    status: ProjectStatus = ProjectStatus.CREATED
    preliminary_list: Optional[Dict[str, Any]] = None
    final_list: Optional[Dict[str, Any]] = None
    dismantling_list: Optional[Dict[str, Any]] = None
    curator_agreement: bool = False
    decorator_agreement: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None


class ProjectCreate(BaseModel):
    title: str
    lead_decorator: str
    project_date: datetime
    full_details: Optional[Dict[str, Any]] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    lead_decorator: Optional[str] = None
    project_date: Optional[datetime] = None
    full_details: Optional[Dict[str, Any]] = None
    status: Optional[ProjectStatus] = None
    preliminary_list: Optional[Dict[str, Any]] = None
    final_list: Optional[Dict[str, Any]] = None
    dismantling_list: Optional[Dict[str, Any]] = None
    curator_agreement: Optional[bool] = None
    decorator_agreement: Optional[bool] = None


# Inventory Models
class InventoryItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str
    name: str
    total_quantity: int
    visual_marker: Optional[str] = None
    description: Optional[str] = None
    images: List[str] = Field(default_factory=list)  # URLs or paths to images
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InventoryItemCreate(BaseModel):
    category: str
    name: str
    total_quantity: int
    visual_marker: Optional[str] = None
    description: Optional[str] = None


class InventoryItemUpdate(BaseModel):
    category: Optional[str] = None
    name: Optional[str] = None
    total_quantity: Optional[int] = None
    visual_marker: Optional[str] = None
    description: Optional[str] = None
    images: Optional[List[str]] = None


# Equipment Models (separate from Inventory)
class EquipmentItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str
    name: str
    total_quantity: int
    visual_marker: Optional[str] = None
    description: Optional[str] = None
    images: List[str] = Field(default_factory=list)  # URLs or paths to images
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EquipmentItemCreate(BaseModel):
    category: str
    name: str
    total_quantity: int
    visual_marker: Optional[str] = None
    description: Optional[str] = None


class EquipmentItemUpdate(BaseModel):
    category: Optional[str] = None
    name: Optional[str] = None
    total_quantity: Optional[int] = None
    visual_marker: Optional[str] = None
    description: Optional[str] = None
    images: Optional[List[str]] = None


# Log Models
class LogEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_name: str
    action: str
    entity_type: str
    entity_id: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LogEntryCreate(BaseModel):
    user_id: str
    user_name: str
    action: str
    entity_type: str
    entity_id: str
    details: Optional[Dict[str, Any]] = None


# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str
    email: str
    role: UserRole
