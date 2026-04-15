import cv2
import numpy as np
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from fpdf import FPDF
from PIL import Image as PILImage

# 自动对齐核心算法
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
    maxWidth = max(int(np.sqrt(((br[0]-bl[0])**2)+((br[1]-bl[1])**2))),
                   int(np.sqrt(((tr[0]-tl[0])**2)+((tr[1]-tl[1])**2))))
    maxHeight = max(int(np.sqrt(((tr[0]-br[0])**2)+((tr[1]-br[1])**2))),
                    int(np.sqrt(((tl[0]-bl[0])**2)+((tl[1]-bl[1])**2))))
    dst = np.array([[0, 0], [maxWidth-1, 0], [maxWidth-1, maxHeight-1], [0, maxHeight-1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (maxWidth, maxHeight), flags=cv2.INTER_CUBIC)

# 扫描增强（去阴影、高清）
def scan_image(img_path):
    img = cv2.imread(img_path)
    if img is None: return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edged = cv2.Canny(blur, 50, 150)

    contours = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    screenCnt = None

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02*peri, True)
        if len(approx) == 4:
            screenCnt = approx
            break

    if screenCnt is not None:
        warped = four_point_transform(img, screenCnt.reshape(4,2))
    else:
        warped = img

    gray_warp = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray_warp = clahe.apply(gray_warp)
    thresh = cv2.adaptiveThreshold(gray_warp,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,15,10)

    out_path = "scan_temp.png"
    cv2.imwrite(out_path, thresh)
    return out_path

# 导出PDF
def export_pdf(page_list, pdf_name="扫描文档.pdf"):
    if not page_list: return False
    pdf = FPDF()
    for img in page_list:
        pdf.add_page()
        pdf.image(img, x=10, y=10, w=190, keep_aspect_ratio=True)
    pdf.output(pdf_name)
    return True

# 手机APP主界面
class ScanApp(App):
    def build(self):
        self.pages = []
        self.current_img = "temp.jpg"

        root = BoxLayout(orientation='vertical', padding=8, spacing=8)

        self.preview = Image(size_hint=(1, 0.6))
        root.add_widget(self.preview)

        btn_layout = BoxLayout(size_hint=(1, 0.15), spacing=5)
        self.btn_camera = Button(text="相机拍照", background_color=(0.2,0.6,1,1))
        self.btn_album = Button(text="相册选择", background_color=(0.3,0.7,0.3,1))
        self.btn_add = Button(text="添加页面", background_color=(1,0.6,0,1))
        self.btn_export = Button(text="导出PDF", background_color=(1,0.2,0.2,1))

        self.btn_camera.bind(on_press=self.take_photo)
        self.btn_album.bind(on_press=self.open_album)
        self.btn_add.bind(on_press=self.add_page)
        self.btn_export.bind(on_press=self.do_export)

        btn_layout.add_widget(self.btn_camera)
        btn_layout.add_widget(self.btn_album)
        btn_layout.add_widget(self.btn_add)
        btn_layout.add_widget(self.btn_export)
        root.add_widget(btn_layout)

        return root

    # 相机拍照
    def take_photo(self, *args):
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE])
        
        layout = BoxLayout(orientation='vertical')
        self.cam_preview = Image(size_hint=(1, 0.9))
        layout.add_widget(self.cam_preview)
        
        def capture():
            self.cam.export_to_png(self.current_img)
            self.process_and_show()
            popup.dismiss()
        
        self.cam = Camera(resolution=(1280,720), play=True)
        self.cam.bind(on_texture=lambda: setattr(self.cam_preview, 'texture', self.cam.texture))
        btn = Button(text="拍照", size_hint=(1, 0.1), on_press=lambda _: capture())
        layout.add_widget(btn)

        popup = Popup(title="拍照", content=layout, size_hint=(0.9, 0.9))
        popup.open()

    # 相册选图
    def open_album(self, *args):
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
        
        layout = BoxLayout(orientation='vertical')
        chooser = FileChooserListView(filters=['*.png','*.jpg','*.jpeg'])
        layout.add_widget(chooser)
        
        def select():
            if chooser.selection:
                self.current_img = chooser.selection[0]
                self.process_and_show()
                popup.dismiss()
        
        btn = Button(text="确定", size_hint=(1, 0.1), on_press=lambda _: select())
        layout.add_widget(btn)

        popup = Popup(title="选择图片", content=layout, size_hint=(0.9, 0.9))
        popup.open()

    # 扫描处理
    def process_and_show(self):
        result = scan_image(self.current_img)
        if result:
            self.show_img(result, self.preview)

    # 添加多页
    def add_page(self, *args):
        if os.path.exists("scan_temp.png"):
            page = f"page_{len(self.pages)+1}.png"
            os.rename("scan_temp.png", page)
            self.pages.append(page)
            print(f"✅ 已添加第{len(self.pages)}页")

    # 导出PDF
    def do_export(self, *args):
        if export_pdf(self.pages):
            print("📄 PDF导出成功！")
        else:
            print("❌ 请先添加扫描页")

    # 显示图片
    def show_img(self, path, widget):
        img = PILImage.open(path).convert("RGBA")
        data = img.tobytes()
        tex = Texture.create(size=img.size, colorfmt='rgba')
        tex.blit_buffer(data, colorfmt='rgba', bufferfmt='ubyte')
        tex.flip_vertical()
        widget.texture = tex

if __name__ == "__main__":
    ScanApp().run()
