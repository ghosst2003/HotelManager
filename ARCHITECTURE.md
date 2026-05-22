# 酒店客房销售管理系统 - 系统架构文档

## 1. 项目概述

酒店客房销售管理系统，用于管理酒店订单的录入、查询、修改、导出以及用户权限控制。

### 技术栈总览

| 层级 | 技术选型 |
|------|---------|
| 后端框架 | FastAPI 0.115.6 + Uvicorn |
| 前端框架 | Vue 3 + Vite 6 |
| UI 组件库 | Element Plus 2.9.1 |
| 状态管理 | Pinia |
| 路由 | Vue Router 4 |
| HTTP 客户端 | Axios |
| ORM | SQLAlchemy 2.0 |
| 数据库 | MySQL (PyMySQL 驱动) |
| 认证 | JWT (python-jose) + bcrypt |
| Excel 导出 | openpyxl |
| 配置管理 | pydantic-settings + .env |

## 2. 项目结构

```
HotelManager/
├── .gitignore              # Git 忽略规则
├── README.md               # 项目说明
├── start_server.py         # 后端启动脚本 (uvicorn 包装)
├── backend/                # 后端服务
│   ├── .env                # 环境变量 (DATABASE_URL, SECRET_KEY)
│   ├── .env.example        # 环境变量模板
│   ├── requirements.txt    # Python 依赖
│   ├── schema.sql          # 数据库建表 DDL
│   ├── create_admin.py     # 初始管理员创建脚本
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI 应用入口，挂载路由/CORS/静态文件
│   │   ├── config.py       # pydantic-settings 配置加载
│   │   ├── database.py     # SQLAlchemy 引擎/会话管理
│   │   ├── models.py       # 数据库 ORM 模型
│   │   ├── schemas.py      # Pydantic 请求/响应 Schema
│   │   ├── auth.py         # 密码加密/JWT 生成与解析
│   │   ├── dependencies.py # 依赖注入: get_current_user, require_role
│   │   ├── routers/
│   │   │   ├── auth.py     # POST /api/auth/login - 用户登录
│   │   │   ├── users.py    # CRUD /api/users - 用户管理 (管理员)
│   │   │   ├── orders.py   # CRUD /api/orders - 订单管理 + Excel 导出
│   │   │   └── logs.py     # GET /api/logs - 操作日志查询
│   │   ├── services/
│   │   │   └── order_service.py  # 订单业务逻辑 (利润计算/权限校验)
│   │   └── utils/
│   │       ├── export.py   # Excel 导出实现
│   │       └── permissions.py    # 权限检查辅助函数
│   └── static/             # 前端构建产物 (生产模式挂载)
├── frontend/               # 前端应用
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js      # Vite 配置 (代理/构建输出)
│   └── src/
│       ├── main.js         # Vue 应用入口
│       ├── App.vue         # 根组件
│       ├── router/
│       │   └── index.js    # 路由配置 + 登录守卫
│       ├── store/
│       │   └── auth.js     # Pinia 认证状态
│       ├── api/
│       │   └── index.js    # Axios 封装 + API 调用
│       ├── components/
│       │   └── OrderItemTable.vue  # 订单明细表格组件
│       └── views/
│           ├── Layout.vue      # 主布局 (侧边栏+内容区)
│           ├── Login.vue       # 登录页
│           ├── OrderList.vue   # 订单列表页 (搜索/分页/删除/导出)
│           ├── OrderForm.vue   # 订单新增/编辑表单
│           ├── UserManagement.vue  # 用户管理页 (仅管理员)
│           └── OperationLog.vue  # 操作日志页
```

## 3. 数据库设计

### 3.1 数据表关系

```
users (1) ────< (N) orders (created_by)
users (1) ────< (N) orders (deleted_by)
users (1) ────< (N) operation_logs
orders (1) ────< (N) order_items
```

### 3.2 表结构

#### users 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT UNSIGNED PK | 自增主键 |
| username | VARCHAR(50) UNIQUE | 登录用户名 |
| password_hash | VARCHAR(255) | bcrypt 哈希 |
| role | ENUM('employee','finance','admin') | 角色 |
| display_name | VARCHAR(100) | 显示名称 |
| is_active | TINYINT(1) | 是否启用 |
| created_at / updated_at | DATETIME | 时间戳 |

#### orders 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT UNSIGNED PK | 自增主键 |
| order_platform | VARCHAR(50) | 订单平台 |
| order_number | VARCHAR(100) | 订单号 |
| room_name | VARCHAR(200) | 房间名称 |
| guest_name | VARCHAR(100) | 客人姓名 |
| salesperson | VARCHAR(100) | 销售人员 |
| hotel_name | VARCHAR(200) | 酒店名称 |
| guest_count | INT | 入住人数 |
| booking_date | DATE | 预订日期 |
| confirmation_number | VARCHAR(100) | 确认号 |
| order_status | ENUM('未处理','已确认','已入住','已取消') | 订单状态 |
| other_remarks | TEXT | 备注 |
| created_by | INT UNSIGNED FK→users | 创建人 |
| is_deleted | TINYINT(1) | 软删除标记 |
| deleted_at / deleted_by | DATETIME / INT UNSIGNED FK→users | 删除信息 |
| created_at / updated_at | DATETIME | 时间戳 |

#### order_items 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT UNSIGNED PK | 自增主键 |
| order_id | INT UNSIGNED FK→orders | 所属订单 |
| date | DATE | 入住日期 |
| room_count | INT | 房间数 |
| cost_price | DECIMAL(10,2) | 成本价 |
| sale_price | DECIMAL(10,2) | 销售价 |
| gross_profit | DECIMAL(10,2) | 毛利 (自动计算) |
| profit_margin | DECIMAL(5,2) | 利润率 (自动计算) |
| salesperson | VARCHAR(100) | 销售人员 |
| confirmation_number | VARCHAR(100) | 确认号 |
| remarks | TEXT | 备注 |
| created_at / updated_at | DATETIME | 时间戳 |

