from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import List, Optional

# --- SCHEMAS DE AUTENTICACIÓN Y TOKEN ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class TokenWithRefresh(Token):
    refresh_token: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

# --- SCHEMAS DE ROLES ---

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleOut(RoleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class AssignRoleRequest(BaseModel):
    user_id: int
    role_id: int

# --- SCHEMAS DE USUARIO ---

class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    roles: List[RoleOut] = []  # Relación con roles
    model_config = ConfigDict(from_attributes=True)

# --- SCHEMAS DE PRODUCTOS ---

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    stock: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel): # Update suele ser opcional
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    stock: Optional[int] = None

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- SCHEMAS DE CARRITO ---

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemOut(CartItemBase):
    id: int
    product: ProductOut
    model_config = ConfigDict(from_attributes=True)

class CartOut(BaseModel):
    id: int
    items: List[CartItemOut]
    total: float
    model_config = ConfigDict(from_attributes=True)