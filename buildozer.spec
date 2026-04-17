[app]

# (str) Title of your application
title = DocumentScanner

# (str) Package name
package.name = documentscanner

# (str) Package domain (needed for android/ios packaging)
package.domain = com.yourname

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,ttf,txt

# (str) Application version
version = 1.0

# (list) Application requirements
# 特别重要：包含所有依赖，特别是OpenCV和Android相关包
requirements = 
    python3==3.13.9,
    kivy==2.3.0,
    numpy==1.26.0,
    opencv-python-headless==4.8.0.76,
    imutils==0.5.4,
    scikit-image==0.21.0,
    plyer==2.1.0,
    androidstorage4kivy==1.0.0,
    pillow==10.0.1,
    requests==2.31.0

# (str) Presplash and icon
presplash.filename = %(source.dir)s/loading.png
icon.filename = %(source.dir)s/app_icon.png

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

#
# Android specific
#

# (bool) Use AndroidX library
android.enable_androidx = True

# (str) Android NDK version
android.ndk = 25b

# (int) Android API to use
android.api = 34

# (str) Android SDK version
android.sdk = 26

# (str) Android arch
android.arch = arm64-v8a

# (list) Permissions
android.permissions = 
    CAMERA,
    INTERNET,
    WRITE_EXTERNAL_STORAGE,
    READ_EXTERNAL_STORAGE,
    ACCESS_NETWORK_STATE

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme
android.theme = Theme.Material.Light.NoActionBar

# (list) Android add jars
android.add_jars = libs/*

# (list) Android add src
android.add_src = src/*

# (str) Android application identifier
android.package = com.yourname.documentscanner

# (bool) Enable AndroidX support
android.enable_androidx = True

# (bool) Copy python bytecode
p4a.pyc = True

# (bool) Strip binaries
p4a.strip = True

# (bool) Use color log
p4a.color = 1

# (str) Bootstrap to use
p4a.bootstrap = sdl2

# (str) Custom source folders for requirements
requirements.source.opencv-python-headless = https://github.com/skieffer/opencv-python-android

# (str) Android logcat filters
android.logcat_filters = *:S python:D

# (bool) Indicate if you want to bundle system requirements
p4a.bundle_system_requirements = True

# (bool) Indicate if you want to bundle system site-packages
p4a.bundle_site_packages = False

# (bool) Use setup.py install
p4a.setup_py_install = True
