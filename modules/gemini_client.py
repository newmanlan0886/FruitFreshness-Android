import os
import time
from PIL import Image

# 嘗試導入 google-genai，失敗時記錄錯誤但不崩潰
try:
    import google.genai as genai
    from google.genai import types
    GENAI_AVAILABLE = True
    print("✅ 成功導入 google.genai")
except ImportError as e:
    GENAI_AVAILABLE = False
    print(f"❌ 無法導入 google.genai: {e}")
    genai = None

class GeminiAnalyzer:
    def __init__(self, api_key: str = None, model_name: str = "gemini-2.5-flash", max_retries: int = 4):
        self.model_name = model_name
        self.max_retries = max_retries
        
        if not api_key:
            raise ValueError("❌ 必須提供 API Key")
        
        if not GENAI_AVAILABLE:
            raise ImportError("❌ google.genai 套件未安裝或無法載入")
        
        try:
            self.client = genai.Client(api_key=api_key)
            print(f"✅ Gemini 客戶端初始化成功")
        except Exception as e:
            raise RuntimeError(f"❌ Gemini 客戶端初始化失敗: {e}")
    
    def analyze_image(self, image: Image.Image, prompt: str) -> str:
        """分析圖片"""
        for attempt in range(self.max_retries):
            try:
                response = self.client.models.generate_content(
                    model=f"models/{self.model_name}",
                    contents=[prompt, image]
                )
                return response.text if hasattr(response, 'text') else str(response)
            except Exception as e:
                print(f"⚠️ API 錯誤 (attempt {attempt+1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise