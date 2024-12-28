# 导入需要的Python包
# Flask: 用于创建Web API的框架
# request: 用于获取HTTP请求数据
# jsonify: 用于将Python对象转换为JSON响应
from flask import Flask, request, jsonify

# SQLAlchemy: 数据库ORM框架，让我们可以用Python代码操作数据库
from flask_sqlalchemy import SQLAlchemy

# 用于处理日期时间的Python标准库
from datetime import datetime, date

# SQLAlchemy的自动映射功能，可以自动创建数据库表对应的Python类
from sqlalchemy.ext.automap import automap_base
import requests
import time
from sqlalchemy import text
from sqlalchemy import MetaData, Table
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 创建Flask应用
# Flask(__name__)中的__name__是Python的一个特殊变量，表示当前模块的名称
app = Flask(__name__)

# 设置数据库连接
# 格式：数据库类型://用户名:密码@数据库地址:端口/数据库名
# postgresql: 数据库类型
# postgres: 用户名
# secret: 密码
# destination_postgres: 数据库服务器地址
# 5432: PostgreSQL的默认端口
# destination_db: 数据库名称
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:secret@destination_postgres:5432/destination_db"
)

# 创建数据库操作对象
db = SQLAlchemy(app)

# 创建 MetaData 实例
metadata = MetaData()


# 等待数据库连接
def wait_for_db():
    max_retries = 5
    for i in range(max_retries):
        try:
            with db.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                logger.info("数据库连接成功！")
                # 验证表的访问权限
                tables = ["films", "actors", "film_actors"]
                for table in tables:
                    try:
                        connection.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                        logger.info(f"成功访问表 {table}")
                    except Exception as e:
                        logger.error(f"访问表 {table} 失败: {str(e)}")
            return True
        except Exception as e:
            logger.error(f"等待数据库连接... ({i+1}/{max_retries})")
            logger.error(f"错误信息: {str(e)}")
            time.sleep(1)
    raise Exception("无法连接到数据库")


with app.app_context():
    # 等待数据库就绪
    wait_for_db()

    # 直接从数据库反射有表
    metadata.reflect(bind=db.engine)

    # 获取表对象
    Film = metadata.tables["films"]
    Actor = metadata.tables["actors"]
    FilmActor = metadata.tables["film_actors"]

    print("\n成功加载表结构：")
    for table_name in metadata.tables:
        print(f"- {table_name}")


# 外部请求 -> localhost:5000/films -> 容器内Flask应用 -> PostgreSQL数据库
#                                                   -> 触发Airflow任务
# API路由：添加新电影
# @app.route 是一个装饰器，用来定义API的URL和HTTP方法
# '/films'是API的URL路径
# methods=['POST']表示这个API只接受POST请求
@app.route("/films", methods=["POST"])
def add_film():
    try:
        logger.info("接收到添加电影请求")
        logger.debug("请求数据: %s", request.json)

        # 检查请求数据是否存在
        if not request.json:
            return jsonify({"error": "没有提供JSON数据"}), 400

        # 验证必需的字段
        required_fields = ["title", "release_date", "price", "rating", "user_rating"]
        for field in required_fields:
            if field not in request.json:
                return jsonify({"error": f"缺少必需字段: {field}"}), 400

        data = request.json
        result = db.session.execute(
            Film.insert().values(
                title=data["title"],
                release_date=date.fromisoformat(data["release_date"]),
                price=data["price"],
                rating=data["rating"],
                user_rating=data["user_rating"],
            )
        )
        db.session.commit()

        # 添加电影成功后触发 DBT 转换任务
        dbt_trigger_result = trigger_dbt_transformation()
        if not dbt_trigger_result:
            logger.warning("DBT 转换任务触发失败，但电影已成功添加")

        logger.info("电影添加成功，ID: %s", result.inserted_primary_key[0])
        return jsonify(
            {
                "message": "Film added successfully",
                "film_id": result.inserted_primary_key[0],
                "dbt_task_triggered": dbt_trigger_result,
            }
        )
    except ValueError as ve:
        logger.error("数据格式错误: %s", str(ve), exc_info=True)
        db.session.rollback()
        return jsonify({"error": f"数据格式错误: {str(ve)}"}), 400
    except Exception as e:
        logger.error("添加电影失败: %s", str(e), exc_info=True)
        db.session.rollback()
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500


# API路由：添加新演员
@app.route("/actors", methods=["POST"])
def add_actor():
    try:
        data = request.json
        result = db.session.execute(
            Actor.insert().values(actor_name=data["actor_name"])
        )
        db.session.commit()
        return jsonify(
            {
                "message": "Actor added successfully",
                "actor_id": result.inserted_primary_key[0],
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# API路由：添加电影-演员关联关系
@app.route("/film-actors", methods=["POST"])
def add_film_actor():
    try:
        data = request.json
        result = db.session.execute(
            FilmActor.insert().values(
                film_id=data["film_id"], actor_id=data["actor_id"]
            )
        )
        db.session.commit()
        return jsonify({"message": "Film-Actor relationship added successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# 触发数据转换任务的函数
def trigger_dbt_transformation():
    """直接触发 Airflow DAG 中的 DBT 任务"""
    try:
        # 修改 URL 以直接触发特定任务
        airflow_url = (
            "http://webserver:8080/api/v1/dags/elt_and_dbt/tasks/run_dbt_task/run"
        )

        auth = ("airflow", "admin123")

        headers = {
            "Content-Type": "application/json",
        }

        data = {"execution_date": datetime.now().isoformat()}

        logger.info(f"正在触发 DBT 任务，URL: {airflow_url}")
        logger.debug(f"使用认证用户: airflow")
        logger.debug(f"请求头: {headers}")
        logger.debug(f"请求数据: {data}")

        response = requests.post(
            airflow_url, json=data, headers=headers, auth=auth, timeout=10
        )

        logger.info(f"Airflow API 响应状态码: {response.status_code}")
        logger.info(f"Airflow API 响应内容: {response.text}")

        if response.status_code != 200:
            raise Exception(f"触发 DBT 任务失败: {response.text}")
        return True
    except requests.exceptions.ConnectionError as ce:
        logger.error(f"连接到 Airflow 失败: {str(ce)}")
        return False
    except requests.exceptions.Timeout as te:
        logger.error(f"请求超时: {str(te)}")
        return False
    except Exception as e:
        logger.error(f"触发 DBT 任务时发生错误: {str(e)}")
        return False


# 应用程序入口点
if __name__ == "__main__":
    with app.app_context():
        try:
            wait_for_db()
            logger.info("API 服务启动成功")
            # 统一使用5001端口
            app.run(host="0.0.0.0", port=5001, debug=True)
        except Exception as e:
            logger.error("API 服务启动失败: %s", str(e))
