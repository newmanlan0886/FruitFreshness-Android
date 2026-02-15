# modules/gemini_client.py
"""
Google Gemini API 客戶端（支援傳入 API Key）
"""
import os
import time
from typing import Optional
from dotenv import load_dotenv
from PIL import Image

# 載入環境變數（作為備用）
load_dotenv()

# 嘗試導入新版本 google-genai
try:
    import google.genai as genai
    from google.genai import types
    GENAI_NEW_VERSION = True
except ImportError:
    try:
        import google.generativeai as genai
        GENAI_NEW_VERSION = False
    except ImportError:
        genai = None
        GENAI_NEW_VERSION = False

class GeminiAnalyzer:
    """封裝 Gemini API 呼叫，支援傳入 API Key"""
    
    def __init__(self, api_key: str = None, model_name: str = "gemini-1.5-flash", max_retries: int = 4):
        """
        初始化 Gemini 分析器
        
        Args:
            api_key: Google Gemini API 金鑰（若為 None，則從環境變數讀取）
            model_name: 使用的模型名稱
            max_retries: 最大重試次數
        """
        self.model_name = model_name
        self.max_retries = max_retries
        
        # 優先使用傳入的 api_key，若無則從環境變數讀取
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        
        if not self.api_key:
            raise ValueError("❌ 未提供 API Key！請在啟動時輸入或在 .env 檔案中設定")
        
        if genai is None:
            raise ImportError("❌ 未安裝 google-genai 或 google-generativeai 套件")
        
        # 根據版本初始化客戶端
        if GENAI_NEW_VERSION:
            # 新版本 API：直接建立 client
            self.client = genai.Client(api_key=self.api_key)
            self.GENAI_NEW_VERSION = True
            print(f"✅ Gemini 客戶端初始化成功（新版本），模型：{model_name}")
        else:
            # 舊版本 API：需 configure
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model_name)
            self.GENAI_NEW_VERSION = False
            print(f"✅ Gemini 客戶端初始化成功（舊版本），模型：{model_name}")
    
    def analyze_image(self, image: Image.Image, prompt: str) -> str:
        """傳送圖片與提示詞，回傳 AI 回覆文字"""
        for attempt in range(self.max_retries):
            try:
                if self.GENAI_NEW_VERSION:
                    response = self.client.models.generate_content(
                        model=f"models/{self.model_name}",
                        contents=[prompt, image]
                    )
                    text = response.text if hasattr(response, 'text') else str(response)
                else:
                    response = self.model.generate_content([prompt, image])
                    text = getattr(response, 'text', str(response))
                return text
            except Exception as e:
                err = str(e)
                print(f"⚠️ Gemini API 錯誤 (attempt {attempt+1}/{self.max_retries}): {err}")
                
                # 重試策略：429（配額限制）/503（服務不可用）等待後重試
                if "429" in err or "Resource exhausted" in err or "503" in err or "UNAVAILABLE" in err:
                    wait = 2 ** attempt if "429" in err else 5
                    print(f"⏳ 等待 {wait} 秒後重試...")
                    time.sleep(wait)
                    continue
                else:
                    # 其他錯誤（如 404 model not found）直接拋出
                    raise e
        
        raise RuntimeError(f"❌ Gemini API 呼叫失敗，已重試 {self.max_retries} 次")
    
    def analyze_text(self, text: str) -> str:
        """純文字分析（保留功能）"""
        for attempt in range(self.max_retries):
            try:
                if self.GENAI_NEW_VERSION:
                    response = self.client.models.generate_content(
                        model=f"models/{self.model_name}",
                        contents=text
                    )
                    return response.text if hasattr(response, 'text') else str(response)
                else:
                    response = self.model.generate_content(text)
                    return getattr(response, 'text', str(response))
            except Exception as e:
                err = str(e)
                print(f"⚠️ Gemini API 錯誤 (attempt {attempt+1}): {err}")
                if "429" in err or "Resource exhausted" in err or "503" in err or "UNAVAILABLE" in err:
                    wait = 2 ** attempt if "429" in err else 5
                    time.sleep(wait)
                    continue
                else:
                    raise e
        raise RuntimeError(f"Gemini API 呼叫失敗，已重試 {self.max_retries} 次")