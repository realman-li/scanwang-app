[app]
# 应用信息
title = 文档扫描仪
package.name = docscanner
package.domain = org.yourname
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# 依赖（完全匹配代码需要的库）
requirements = python3, kivy==2.2.1, opencv-python==4.8.0.76, numpy==1.26.4, imutils==0.5.4, scikit-image==0.22.0, plyer==2.1.0, androidstorage4kivy==0.8.1

# 安卓配置
android.api = 33
android.ndk = 25b
android.sdk = 24.0.0
android.arch = arm64-v8a
android.permissions = CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES
android.ndk_path =
android.sdk_path =
android.gradle_dependencies = 'com.google.android.material:material:1.11.0'
android.enable_androidx = True
android.minapi = 26
android.sdk = 33

# 其他配置
fullscreen = 0
orientation = portrait
log_level = 2
