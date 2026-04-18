FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# ... 前面的 FROM 和 WORKDIR 不变 ...

COPY requirements.txt .

# 第一步：单独安装 Git（确保它一定被安装了）
# 使用 --no-cache 避免 apt 缓存问题
RUN apt-get update && apt-get install -y --no-install-recommends git

# 第二步：安装 Python 依赖
# 注意：这里不要卸载 git，因为 pip 需要它来 clone 代码
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# 第三步：(可选) 如果你非常在意镜像体积，可以在这里卸载 git
# 但通常保留 git 对运行时的 APK 构建没有坏处，反而能避免很多麻烦
# RUN apt-get purge -y --auto-remove git && rm -rf /var/lib/apt/lists/*

# ... 后面的代码 ...

# 复制项目代码
COPY . .

# 这里的命令取决于你的构建脚本，如果是用 buildozer 打包安卓，通常是：
# CMD ["buildozer", "android debug"]
