# -*- coding: utf-8 -*-
# 文档扫描仪安卓APP (完全基于你原OpenCV代码改造)
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import mainthread
from kivy.utils import platform

import cv2
import numpy as np
import imutils
import os
from datetime import datetime
from skimage.filters import threshold_local
from plyer import camera

# ================= 完全保留你原代码的核心函数 =================
def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

# ================= 完全保留你原代码的扫描逻辑 =================
def scan_document(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return None
    
    ratio = image.shape[0] / 500.0
    orig = image.copy()
    image = imutils.resize(image, height=500)

    # 1. 边缘检测 (原代码步骤)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)

    # 2. 寻找轮廓 (原代码步骤)
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    screenCnt = None
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            screenCnt = approx
            break

    # 3. 透视变换与二值化 (原代码步骤)
    if screenCnt is not None:
        warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
        warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        T = threshold_local(warped, 11, offset=10, method="gaussian")
        warped = (warped > T).astype("uint8") * 255
        return warped
    return None

# ================= 安卓APP界面逻辑 =================
class ScannerApp(App):
    def build(self):
        self.scan_result = None
        self.title = "文档扫描仪"

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 图片显示区域
        self.img_widget = Image(size_hint=(1, 0.7), allow_stretch=True)
        layout.add_widget(self.img_widget)

        # 按钮区域
        btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)
        
        # 拍照按钮
        self.btn_camera = Button(text="拍照扫描", font_size=18)
        self.btn_camera.bind(on_press=self.take_photo)
        btn_layout.add_widget(self.btn_camera)

        # 保存按钮
        self.btn_save = Button(text="保存扫描件", font_size=18)
        self.btn_save.bind(on_press=self.save_scan)
        btn_layout.add_widget(self.btn_save)

        layout.add_widget(btn_layout)
        return layout

    def take_photo(self, instance):
        # 触发手机拍照
        photo_path = os.path.join(self.user_data_dir, "temp_shot.jpg")
        camera.take_picture(filename=photo_path, on_complete=self.on_photo_taken)

    def on_photo_taken(self, path):
        if path:
            # 后台处理扫描任务，防止界面卡顿
            import threading
            threading.Thread(target=self.process_scan, args=(path,)).start()

    def process_scan(self, image_path):
        result = scan_document(image_path)
        if result is not None:
            self.scan_result = result
            self.update_ui(result)

    @mainthread
    def update_ui(self, img):
        # 转换图像格式供Kivy显示
        img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        buf = cv2.flip(img_rgb, 0).tobytes()
        texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='rgb')
        texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        self.img_widget.texture = texture

    def save_scan(self, instance):
        if self.scan_result is None:
            return
            
        # 保存到系统相册
        if platform == "android":
            try:
                from androidstorage4kivy import SharedStorage
                ss = SharedStorage()
                filename = f"Scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                temp_path = os.path.join(self.user_data_dir, filename)
                cv2.imwrite(temp_path, self.scan_result)
                ss.copy_to_shared(temp_path, collection=ss.COLLECTION_PICTURES)
                print(f"保存成功: {filename}")
            except Exception as e:
                print(f"保存失败: {e}")

if __name__ == "__main__":
    ScannerApp().run()
