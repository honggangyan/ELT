from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator
from docker.types import Mount
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.bash import BashOperator
from airflow.models import Variable
import subprocess
from airflow.operators.python import BranchPythonOperator

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

def run_elt_script():
    script_path = "/opt/airflow/elt_script/elt_script.py"
    result = subprocess.run(["python3", script_path], capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(f"ELT script failed with output: {result.stderr}")
    print("ELT script completed successfully.")
    # 设置初始化标志
    Variable.set("is_initialized", "true")

def should_run_elt():
    """检查是否需要运行 ELT 脚本，返回下一个要执行的任务ID"""
    is_initialized = Variable.get("is_initialized", default_var="false")
    if is_initialized.lower() != "true":
        return "run_elt_script"  # 返回 ELT 任务的 task_id
    return "run_dbt_task"        # 返回 DBT 任务的 task_id

# 创建主 DAG
dag = DAG(
    "elt_and_dbt",
    default_args=default_args,
    description="ELT workflow with dbt",
    schedule_interval=None,
    start_date=datetime(2024, 12, 26),
    catchup=False,
    tags=['manual'],
)

# 分支任务
branch_task = BranchPythonOperator(
    task_id='check_initialization',
    python_callable=should_run_elt,
    dag=dag,
    trigger_rule='all_done'
)

# ELT 任务
t1 = PythonOperator(
    task_id="run_elt_script",
    python_callable=run_elt_script,
    dag=dag,
    execution_timeout=timedelta(minutes=2),
)

# DBT 任务
t2 = DockerOperator(
    task_id="run_dbt_task",
    image="ghcr.io/dbt-labs/dbt-postgres:1.7.3",
    command=["run", "--profiles-dir", "/root", "--project-dir", "/opt/dbt"],
    auto_remove=True,
    docker_url="unix://var/run/docker.sock",
    network_mode="elt_elt_network",
    mounts=[
        Mount(
            source="/Users/honggang/dev/data-engineering/elt/custom_postgres",
            target="/opt/dbt",
            type="bind",
        ),
        Mount(source="/Users/honggang/.dbt", target="/root", type="bind"),
    ],
    mount_tmp_dir=False,
    dag=dag,
    trigger_rule='all_done'
)

# 修改任务依赖
branch_task >> t1 >> t2  # branch_task 到 t1 到 t2 的路径
branch_task >> t2       # branch_task 直接到 t2 的路径
