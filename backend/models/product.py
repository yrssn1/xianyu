from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="商品标题")
    price = Column(Float, nullable=False, comment="售价")
    original_price = Column(Float, nullable=True, comment="原价(划线价)")
    category = Column(String(50), nullable=True, comment="商品分类")
    condition = Column(String(20), default="全新", comment="成色")
    brand = Column(String(100), nullable=True, comment="品牌")
    shipping_method = Column(String(20), default="快递发货", comment="发货方式")
    shipping_fee = Column(Float, default=0, comment="邮费，0为包邮")
    location = Column(String(200), nullable=True, comment="宝贝所在地")
    description = Column(Text, nullable=False, comment="商品描述")
    notes = Column(Text, nullable=True, comment="备注(内部使用)")
    status = Column(String(20), default="draft", comment="状态: draft/published/offline")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String(500), nullable=False, comment="图片路径")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="images")
