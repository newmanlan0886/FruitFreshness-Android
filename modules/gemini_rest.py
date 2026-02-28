# modules/gemini_rest.py
"""
Gemini REST API 客戶端 - 不依賴 google-genai 套件
"""
import requests
import base64
import json
import io
from PIL import Image

class GeminiRESTClient:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://generativelanguage.googleapis.com/v1/models"
        
    def analyze_image(self, image: Image.Image, prompt: str) -> str:
        """分析圖片並回傳結果"""
        try:
            # 將 PIL Image 轉為 base64
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # 準備請求資料
            url = f"{self.base_url}/{self.model_name}:generateContent?key={self.api_key}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": img_str
                            }
                        }
                    ]
                }]
            }
            
            # 發送請求
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                # 解析回應
                try:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    return text
                except (KeyError, IndexError):
                    return f"無法解析回應：{result}"
            else:
                return f"API 錯誤 ({response.status_code}): {response.text}"
                
        except Exception as e:
            return f"分析失敗：{str(e)}"
    
    def analyze_text(self, text: str) -> str:
        """純文字分析"""
        try:
            url = f"{self.base_url}/{self.model_name}:generateContent?key={self.api_key}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [{
                    "parts": [{"text": text}]
                }]
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                try:
                    return result['candidates'][0]['content']['parts'][0]['text']
                except (KeyError, IndexError):
                    return f"無法解析回應：{result}"
            else:
                return f"API 錯誤 ({response.status_code}): {response.text}"
                
        except Exception as e:
            return f"分析失敗：{str(e)}"