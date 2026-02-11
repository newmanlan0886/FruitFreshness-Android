# -*- coding: utf-8 -*-
"""
Google Gemini API 客戶端（支援新舊版本，含重試機制）
"""
import os
import time
from typing import Optional
from dotenv import load_dotenv
from PIL import Image

# 載入環境變數
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "")

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
    """封裝 Gemini API 呼叫"""
    def __init__(self, model_name: str = "gemini-2.5-flash", max_retries: int = 4):
        self.model_name = model_name
        self.max_retries = max_retries
        self.client = None
        if genai is None:
            raise ImportError("未安裝 google-genai 或 google-generativeai")
        
        if GENAI_NEW_VERSION:
            # 新版本 API：直接建立 client
            self.client = genai.Client(api_key=API_KEY) if API_KEY else genai.Client()
        else:
            # 舊版本 API：需 configure
            if API_KEY:
                genai.configure(api_key=API_KEY)
            self.model = genai.GenerativeModel(model_name)
    
    def analyze_image(self, image: Image.Image, prompt: str) -> str:
        """傳送圖片與提示詞，回傳 AI 回覆文字"""
        for attempt in range(self.max_retries):
            try:
                if GENAI_NEW_VERSION:
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
                print(f"Gemini API 錯誤 (attempt {attempt+1}): {err}")
                # 重試策略：429/503 等待後重試，其餘直接中斷
                if "429" in err or "Resource exhausted" in err or "503" in err or "UNAVAILABLE" in err:
                    wait = 2 ** attempt if "429" in err else 5
                    time.sleep(wait)
                    continue
                else:
                    # 其他錯誤（如 404 model not found）不重試
                    raise e
        raise RuntimeError(f"Gemini API 呼叫失敗，已重試 {self.max_retries} 次")