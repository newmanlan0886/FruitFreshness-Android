# -*- coding: utf-8 -*-
"""
Android 版主程式 - Kivy 前端
實作功能：攝影機預覽、拍照、Gemini AI 圖片分析
字體：使用霞鶩文楷 (LXGWWenKai)
功能：啟動時彈窗輸入 API Key
修正：Android 檔案路徑問題
"""
import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.utils import platform
from PIL import Image as PILImage

from modules.gemini_rest import GeminiRESTClient as GeminiAnalyzer
from modules.config import AppConfig

# 🔥 根據平台取得正確的檔案路徑
def get_font_path():
    """根據執行平台取得字體檔案的正確路徑"""
    if platform == 'android':
        # Android 上，檔案在 APK 內的 assets 或根目錄
        from android.storage import primary_external_storage_path
        # 嘗試多個可能的路徑
        possible_paths = [
            '/data/data/org.yourorg.fruitfreshness/files/app/fonts/LXGWWenKai-Regular.ttf',
            '/data/data/org.yourorg.fruitfreshness/files/fonts/LXGWWenKai-Regular.ttf',
            '/sdcard/Android/data/org.yourorg.fruitfreshness/files/fonts/LXGWWenKai-Regular.ttf',
            './fonts/LXGWWenKai-Regular.ttf',
            'fonts/LXGWWenKai-Regular.ttf'
        ]
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ 找到字體檔案: {path}")
                return path
        return None
    else:
        # 桌面版開發時使用相對路徑
        return 'fonts/LXGWWenKai-Regular.ttf'

# 🔥 註冊霞鶩文楷字體
FONT_NAME = 'Roboto'  # 預設字體
font_path = get_font_path()
if font_path and os.path.exists(font_path):
    try:
        LabelBase.register(name='LXGWWenKai', fn_regular=font_path)
        FONT_NAME = 'LXGWWenKai'
        print(f"✅ 成功載入霞鶩文楷字體: {font_path}")
    except Exception as e:
        print(f"⚠️ 字體載入失敗，使用預設字體: {e}")
else:
    print(f"⚠️ 字體檔案不存在: {font_path}，使用預設字體")
    print("📌 在 Android 上，請確保字體已被打包進 APK")

