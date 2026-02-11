# -*- coding: utf-8 -*-
"""
Android 版主程式 - Kivy 前端
實作功能：攝影機預覽、拍照、Gemini AI 圖片分析
"""
import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from PIL import Image as PILImage
from dotenv import load_dotenv

from modules.gemini_client import GeminiAnalyzer
from modules.config import AppConfig
from modules.utils import ensure_dir, timestamp_str

# 載入 .env（若存在）
load_dotenv()

class FruitFreshnessAndroidApp(App):
    def build(self):
        self.config = AppConfig()
        self.gemini = None
        try:
            self.gemini = GeminiAnalyzer(model_name="gemini-2.5-flash")
        except Exception as e:
            print(f"Gemini 初始化失敗: {e}")

        # 建立主佈局
        root = BoxLayout(orientation='vertical', spacing=5, padding=10)

        # 標題列
        title = Label(
            text="水果新鮮度診斷 (Android版)",
            size_hint=(1, 0.1),
            font_size='20sp',
            bold=True
        )
        root.add_widget(title)

        # 攝影機區域
        cam_box = BoxLayout(orientation='vertical', size_hint=(1, 0.4))
        self.camera = Camera(play=True, resolution=(640, 480))
        cam_box.add_widget(self.camera)

        # 拍照按鈕
        btn_capture = Button(text="📸 拍照分析", size_hint=(1, 0.15))
        btn_capture.bind(on_press=self.capture_and_analyze)
        cam_box.add_widget(btn_capture)
        root.add_widget(cam_box)

        # 圖片預覽區域
        preview_label = Label(text="拍攝預覽", size_hint=(1, 0.05), halign='left')
        root.add_widget(preview_label)
        self.img_preview = Image(size_hint=(1, 0.25), allow_stretch=True)
        root.add_widget(self.img_preview)

        # 分析結果區域（可捲動）
        result_label = Label(text="分析結果", size_hint=(1, 0.05), halign='left')
        root.add_widget(result_label)
        self.result_text = TextInput(
            text="等待拍照分析...",
            readonly=True,
            size_hint=(1, 0.25),
            font_size='16sp'
        )
        root.add_widget(self.result_text)

        # 狀態列
        self.status = Label(
            text="就緒",
            size_hint=(1, 0.05),
            font_size='14sp'
        )
        root.add_widget(self.status)

        return root

    def capture_and_analyze(self, instance):
        """拍照並呼叫 Gemini 分析"""
        if not self.gemini:
            self.update_status("❌ Gemini 未初始化")
            return

        texture = self.camera.texture
        if not texture:
            self.update_status("⚠️ 無法取得攝影機畫面")
            return

        # 將 Kivy Texture 轉為 PIL Image
        size = texture.size
        pixels = texture.pixels
        pil_image = PILImage.frombytes(mode='RGBA', size=size, data=pixels)
        pil_image = pil_image.convert('RGB')

        # 顯示預覽
        self.img_preview.texture = texture
        self.update_status("📷 拍照完成，正在分析...")

        # 非同步呼叫 Gemini API
        threading.Thread(target=self._analyze_thread, args=(pil_image,), daemon=True).start()

    def _analyze_thread(self, image: PILImage.Image):
        """在背景執行 Gemini 分析"""
        prompt = """
你是一位專業的水果品質分析師。請詳細分析這張水果圖片，提供：
1. 水果種類識別
2. 新鮮度評分（0-100）
3. 成熟度評分（0-100）
4. 顏色與外觀觀察
5. 建議（保存/食用/處理方式）
6. 快速結論（1-2行）

請使用繁體中文回答，格式清晰易讀。
"""
        try:
            result = self.gemini.analyze_image(image, prompt)
        except Exception as e:
            result = f"分析失敗：{str(e)}"

        # 回到主線程更新 UI
        Clock.schedule_once(lambda dt: self.update_result(result))

    def update_result(self, text: str):
        """更新結果文字框"""
        self.result_text.text = text
        self.update_status("✅ 分析完成")

    def update_status(self, message: str):
        """更新狀態列"""
        self.status.text = message

if __name__ == '__main__':
    FruitFreshnessAndroidApp().run()