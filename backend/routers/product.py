import os
import io
import uuid
import shutil
import zipfile
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from models.product import Product, ProductImage
from models.user import User
from schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from auth import get_current_user
from config import UPLOAD_DIR

router = APIRouter(prefix="/api/products", tags=["商品管理"], dependencies=[Depends(get_current_user)])

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}


def sanitize_folder_name(name: str) -> str:
    """将商品标题转换为安全的文件夹名。"""
    if not name:
        return ""
    invalid = '<>:"/\\|?*\n\r\t'
    cleaned = "".join("_" if c in invalid else c for c in name).strip().strip(".")
    return cleaned[:100]


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


@router.get("/export")
def export_products(db: Session = Depends(get_db)):
    """一键导出：将全部商品打包为 zip，每个商品一个以标题命名的文件夹，内含其图片。"""
    products = db.query(Product).order_by(Product.created_at.desc()).all()

    buffer = io.BytesIO()
    used_names: dict[str, int] = {}
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for product in products:
            base = sanitize_folder_name(product.title) or f"product_{product.id}"
            count = used_names.get(base, 0)
            folder = base if count == 0 else f"{base}_{count}"
            used_names[base] = count + 1

            images = sorted(product.images, key=lambda i: i.sort_order)
            if not images:
                zf.writestr(f"{folder}/", "")
                continue

            for idx, image in enumerate(images):
                filename = os.path.basename(image.image_url)
                filepath = os.path.join(UPLOAD_DIR, filename)
                if not os.path.exists(filepath):
                    continue
                ext = os.path.splitext(filename)[1] or ".jpg"
                zf.write(filepath, f"{folder}/{idx + 1}{ext}")

    buffer.seek(0)
    headers = {"Content-Disposition": "attachment; filename=products_export.zip"}
    return StreamingResponse(buffer, media_type="application/zip", headers=headers)


@router.post("/import")
def import_products(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """一键导入：上传 zip 压缩包，每个顶层文件夹生成一个商品（标题=文件夹名），内部图片作为商品图片。"""
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="请上传 .zip 压缩包")

    try:
        content = file.file.read()
        archive = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="无效的压缩包文件")

    folders: dict[str, list[zipfile.ZipInfo]] = {}
    for info in archive.infolist():
        if info.is_dir():
            continue
        parts = info.filename.replace("\\", "/").split("/")
        if any(p.startswith("__MACOSX") or p.startswith(".") for p in parts):
            continue
        if len(parts) < 2:
            continue
        ext = os.path.splitext(parts[-1])[1].lower()
        if ext not in IMAGE_EXTENSIONS:
            continue
        folders.setdefault(parts[0], []).append(info)

    if not folders:
        raise HTTPException(status_code=400, detail="压缩包中没有找到符合结构的图片文件夹")

    created = 0
    total_images = 0
    for folder, infos in folders.items():
        title = (folder.strip() or "未命名素材")[:200]
        product = Product(title=title, price=0, description=title, status="draft")
        db.add(product)
        db.flush()

        for idx, info in enumerate(infos[:9]):
            ext = os.path.splitext(info.filename)[1].lower()
            new_name = f"{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(UPLOAD_DIR, new_name)
            with open(filepath, "wb") as out:
                out.write(archive.read(info))
            db.add(ProductImage(
                product_id=product.id,
                image_url=f"/uploads/{new_name}",
                sort_order=idx,
            ))
            total_images += 1
        created += 1

    db.commit()
    return {
        "message": f"成功导入 {created} 个商品，共 {total_images} 张图片",
        "created": created,
        "images": total_images,
    }


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
