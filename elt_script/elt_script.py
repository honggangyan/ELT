"""
ELT 脚本 (PostgreSQL 数据迁移工具)
================================

主要功能概述：
-------------
这个脚本实现了一个简单的 PostgreSQL 数据库迁移工具，遵循 ELT（Extract-Load-Transform）模式：
1. Extract（提取）：从源数据库导出数据到 SQL 文件
2. Load（加载）：将 SQL 文件数据导入到目标数据库
3. Transform（转换）：预期在目标数据库中进行数据转换（本脚本未实现, 后期通过DBT实现）

技术特点：
- 使用 pg_dump 和 psql 工具进行数据迁移
- 实现数据库连接状态检查和重试机制
- 通过环境变量安全传递数据库密码
- 支持错误处理和状态报告

使用场景：
- 数据库迁移和备份
- 测试环境数据同步
- 数据仓库初始化加载

前提条件：
- PostgreSQL 客户端工具已安装（pg_dump, psql, pg_isready）
- 源数据库和目标数据库的连接信息正确配置
- 具有足够的磁盘空间存储导出文件
"""

#######################
# 导入必要的库
#######################
import subprocess
import time


#######################
# 数据库连接检查函数 CHECK CONNECTION
#######################
def wait_for_postgres(host, max_retries=5, delay_seconds=5):
    """
    Wait for PostgreSQL database to be ready

    Args:
        host: PostgreSQL host address
        max_retries: Maximum number of retry attempts (default 5)
        delay_seconds: Delay between retries (default 5 seconds)

    Returns:
        bool: True if database is ready, False otherwise
    """
    retries = 0
    while retries < max_retries:
        try:
            # Check database connection status using pg_isready command
            result = subprocess.run(
                ["pg_isready", "-h", host],
                check=True,  # Raises CalledProcessError if command returns non-zero status
                capture_output=True,  # Capture command's standard output
                text=True,  # Convert output to string
            )
            # Check if output contains "accepting connections"
            if "accepting connections" in result.stdout:
                print("PostgreSQL is ready.")
                return True
        except subprocess.CalledProcessError as e:
            # If connection fails, print error message and wait
            print(
                f"PostgreSQL is not ready yet. Retrying in {delay_seconds} seconds...(Attempt {retries + 1}/{max_retries})"
            )
            time.sleep(delay_seconds)
            retries += 1

    print("Failed to connect to PostgreSQL after max attempts.")
    return False


#######################
# 初始化检查
#######################
# Check if source database is ready
if not wait_for_postgres(host="source_postgres"):
    exit(1)

print("Starting ELT script...")


#######################
# 数据库配置 Configurion of database
#######################
source_config = {
    "dbname": "source_db",
    "user": "postgres",
    "password": "secret",
    "host": "source_postgres",
}

destination_config = {
    "dbname": "destination_db",
    "user": "postgres",
    "password": "secret",
    "host": "destination_postgres",
}

# EXTRACT and LOAD needs permission to read and write to the database.CHEKC PERMISSION IF ERROR.

#######################
# Extract: 数据导出阶段
#######################
# 添加调试信息
print("开始数据导出...")

# 设置环境变量
subprocess_env = dict(PGPASSWORD=source_config["password"])
# 先导出架构
dump_command = [
    "pg_dump",
    "-h", source_config["host"],
    "-U", source_config["user"],
    "-d", source_config["dbname"],
    "-f", "schema_dump.sql",
    "--schema-only",    # 只导出架构
    "--clean",          # 清理现有对象
    "--if-exists"       # 如果对象存在则删除
]

print(f"执行架构导出命令: {' '.join(dump_command)}")
result = subprocess.run(dump_command, env=subprocess_env, capture_output=True, text=True)
if result.returncode != 0:
    print(f"架构导出失败: {result.stderr}")
    exit(1)
print("架构导出成功")

# 检查导出的架构文件
print("\n导出的架构内容预览:")
with open("schema_dump.sql", "r") as f:
    print(f.read())

# 然后导出数据
dump_command = [
    "pg_dump",
    "-h", source_config["host"],
    "-U", source_config["user"],
    "-d", source_config["dbname"],
    "-f", "data_dump.sql",
    "--data-only"       # 只导出数据
]

print(f"\n执行数据导出命令: {' '.join(dump_command)}")
result = subprocess.run(dump_command, env=subprocess_env, capture_output=True, text=True)
if result.returncode != 0:
    print(f"数据导出失败: {result.stderr}")
    exit(1)
print("数据导出成功")


#######################
# Load: 数据加载阶段
#######################
# 加载阶段
print("\n开始数据导入...")

# 设置环境变量
subprocess_env = dict(PGPASSWORD=destination_config["password"])
# 先导入架构
# 先导入架构
load_command = [
    "psql",
    "-h", destination_config["host"],
    "-U", destination_config["user"],
    "-d", destination_config["dbname"],
    "-a",
    "-f", "schema_dump.sql"
]

print(f"执行架构导入命令: {' '.join(load_command)}")
result = subprocess.run(load_command, env=subprocess_env, capture_output=True, text=True)
if result.returncode != 0:
    print(f"架构导入失败: {result.stderr}")
    exit(1)
print("架构导入成功")

# 然后导入数据
load_command[-1] = "data_dump.sql"
print(f"\n执行数据导入命令: {' '.join(load_command)}")
result = subprocess.run(load_command, env=subprocess_env, capture_output=True, text=True)
if result.returncode != 0:
    print(f"数据导入失败: {result.stderr}")
    exit(1)
print("数据导入成功")

#######################
# 完成处理
#######################
print("Data load completed successfully. Ending ELT script.")
