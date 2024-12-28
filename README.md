# ELT Data Engineering Project

A modern data stack solution for end-to-end data processing, integrating PostgreSQL, Airflow, and DBT.

## Architecture

### Core Components

#### 1. Data Storage Layer
- **Source Database** (`source_postgres`)
  - PostgreSQL instance
  - Port: 5433
  - Stores raw business data
  
- **Target Database** (`destination_postgres`)
  - PostgreSQL instance
  - Port: 5434
  - Stores transformed analytical data

#### 2. Orchestration Layer
- **Airflow**
  - Web UI: Port 8080
  - Scheduler service
  - Task orchestration and monitoring
  - Supports conditional branching and error retries

#### 3. Data Processing Layer
- **ELT Script**
  - Based on `pg_dump` and `psql`
  - Supports incremental and full data migration
  - Automated data extraction and loading

- **DBT Transformations**
  - Modular data transformations
  - Built-in testing and documentation
  - Version control and dependency management

### Data Flow

Source DB (OLTP)
↓ [ELT Script]
Target DB (Stage)
↓ [DBT Models]
Analytics Views (Mart)

## Features

### 1. Data Pipeline
- Automated data extraction and loading
- Modular transformation using DBT
- Real-time data processing via API
- Data quality testing and validation

### 2. Workflow Management
- Conditional task execution
- Automated error handling
- Visual pipeline monitoring
- REST API integration

### 3. Containerized Deployment
- Docker-based services
- Network isolation
- Environment consistency
- Easy scaling and deployment

## Project Structure

```
📦 elt
 ┣ 📂 airflow
 ┃ ┗ 📂 dags         # Airflow DAG 定义文件
 ┣ 📂 api            # REST API 服务
 ┣ 📂 custom_postgres # DBT 项目文件
 ┃ ┣ 📂 models       # 数据模型定义
 ┃ ┣ 📂 macros       # 可重用转换逻辑
 ┃ ┗ 📂 tests        # 数据质量测试
 ┣ 📂 elt_script     # 数据迁移脚本
 ┣ 📂 source_db_init # 源数据库初始化
 ┗ 📜 docker-compose.yaml # 容器编排配置
```
## Quick Start

### Prerequisites
- Docker Engine 24.0+
- Docker Compose 2.0+
- Available ports: 5433, 5434, 8080, 5001
- Disk space: 2GB minimum

### Installation

1. Clone the repository

2. Start services
```
bash
docker-compose up -d
```

3. Access services
- Airflow UI: http://localhost:8080
  - Username: airflow
  - Password: admin123
- API Service: http://localhost:5001

### Development Guide

#### Adding New Models
1. Create model file in `custom_postgres/models/`
2. Update `schema.yml` with test rules
3. Define sources in `sources.yml`
4. Run `dbt run` to validate changes

#### Modifying Data Flow
1. Update `elt_script/elt_script.py`
2. Modify `airflow/dags/elt_dag.py`
3. Restart relevant services

## Maintenance

### Routine Tasks
- Monitor Airflow task status
- Check data quality test results
- Clean historical data
- Update model documentation

### Troubleshooting
- Check container logs
- Verify database connections
- Validate configurations
- Retry failed tasks
