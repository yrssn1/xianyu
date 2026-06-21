# 闲鱼自动化系统

## 技术栈

- **前端**: Vue 3 + Ant Design Vue 4 + Vite + Pinia
- **后端**: FastAPI + SQLAlchemy
- **数据库**: MySQL

## 项目结构

```
xianyu-auto/
├── frontend/          # Vue 3 前端
│   ├── src/
│   │   ├── api/       # API 请求
│   │   ├── router/    # 路由
│   │   ├── views/     # 页面组件
│   │   └── main.js
│   └── package.json
├── backend/           # FastAPI 后端
│   ├── models/        # 数据库模型
│   ├── schemas/       # Pydantic 验证
│   ├── routers/       # 路由处理
│   ├── main.py
│   └── requirements.txt
└── README.md
```

## 快速开始

### 1. 数据库准备

```sql
CREATE DATABASE xianyu_auto DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 后端启动

```bash
cd backend
pip install -r requirements.txt
# 修改 .env 中的数据库连接信息
uvicorn main:app --reload --port 8000
```

### 3. 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 功能模块

- [x] 商品管理（素材管理）
- [ ] 发布管理
- [ ] 账号管理
- [ ] 系统设置
