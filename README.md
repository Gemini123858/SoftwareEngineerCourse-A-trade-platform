# SoftwareEngineerCourse-A-trade-platform

A course project - a school trade platform for buying and selling second-hand items within a campus community.

## 项目简介 | Project Overview

这是一个基于 PyQt5 开发的校园二手交易平台桌面应用程序。该系统允许用户注册、登录、发布商品、搜索商品、表达购买意向以及管理员管理功能。数据持久化使用 JSON 文件存储。

This is a desktop application for a school trade platform built with PyQt5. The system allows users to register, login, publish items, search for items, express buying interest, and includes admin management features. Data persistence is implemented using JSON files.

## 主要功能 | Features

### 用户功能 | User Features
- **用户注册与登录** | User Registration & Login
  - 邮箱注册，密码加密存储（模拟）
  - 会话管理
  
- **商品管理** | Item Management
  - 发布商品（标题、描述、价格、图片）
  - 浏览所有商品
  - 搜索商品（支持标题和描述关键词搜索）
  
- **交易互动** | Trade Interaction
  - 对感兴趣的商品表达购买意向
  - 获取卖家联系方式
  - 查看互动记录

### 管理员功能 | Admin Features
- **用户管理** | User Management
  - 查看所有用户
  - 删除用户（不能删除自己）
  
- **商品管理** | Item Management
  - 查看所有商品
  - 删除任意商品

## 技术栈 | Technology Stack

- **前端框架** | Frontend: PyQt5 (Qt Designer UI files)
- **后端语言** | Backend: Python 3.12+
- **数据存储** | Data Storage: JSON files
- **架构模式** | Architecture: MVC (Model-View-Controller)

### 依赖库 | Dependencies
```
PyQt5==5.15.9
pyqt5-plugins==5.15.9.2.3
PyQt5-Qt5==5.15.2
pyqt5-tools==5.15.9.3.3
PyQt5_sip==12.17.1
python-dotenv==1.2.1
click==8.3.0
qt5-applications==5.15.2.2.3
qt5-tools==5.15.2.1.3
```

## 项目结构 | Project Structure

```
SoftwareEngineerCourse-A-trade-platform/
├── main.py                    # GUI 应用主入口 | Main GUI application entry
├── test_main.py               # 后端功能演示 | Backend functionality demo
├── requirement.txt            # 依赖列表 | Dependencies list
├── data/                      # 数据存储目录 | Data storage directory
│   ├── users.json            # 用户数据 | User data
│   ├── items.json            # 商品数据 | Item data
│   └── interactions.json     # 交互记录 | Interaction records
├── src/                       # 源代码目录 | Source code directory
│   ├── models.py             # 数据模型 | Data models (User, Item, InterestInteraction)
│   ├── data_manager.py       # 数据管理器 | Data manager for JSON I/O
│   ├── controllers/          # 控制器 | Controllers
│   │   ├── login_controller.py
│   │   ├── register_controller.py
│   │   ├── main_controller.py
│   │   ├── publish_item_controller.py
│   │   └── admin_controller.py
│   ├── services/             # 业务逻辑服务 | Business logic services
│   │   ├── auth_service.py   # 认证服务 | Authentication service
│   │   ├── item_service.py   # 商品服务 | Item service
│   │   └── admin_service.py  # 管理员服务 | Admin service
│   ├── ui_*.py               # UI 类文件 | UI class files (generated from .ui)
└── ui/                        # Qt Designer UI 文件 | Qt Designer UI files
    ├── login_window.ui
    ├── register_dialog.ui
    ├── main_window.ui
    ├── publish_item_dialog.ui
    └── admin_dialog.ui
```

## 安装与运行 | Installation & Usage

### 1. 克隆仓库 | Clone Repository
```bash
git clone https://github.com/Gemini123858/SoftwareEngineerCourse-A-trade-platform.git
cd SoftwareEngineerCourse-A-trade-platform
```

### 2. 安装依赖 | Install Dependencies
```bash
pip install -r requirement.txt
```

### 3. 运行 GUI 应用 | Run GUI Application
```bash
python main.py
```

**注意** | **Note**: 在 Linux 系统上，可能需要设置环境变量：
```bash
export QT_QPA_PLATFORM_PLUGIN_PATH=/path/to/your/venv/lib/python3.x/site-packages/PyQt5/Qt5/plugins/platforms
```

### 4. 运行后端演示 | Run Backend Demo
```bash
python test_main.py
```

## 默认管理员账户 | Default Admin Account

首次运行时，系统会自动创建管理员账户：
- **邮箱** | **Email**: `admin@app.com`
- **密码** | **Password**: `admin123`

## 开发说明 | Development Notes

### 数据模型 | Data Models

1. **User** - 用户模型
   - id: 用户ID
   - email: 邮箱（唯一）
   - password_hash: 密码哈希
   - nickname: 昵称
   - contact_info: 联系方式
   - role: 角色（USER/ADMIN）
   - created_at: 创建时间

2. **Item** - 商品模型
   - id: 商品ID
   - seller_id: 卖家ID
   - title: 标题
   - description: 描述
   - price: 价格
   - status: 状态（AVAILABLE/SOLD）
   - image_paths: 图片路径列表
   - created_at: 创建时间

3. **InterestInteraction** - 交互记录模型
   - id: 记录ID
   - item_id: 商品ID
   - buyer_id: 买家ID
   - interaction_time: 交互时间

### 架构设计 | Architecture Design

本项目采用 MVC 架构模式：
- **Models** (`models.py`): 定义数据结构
- **Views** (`ui/*.ui`, `ui_*.py`): PyQt5 界面
- **Controllers** (`controllers/*.py`): 处理用户交互和业务逻辑调用
- **Services** (`services/*.py`): 核心业务逻辑

## 测试 | Testing

运行 `test_main.py` 可以测试后端功能：
- 用户注册和登录
- 商品发布和搜索
- 购买意向表达
- 管理员操作

## 注意事项 | Notes

1. 本项目仅用于教学目的，密码存储采用简单模拟方式
2. 生产环境中应使用真正的密码哈希算法（如 bcrypt 或 werkzeug.security）
3. 数据存储使用 JSON 文件，不适合大规模应用
4. 生产环境建议使用数据库（如 PostgreSQL、MySQL）

## 许可证 | License

本项目为课程作业项目。

## 作者 | Author

Course Project - Software Engineering Course
