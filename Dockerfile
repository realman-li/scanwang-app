FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 【关键修改】先更新系统源，安装 git，然后再安装 python 依赖
# 最后清理缓存以减小镜像体积
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove git && \
    rm -rf /var/lib/apt/lists/*

# 复制项目代码
COPY . .

# 这里的命令取决于你的构建脚本，如果是用 buildozer 打包安卓，通常是：
# CMD ["buildozer", "android debug"]
