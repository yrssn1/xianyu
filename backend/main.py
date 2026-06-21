from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from models import Product, ProductImage, User  # noqa: F401
from routers import product
from routers import auth
from config import UPLOAD_DIR

Base.metadata.create_all(bind=engine)

# 启动时自动创建默认管理员
from init_db import init
init()

app = FastAPI(title="闲鱼自动化系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(auth.router)
app.include_router(product.router)


@app.get("/")
def root():
    return {"message": "闲鱼自动化系统 API"}
