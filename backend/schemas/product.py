from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProductImageResponse(BaseModel):
    id: int
    image_url: str
    sort_order: int

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="商品标题")
    price: float = Field(..., ge=0, description="售价")
    original_price: Optional[float] = Field(None, ge=0, description="原价")
    category: Optional[str] = Field(None, max_length=50, description="商品分类")
    condition: str = Field(default="全新", description="成色")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    shipping_method: str = Field(default="快递发货", description="发货方式")
    shipping_fee: float = Field(default=0, ge=0, description="邮费")
    location: Optional[str] = Field(None, max_length=200, description="宝贝所在地")
    description: str = Field(..., min_length=1, description="商品描述")
    notes: Optional[str] = Field(None, description="备注")


class ProductUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    price: Optional[float] = Field(None, ge=0)
    original_price: Optional[float] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=50)
    condition: Optional[str] = None
    brand: Optional[str] = Field(None, max_length=100)
    shipping_method: Optional[str] = None
    shipping_fee: Optional[float] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    notes: Optional[str] = None
    status: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    title: str
    price: float
    original_price: Optional[float]
    category: Optional[str]
    condition: str
    brand: Optional[str]
    shipping_method: str
    shipping_fee: float
    location: Optional[str]
    description: str
    notes: Optional[str]
    status: str
    images: List[ProductImageResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    total: int
    items: List[ProductResponse]
