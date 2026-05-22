# 酒店客房销售管理系统

Vue 3 + Element Plus 前端 + FastAPI 后端 + MySQL

## 角色说明

| 角色 | 权限 |
|------|------|
| 员工 | 录入/修改/删除/查询自己的订单（超过1个月的记录不可修改删除） |
| 财务 | 查询所有订单、导出Excel |
| 管理员 | 用户管理、所有订单的增删改查和导出、查看操作日志 |

## 启动方式

### 后端
```bash
cd backend
# 首次需要安装依赖
pip install -r requirements.txt
# 确保 .env 文件配置好数据库连接
# 创建数据库表
python3 -c "from app.models import Base; from app.database import engine; Base.metadata.create_all(engine)"
# 创建管理员
python3 create_admin.py --db-url "mysql+pymysql://root:password@host:3306/hotel_manager?charset=utf8mb4"
# 启动
python3 ../start_server.py
```

或者在项目根目录：
```bash
python3 start_server.py
```

后端运行在 `http://localhost:8000`，API文档在 `http://localhost:8000/docs`

### 前端
```bash
cd frontend
npm install
npm run dev
```

前端运行在 `http://localhost:5173`，API请求通过 Vite 代理到后端。

### 生产部署
```bash
cd frontend
npm run build  # 输出到 ../backend/static/
cd ../backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 默认账号
- 管理员: `admin / admin123`

## 项目结构
```
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── routers/      # API路由
│   │   ├── services/     # 业务逻辑
│   │   ├── utils/        # 工具函数
│   │   ├── models.py     # 数据库模型
│   │   ├── schemas.py    # Pydantic schema
│   │   └── ...
│   ├── static/           # 前端构建产物
│   └── schema.sql        # 数据库DDL
├── frontend/             # Vue 3 前端
│   ── src/
│       ├── views/        # 页面组件
│       ├── components/   # 通用组件
│       ├── store/        # Pinia状态管理
│       └── api/          # API封装
└── start_server.py       # 后端启动脚本
```
