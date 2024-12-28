# 使用 Python 3.9 的精简版本作为基础镜像
FROM python:3.9-slim

# 设置容器内的工作目录为 /app
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 文件到容器中
COPY requirements.txt .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 将当前目录下的所有文件复制到容器的工作目录中
COPY . .

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# 暴露端口
EXPOSE 5001

# 启动 Flask 应用
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"] 