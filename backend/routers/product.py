import os
import uuid
import shutil
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from database import get_db
from models.product import Product, ProductImage
from models.user import User
from schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from auth import get_current_user
from config import UPLOAD_DIR

router = APIRouter(prefix="/api/products", tags=["商品管理"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=ProductListResponse)
def get_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if keyword:
        query = query.filter(Product.title.contains(keyword))
    if category:
        query = query.filter(Product.category == category)
    if status:
        query = query.filter(Product.status == status)

    total = query.count()
    items = query.order_by(Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return ProductListResponse(total=total, items=items)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


@router.post("", response_model=ProductResponse)
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    product = Product(**product_data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_data: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    db.delete(product)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{product_id}/images")
def upload_images(
    product_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    existing_count = db.query(ProductImage).filter(ProductImage.product_id == product_id).count()
    if existing_count + len(files) > 9:
        raise HTTPException(status_code=400, detail="商品图片最多9张")

    uploaded = []
    for i, file in enumerate(files):
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        image = ProductImage(
            product_id=product_id,
            image_url=f"/uploads/{filename}",
            sort_order=existing_count + i,
        )
        db.add(image)
        uploaded.append(image)

    db.commit()
    return {"message": f"成功上传{len(uploaded)}张图片"}


@router.delete("/{product_id}/images/{image_id}")
def delete_image(product_id: int, image_id: int, db: Session = Depends(get_db)):
    image = db.query(ProductImage).filter(
        ProductImage.id == image_id, ProductImage.product_id == product_id
    ).first()
    if not image:
        raise HTTPException(status_code=404, detail="图片不存在")

    filepath = os.path.join(UPLOAD_DIR, os.path.basename(image.image_url))
    if os.path.exists(filepath):
        os.remove(filepath)

    db.delete(image)
    db.commit()
    return {"message": "删除成功"}
