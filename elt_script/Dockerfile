# ELT 服务 Dockerfile
# ==================
#
# 基础环境：
# - PostgreSQL 17.2 (包含必要的数据库工具)
# - Python 3 (用于运行 ELT 脚本)
#
# 包含组件：
# 1. PostgreSQL 客户端工具
#    - pg_dump: 用于导出数据
#    - psql: 用于导入数据
# 2. Python 环境
#    - 用于执行数据处理脚本
#
# 工作流程：
# 1. 构建镜像时安装必要组件
# 2. 复制 ELT 脚本到容器
# 3. 容器启动时自动执行脚本

# 使用 PostgreSQL 17.2 的基础镜像
FROM postgres:17.2-bookworm

# 安装 Python 和 PostgreSQL 客户端
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    postgresql-client

# 将 ETL 脚本复制到容器中
COPY elt_script.py .

# 设置容器启动时执行的命令
CMD ["python3", "elt_script.py"]