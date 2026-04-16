# -*- coding: utf-8 -*-
# 完全基于你原有的OpenCV文档扫描代码改造的安卓APP
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
from plyer import camera, filechooser

# ====================== 完全保留你原代码的核心透视变换函数 ======================
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

# ====================== 完全保留你原代码的扫描逻辑 ======================
def scan_document(image_path):
    # 完全复刻你原代码的步骤：加载→缩放→边缘检测→找轮廓→透视变换→二值化
    image = cv2.imread(image_path)
    if image is None:
        return None
    
    ratio = image.shape[0] / 500.0
    orig = image.copy()
    image = imutils.resize(image, height=500)

    # 原代码：灰度化→高斯模糊→Canny边缘检测
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)

    # 原代码：找轮廓→排序→多边形逼近找4个角点
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

    # 原代码：透视变换→局部阈值二值化→生成扫描件
    if screenCnt is not None:
        warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
        warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        T = threshold_local(warped, 11, offset=10, method="gaussian")
        warped = (warped > T).astype("uint8") * 255
        return warped
    return None

# ====================== 安卓APP界面（仅加了外壳，不影响核心逻辑） ======================
class ScannerApp(App):
    def build(self):
        self.current_image = None
        self.scan_result = None
        self.title = "文档扫描仪"

        # 主布局
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)

        # 图片显示区域
        self.img_display = Image(size_hint=(1, 0.7), allow_stretch=True, keep_ratio=True)
        layout.add_widget(self.img_display)

        # 按钮区域
        btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)

        # 拍照按钮
        btn_camera = Button(text="拍照扫描", font_size=18)
        btn_camera.bind(on_press=self.take_photo)
        btn_layout.add_widget(btn_camera)

        # 从相册选择按钮
        btn_album = Button(text="相册选图", font_size=18)
        btn_album.bind(on_press=self.choose_from_album)
        btn_layout.add_widget(btn_album)

        # 保存按钮
        btn_save = Button(text="保存扫描件", font_size=18)
        btn_save.bind(on_press=self.save_scan)
        btn_layout.add_widget(btn_save)

        layout.add_widget(btn_layout)
        return layout

    # 拍照功能
    def take_photo(self, instance):
        # 安卓拍照路径
        save_path = os.path.join(self.user_data_dir, "temp_photo.jpg")
        camera.take_picture(filename=save_path, on_complete=self.on_photo_captured)

    # 拍照完成回调
    def on_photo_captured(self, path):
        if path and os.path.exists(path):
            self.current_image = path
            # 后台处理扫描，避免界面卡顿
            import threading
            threading.Thread(target=self.process_scan_thread, args=(path,)).start()

    # 从相册选择图片
    def choose_from_album(self, instance):
        filechooser.open_file(on_selection=self.on_file_selected)

    def on_file_selected(self, selection):
        if selection:
            self.current_image = selection[0]
            import threading
            threading.Thread(target=self.process_scan_thread, args=(selection[0],)).start()

    # 后台扫描处理线程
    def process_scan_thread(self, image_path):
        result = scan_document(image_path)
        if result is not None:
            self.scan_result = result
            # 主线程更新UI
            self.update_display(result)

    # 更新界面显示
    @mainthread
    def update_display(self, img):
        # 适配Kivy的纹理显示
        img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        img_flip = cv2.flip(img_rgb, 0)
        buf = img_flip.tobytes()
        texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='rgb')
        texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        self.img_display.texture = texture

    # 保存扫描件到相册
    @mainthread
    def save_scan(self, instance):
        if self.scan_result is None:
            return
        # 安卓保存到DCIM目录，相册可见
        if platform == "android":
            from androidstorage4kivy import SharedStorage
            ss = SharedStorage()
            filename = f"scan_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            temp_path = os.path.join(self.user_data_dir, filename)
            cv2.imwrite(temp_path, self.scan_result)
            ss.copy_to_shared(temp_path, collection=ss.COLLECTION_PICTURES)
            os.remove(temp_path)
        else:
            # 电脑测试用
            save_dir = os.path.join(os.path.expanduser("~"), "Pictures", "DocumentScanner")
            os.makedirs(save_dir, exist_ok=True)
            filename = f"scan_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            save_path = os.path.join(save_dir, filename)
            cv2.imwrite(save_path, self.scan_result)
        print("扫描件保存成功！")

if __name__ == "__main__":
    ScannerApp().run()
