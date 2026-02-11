# -*- coding: utf-8 -*-
"""
攝影機管理器（保留原始 OpenCV 實作，Android 上建議使用 Kivy Camera）
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional
from modules.config import AppConfig

class CameraManager:
    """攝影機管理器（與原始桌面版相同）"""
    def __init__(self):
        self.cap: Optional[cv2.VideoCapture] = None
        self.preview_running: bool = False
        self.current_frame: Optional[np.ndarray] = None
    
    def scan_cameras(self) -> List[str]:
        found = []
        config = AppConfig()
        scan_range = min(config.MAX_CAMERA_SCAN, 5)
        for i in range(scan_range):
            try:
                cap = cv2.VideoCapture(i)
                if cap is None or not cap.isOpened():
                    continue
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
                ret, frame = cap.read()
                if ret and frame is not None:
                    found.append(str(i))
                cap.release()
            except Exception:
                if i == 0:
                    pass
        return found if found else ["0"]
    
    def test_connection(self, camera_index: int) -> Tuple[bool, str]:
        try:
            cap = cv2.VideoCapture(camera_index)
            if not cap.isOpened():
                return False, "攝影機無法開啟"
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            success_count = 0
            for _ in range(3):
                ret, frame = cap.read()
                if ret and frame is not None:
                    success_count += 1
            cap.release()
            if success_count >= 3:
                return True, "攝影機連接正常"
            else:
                return False, f"只能讀取 {success_count}/3 幀"
        except Exception as e:
            return False, f"連接測試錯誤：{str(e)[:100]}"
    
    def start_preview(self, camera_index: int) -> bool:
        try:
            self.stop_preview()
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                return False
            config = AppConfig()
            for width, height in config.RESOLUTIONS:
                if self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width) and \
                   self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height):
                    break
            self.preview_running = True
            return True
        except Exception:
            return False
    
    def stop_preview(self):
        self.preview_running = False
        if self.cap:
            try:
                self.cap.release()
            except:
                pass
            self.cap = None
        self.current_frame = None
    
    def get_frame(self) -> Optional[np.ndarray]:
        if not self.preview_running or self.cap is None:
            return None
        try:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.current_frame = frame
                return frame
        except Exception:
            pass
        return None