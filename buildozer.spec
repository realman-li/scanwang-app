[app]
title = Your App Name
package.name = yourpackagename
package.domain = org.example
source.dir = .
version = 1.0

[python]
requirements = kivy==2.2.1,opencv-python-headless==4.8.1.78,imutils==0.5.4,numpy==1.24.3,scikit-image==0.21.0,plyer==2.1.0,androidstorage4kivy==1.1.0

[android]
permissions = CAMERA,INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
api = 34
minapi = 21
ndk = 23.0.7599858
