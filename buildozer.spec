[app]
title = 文档扫描仪
package.name = docscanner
package.domain = org.scan
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3,kivy==2.2.1,opencv-python==4.8.0.76,numpy,imutils,scikit-image,plyer,androidstorage4kivy

android.api = 33
android.ndk = 25b
android.sdk = 24.0.0
android.arch = arm64-v8a
android.permissions = CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES
android.minapi = 24
fullscreen = 0
orientation = portrait
log_level = 2
