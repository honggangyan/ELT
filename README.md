# ELT 数据工程项目

这是一个基于 Docker 的数据工程项目，集成了 PostgreSQL、Airflow 和 DBT，用于实现端到端的数据处理流程。

## 项目架构

### 核心组件

1. **数据库服务**
   - `source_postgres`: 源数据库 (端口 5433)
   - `destination_postgres`: 目标数据库 (端口 5434)
   - `postgres`: Airflow 元数据库

2. **Airflow 服务**
   - `webserver`: Airflow Web UI (端口 8080)
   - `scheduler`: Airflow 调度器
   - `init-airflow`: Airflow 初始化服务

3. **数据处理服务**
   - ELT 脚本：用于数据提取和加载
   - DBT：用于数据转换

## 功能特点

1. **数据迁移与转换**
   - 支持从源数据库到目标数据库的数据迁移
   - 使用 DBT 进行数据建模和转换
   - 通过 Airflow DAGs 实现工作流程自动化

2. **工作流编排**
   - 使用 Airflow 管理和调度数据管道
   - 支持任务依赖关系管理
   - 提供可视化的任务监控界面

3. **容器化部署**
   - 所有组件都运行在 Docker 容器中
   - 使用 Docker Compose 进行服务编排
   - 确保环境一致性和可移植性

## 快速开始

### 前置要求
- Docker
- Docker Compose
- 可用端口：5433, 5434, 8080

### 安装步骤

1. **启动服务**
```

2. **访问 Airflow**
- URL: http://localhost:8080
- 用户名: airflow
- 密码: admin123

### 目录结构
elt/
├── airflow/
│ └── dags/ # Airflow DAG 定义
├── custom_postgres/ # DBT 项目文件
├── elt_script/ # 数据处理脚本
├── source_db_init/ # 源数据库初始化脚本
└── docker-compose.yaml