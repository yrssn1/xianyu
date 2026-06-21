"""初始化数据库：创建表并生成默认管理员账号"""
from database import engine, Base, SessionLocal
from models import Product, ProductImage, User  # noqa: F401
from auth import get_password_hash


def init():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "admin").first()
        if not existing:
            admin = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                nickname="管理员",
                is_superuser=True,
            )
            db.add(admin)
            db.commit()
            print("✓ 默认管理员账号已创建: admin / admin123")
        else:
            print("✓ 管理员账号已存在，跳过创建")
    finally:
        db.close()


if __name__ == "__main__":
    init()
