[app]
title = Document Scanner
package.name = docscanner
package.domain = org.example
source.dir = .
version = 1.0
requirements = python3,kivy,opencv-python-headless,imutils,numpy,scikit-image,plyer,androidstorage4kivy
icon.filename = assets/icon.png

[android]
permissions = CAMERA,INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
api = 34
minapi = 21
ndk = 23b
arch = arm64-v8a