class ApiKeyPopup(Popup):
    """API Key 輸入彈窗"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "設定 API Key"
        self.size_hint = (0.8, 0.4)
        self.auto_dismiss = False  # 禁止點擊外部關閉
        
        # 主佈局
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # 說明文字
        content.add_widget(Label(
            text="請輸入您的 Gemini API Key：",
            font_name=FONT_NAME,
            size_hint_y=0.3,
            color=(0.2, 0.2, 0.2, 1)
        ))
        
        # 輸入框
        self.api_input = TextInput(
            hint_text='輸入 API Key...',
            multiline=False,
            password=True,  # 隱藏輸入
            font_name=FONT_NAME,
            size_hint_y=0.3
        )
        content.add_widget(self.api_input)
        
        # 提示文字
        content.add_widget(Label(
            text="金鑰僅用於本次執行，不會被儲存",
            font_name=FONT_NAME,
            font_size='12sp',
            size_hint_y=0.2,
            color=(0.5, 0.5, 0.5, 1)
        ))
        
        # 按鈕區域
        btn_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        
        confirm_btn = Button(
            text="確認",
            font_name=FONT_NAME,
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        confirm_btn.bind(on_press=self.on_confirm)
        
        cancel_btn = Button(
            text="取消",
            font_name=FONT_NAME,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        cancel_btn.bind(on_press=self.on_cancel)
        
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        self.content = content
        self.api_key = None
    
    def on_confirm(self, instance):
        """確認按鈕事件"""
        self.api_key = self.api_input.text.strip()
        if not self.api_key:
            # 顯示錯誤提示
            error_popup = Popup(
                title='錯誤',
                content=Label(
                    text='API Key 不能為空！',
                    font_name=FONT_NAME
                ),
                size_hint=(0.6, 0.3)
            )
            error_popup.open()
            return
        self.dismiss()
    
    def on_cancel(self, instance):
        """取消按鈕事件"""
        self.api_key = None
        self.dismiss()

class FruitFreshnessAndroidApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = None
        self.gemini = None
        self.config = AppConfig()
        self.camera = None
        self.img_preview = None
        self.result_text = None
        self.status = None
    
    def build(self):
        """建立 UI（先顯示 API Key 彈窗）"""
        # 顯示 API Key 輸入彈窗
        self.show_api_key_popup()
        
        # 建立主佈局（先返回空，等 API Key 設定完成後再建立實際 UI）
        self.root_layout = BoxLayout(orientation='vertical')
        
        # 顯示載入中畫面
        loading_label = Label(
            text="載入中...\n請輸入 API Key",
            font_name=FONT_NAME,
            font_size='20sp'
        )
        self.root_layout.add_widget(loading_label)
        
        return self.root_layout
    
    def show_api_key_popup(self):
        """顯示 API Key 輸入彈窗"""
        popup = ApiKeyPopup()
        popup.bind(on_dismiss=self.on_popup_dismiss)
        popup.open()
    
    def on_popup_dismiss(self, instance):
        """彈窗關閉時的回調"""
        api_key = instance.api_key
        
        if not api_key:
            # 使用者取消，顯示提示並退出
            self.show_error_and_exit("未輸入 API Key，程式將關閉")
            return
        
        self.api_key = api_key
        print(f"✅ 已取得 API Key: {api_key[:5]}...")
        
        # 初始化 Gemini
        try:
            self.gemini = GeminiAnalyzer(api_key=self.api_key, model_name="gemini-2.5-flash")
            print("✅ Gemini 初始化成功")
            
            # 建立實際的 UI
            Clock.schedule_once(lambda dt: self.build_main_ui(), 0)
            
        except Exception as e:
            print(f"❌ Gemini 初始化失敗: {e}")
            self.show_error_and_exit(f"Gemini 初始化失敗：{str(e)}")
    
    def show_error_and_exit(self, message):
        """顯示錯誤並退出"""
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(
            text=message,
            font_name=FONT_NAME,
            size_hint_y=0.7
        ))
        
        close_btn = Button(
            text="關閉",
            font_name=FONT_NAME,
            size_hint_y=0.3,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        content.add_widget(close_btn)
        
        error_popup = Popup(
            title='錯誤',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        close_btn.bind(on_press=lambda x: (
            error_popup.dismiss(),
            Clock.schedule_once(lambda dt: self.stop(), 0.1)
        ))
        
        error_popup.open()
    
    def build_main_ui(self):
        """建立主要 UI（在取得 API Key 後呼叫）"""
        # 清除原有的載入畫面
        self.root_layout.clear_widgets()
        
        # 建立主佈局
        root = BoxLayout(orientation='vertical', spacing=5, padding=10)

        # 標題列
        title = Label(
            text="水果新鮮度診斷 (Android版)",
            size_hint=(1, 0.1),
            font_size='20sp',
            bold=True,
            font_name=FONT_NAME,
            color=(0.2, 0.6, 0.2, 1)  # 深綠色標題
        )
        root.add_widget(title)

        # 攝影機區域
        cam_box = BoxLayout(orientation='vertical', size_hint=(1, 0.4))
        self.camera = Camera(play=True, resolution=(640, 480))
        cam_box.add_widget(self.camera)

        # 拍照按鈕
        btn_capture = Button(
            text="📸 拍照分析",
            size_hint=(1, 0.15),
            font_name=FONT_NAME,
            background_color=(0.2, 0.8, 0.2, 1),  # 綠色按鈕
            color=(1, 1, 1, 1)
        )
        btn_capture.bind(on_press=self.capture_and_analyze)
        cam_box.add_widget(btn_capture)
        root.add_widget(cam_box)

        # 圖片預覽區域
        preview_label = Label(
            text="📸 拍攝預覽",
            size_hint=(1, 0.05),
            halign='left',
            font_name=FONT_NAME,
            bold=True,
            color=(0.5, 0.5, 0.5, 1)
        )
        root.add_widget(preview_label)
        self.img_preview = Image(size_hint=(1, 0.25), allow_stretch=True)
        root.add_widget(self.img_preview)

        # 分析結果區域
        result_label = Label(
            text="📊 分析結果",
            size_hint=(1, 0.05),
            halign='left',
            font_name=FONT_NAME,
            bold=True,
            color=(0.5, 0.5, 0.5, 1)
        )
        root.add_widget(result_label)
        self.result_text = TextInput(
            text="等待拍照分析...",
            readonly=True,
            size_hint=(1, 0.25),
            font_size='16sp',
            font_name=FONT_NAME,
            background_color=(0.95, 0.95, 0.95, 1)
        )
        root.add_widget(self.result_text)

        # 狀態列
        self.status = Label(
            text="就緒",
            size_hint=(1, 0.05),
            font_size='14sp',
            font_name=FONT_NAME,
            color=(0.3, 0.3, 0.3, 1)
        )
        root.add_widget(self.status)

        # 替換 root_layout 的內容
        self.root_layout.add_widget(root)

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
        # Kivy 的 Texture 座標系與 PIL 不同，需要垂直翻轉
        pil_image = pil_image.transpose(PILImage.FLIP_TOP_BOTTOM)
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