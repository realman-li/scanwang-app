# 1. 使用轻量级 Python 基础镜像
FROM python:3.10-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 【关键修复】安装系统依赖
# 必须先安装 git，否则 pip 无法下载 github 上的库
# 同时安装 build-essential，防止编译 C 语言库时报错
RUN apt-get update && \
    apt-get install -y --no-install-recommends git build-essential && \
    rm -rf /var/lib/apt/lists/*

# 4. 复制依赖文件
COPY requirements.txt .

# 5. 安装 Python 依赖
# 此时系统里已经有 git 了，可以顺利拉取代码
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# 6. 复制项目代码
COPY . .

# 7. 启动命令（根据你的实际情况修改）
# CMD ["python", "main.py"]
