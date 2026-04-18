# Dockerfile for GitHub Actions
FROM ubuntu:22.04

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    OPENCV_VERSION=4.8.0 \
    NUMPY_VERSION=1.26.0 \
    KIVY_VERSION=2.3.0

# 安装系统依赖（优化安装顺序，利用Docker缓存）
RUN apt-get update && apt-get install -y --no-install-recommends \
    # 基础工具
    git zip unzip curl wget build-essential cmake \
    # Java 17 (Android构建必需)
    openjdk-17-jdk-headless \
    # Python 3.13
    python3 python3-pip python3-venv python3-dev \
    # OpenCV依赖
    libopencv-dev libgtk-3-dev libavcodec-dev libavformat-dev \
    libswscale-dev libv4l-dev libxvidcore-dev libx264-dev \
    libjpeg-dev libpng-dev libtiff-dev gfortran \
    # 科学计算
    libatlas-base-dev liblapacke-dev libhdf5-dev \
    # Android构建工具
    libtool autoconf automake pkg-config \
    libssl-dev libffi-dev libsqlite3-dev \
    # SDL2图形库
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    # 其他依赖
    libbz2-dev libreadline-dev liblzma-dev \
    # 清理
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN useradd -m -u 1001 builder && \
    mkdir -p /app && \
    chown -R builder:builder /app

USER builder
# 创建非root用户（GitHub Actions推荐）
# 检查用户是否已存在，不存在则创建，并修正目录权限
RUN if ! id -u builder >/dev/null 2>&1; then \
      useradd -m -u 1001 builder; \
    fi && \
    mkdir -p /app && \
    chown -R builder:builder /app
USER builder

# 设置工作目录
WORKDIR /app

# 安装Python依赖（分层安装，优化缓存）
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 设置构建命令
CMD ["bash", "-c", "buildozer android debug"]