#### operation_logs 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT UNSIGNED PK | 自增主键 |
| user_id | INT UNSIGNED FK→users | 操作人 |
| action | ENUM(create,update,delete,login,export, ...) | 操作类型 |
| entity_type | VARCHAR(50) | 实体类型 |
| entity_id | INT UNSIGNED | 实体 ID |
| details | JSON | 操作详情 |
| ip_address | VARCHAR(45) | 操作 IP |
| created_at | DATETIME | 操作时间 |

## 4. 系统架构

### 4.1 后端架构

```
HTTP Request
    │
    ▼
┌─────────────────────────┐
│        FastAPI App       │  (main.py)
│  CORS Middleware         │
│  Static Files Mount      │
└────────┬────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌─────────┐
│ auth   │ │ users  │ │ orders   │ │  logs   │  ← routers/
│ .router│ │ .router│ │ .router  │ │ .router │
└────┬───┘ └───┬────┘ └────┬─────┘ └────┬────┘
     │         │           │            │
     ▼         ▼           ▼            ▼
┌──────────────────────────────────────────────┐
│  dependencies.py                              │
│  get_current_user() / require_role()          │
└──────────────────────┬───────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌──────────────────┐      ┌──────────────────────┐
│  models.py       │      │  services/           │
│  SQLAlchemy ORM  │      │  order_service.py    │
└────────┬─────────┘      └──────────┬───────────┘
         │                           │
         ▼                           ▼
┌─────────────────────────┐   ┌─────────────────────┐
│    database.py           │   │  utils/             │
│    SessionLocal / Base   │   │  export.py / perms  │
└────────┬────────────────┘   └─────────────────────┘
         │
         ▼
┌─────────────────────────┐
│      MySQL Database      │
└─────────────────────────┘
```

### 4.2 认证流程

1. 用户 POST `/api/auth/login` (username + password)
2. 后端验证用户名密码，生成 JWT token (HS256, 480分钟过期)
3. 前端存储 token，后续请求在 `Authorization: Bearer <token>` 中携带
4. 后端通过 `get_current_user` 依赖注入解析 token 获取当前用户
5. 路由通过 `require_role("admin")` 等装饰器进行角色鉴权

### 4.3 前端架构

```
┌───────────────────────────────────┐
│           Vue App                  │
│  ┌─────────┐  ┌─────────────────┐ │
│  │ Router   │  │ Pinia Store     │ │
│  │ + Guard  │  │ (auth store)    │ │
│  └────┬────┘  └────────┬────────┘ │
│       │                 │          │
│       ▼                 ▼          │
│  ┌─────────────────────────────┐  │
│  │         Views               │  │
│  │  Login / Layout / Orders    │  │
│  │  Users / Logs               │  │
│  └─────────────┬───────────────┘  │
│                │                   │
│                ▼                   │
│  ┌─────────────────────────────┐  │
│  │  API Layer (Axios + token)  │  │
│  └─────────────┬───────────────┘  │
└────────────────┼──────────────────┘
                 │
                 ▼ (Vite proxy → localhost:8000)
         FastAPI Backend
```

## 5. 权限设计

### 5.1 角色权限矩阵

| 功能 | 员工 (employee) | 财务 (finance) | 管理员 (admin) |
|------|:-:|:-:|:-:|
| 创建订单 | ✓ | ✗ | ✓ |
| 查看自己订单 | ✓ | ✗ | ✓ |
| 修改自己订单 (>1个月不可) | ✓ | ✗ | ✓ |
| 删除自己订单 (>1个月不可) | ✓ | ✗ | ✓ |
| 查看所有订单 | ✗ | ✓ | ✓ |
| 导出订单 Excel | ✗ | ✓ | ✓ |
| 用户管理 | ✗ | ✗ | ✓ |
| 查看操作日志 | ✗ | ✗ | ✓ |

### 5.2 权限实现

- 后端: `require_role()` 依赖注入工厂函数，在路由级别拦截
- `permissions.py`: 提供 `check_order_permission()` 用于行级权限校验
- 员工只能操作 `created_by` 为自己的订单
- 订单修改/删除限制: 创建时间超过 1 个月则禁止操作

## 6. API 端点

### 认证
| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | /api/auth/login | 用户登录 | 无 |

### 用户
| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | /api/users | 用户列表 | admin |
| POST | /api/users | 创建用户 | admin |
| PUT | /api/users/{id} | 更新用户 | admin |
| DELETE | /api/users/{id} | 删除用户 | admin |
| POST | /api/users/{id}/toggle-active | 启用/禁用 | admin |

### 订单
| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | /api/orders | 订单列表 (分页/搜索) | 全部角色 |
| POST | /api/orders | 创建订单 | employee, admin |
| PUT | /api/orders/{id} | 更新订单 | employee, admin |
| DELETE | /api/orders/{id} | 软删除订单 | employee, admin |
| POST | /api/orders/export | 导出 Excel | finance, admin |

### 日志
| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | /api/logs | 操作日志列表 (分页) | admin |

### 健康检查
| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | /api/health | 健康检查 | 无 |

## 7. 部署方式

### 开发模式
- 后端: `python start_server.py` → `http://localhost:8000`
- 前端: `cd frontend && npm run dev` → `http://localhost:5173`
- Vite 代理 `/api` 请求到后端

### 生产模式
- `cd frontend && npm run build` → 输出到 `../backend/static/`
- `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- FastAPI 直接挂载 static 目录，单进程服务前后端
