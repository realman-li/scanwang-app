name: Build Android APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    env:
      BUILD_TOOLS_VERSION: "33.0.0"
      COMPILE_SDK_VERSION: "33"
      MIN_SDK_VERSION: "21"
      TARGET_SDK_VERSION: "33"
      
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up JDK 17
      uses: actions/setup-java@v3
      with:
        java-version: '17'
        distribution: 'temurin'
        
    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y git zip unzip python3 python3-pip autoconf libtool pkg-config libpng-dev libjpeg-dev libtiff-dev libffi-dev
        
    - name: Install Buildozer
      run: |
        pip3 install --user Cython==0.29.33
        pip3 install --user buildozer
        
    - name: Initialize Buildozer
      run: |
        buildozer init
        # 复制我们自定义的buildozer.spec
        cp buildozer.spec ./
        
    - name: Build APK
      run: |
        buildozer -v android debug
      env:
        DISPLAY: ':99.0'
        
    - name: Upload APK artifact
      uses: actions/upload-artifact@v3
      with:
        name: debug-apk
        path: bin/*.apk
