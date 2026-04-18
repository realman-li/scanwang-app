# 1. 基础镜像：使用 slim 版本以保持轻量，同时支持 apt-get
FROM python:3.10-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 安装系统级依赖
# 关键修复：这里必须安装 git，因为你的 requirements.txt 里有 github 的库
# 同时安装 build-essential，防止编译 python 库（如 lxml, pillow 等）时报错
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. 复制 Python 依赖文件
COPY requirements.txt .

# 5. 安装 Python 依赖
# 此时 git 已经存在，pip 可以顺利拉取 github 代码
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# 6. 复制项目其余代码
COPY . .

# 7. 默认命令（根据你的项目实际情况修改，如果是打包 APK，通常是 buildozer）
# CMD ["python", "main.py"]
