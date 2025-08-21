from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    email: str
    name: str



class LoginRequest(BaseModel):
    email: str
    password: str
    
class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

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


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    stock: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemOut(CartItemBase):
    id: int
    product: ProductOut
    model_config = ConfigDict(from_attributes=True)

class CartOut(BaseModel):
    id: int
    items: List[CartItemOut]
    total: float
    model_config = ConfigDict(from_attributes=True)



class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    stock: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)









class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemOut(CartItemBase):
    id: int
    product: ProductOut

    class Config:
        orm_mode = True

class CartOut(BaseModel):
    id: int
    items: List[CartItemOut]
    total: float

    class Config:
        orm_mode = True



class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class TokenWithRefresh(Token):
    refresh_token: str
    
class RefreshTokenCreate(BaseModel):
    refresh_token: str


class RefreshRequest(BaseModel):
    refresh_token: str
    
class RefreshTokenOut(BaseModel):
    id: int
    token: str
    revoked: bool
    created_at: datetime
    expires_at: datetime
    model_config = ConfigDict(from_attributes=True)