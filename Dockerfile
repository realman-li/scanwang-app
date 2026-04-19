# 1. 使用轻量级 Python 基础镜像
FROM python:3.10-slim

# 设置非交互式环境，防止安装过程中弹出配置窗口
ENV DEBIAN_FRONTEND=noninteractive
# 设置时区（可选，推荐）
ENV TZ=Asia/Shanghai

# 2. 设置工作目录
WORKDIR /app

# 3. 安装系统依赖
# 增加了：tzdata (时区), fonts-wqy-zenhei (中文字体-文泉驿), ffmpeg (如果处理视频/音频)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    build-essential \
    tzdata \
    fonts-wqy-zenhei \
    ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 4. 安装 Python 依赖 (利用 Docker 缓存机制)
# 先只复制 requirements.txt，这样代码变动时不需要重新 pip install
COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# 5. 复制项目代码
COPY . .

# 6. 启动命令 (根据你的实际情况修改)
# CMD ["python", "main.py"]
