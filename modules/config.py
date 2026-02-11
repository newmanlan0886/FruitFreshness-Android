# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class AppConfig:
    """應用程式配置（Android 移植版保留原始設定）"""
    SAMPLE_RATE: int = 44100
    RECORD_SECONDS: int = 5
    MAX_WORKERS: int = 1
    MAX_RETRIES: int = 4
    MAX_CAMERA_SCAN: int = 4
    PREVIEW_UPDATE_DELAY: int = 33
    THUMBNAIL_SIZE: Tuple[int, int] = (120, 120)
    PREVIEW_SIZE: Tuple[int, int] = (640, 360)
    IMAGE_CAMERA_PREVIEW_SIZE: Tuple[int, int] = (280, 160)
    IMAGE_PREVIEW_SIZE: Tuple[int, int] = (300, 250)
    RESOLUTIONS: List[Tuple[int, int]] = field(default_factory=lambda: [
        (320, 240), (640, 360), (480, 360), (800, 600), (1280, 720)
    ])

class ColorScheme:
    """配色方案（原 Tkinter 顏色保留，Kivy 中可另行定義）"""
    BLOCK_COLORS = {
        '狀態區塊': '#fff3e0',
        '音訊區塊': "#f5eee8",
        '比對區塊': "#f5eee8",
        '攝影機區塊': "#f5eee8",
        'AI分析區塊': '#f5eee8',
        '預覽區塊': "#fff8e1",
        '結果區塊': '#fff8e1'
    }
    TEXT_COLORS = {
        '深色文字': "#000000",
        '深色文字alt': "#000000",
        '中色文字': "#000000",
        '淺色文字': "#000000"
    }
    BUTTON_COLORS = {
        '主要按鈕': "#d73f3f",
        '次要按鈕': '#ff9800',
        '危險按鈕': '#f44336',
        '成功按鈕': '#4caf50',
        '警告按鈕': "#ed6035"
    }

    @classmethod
    def get_block_color(cls, block_name: str) -> str:
        return cls.BLOCK_COLORS.get(block_name, '#ffffff')
    
    @classmethod
    def get_text_color(cls, text_type: str = '深色文字') -> str:
        return cls.TEXT_COLORS.get(text_type, '#333333')
    
    @classmethod
    def get_button_color(cls, button_type: str = '主要按鈕') -> str:
        return cls.BUTTON_COLORS.get(button_type, '#2196f3')