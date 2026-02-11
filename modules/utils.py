# -*- coding: utf-8 -*-
"""
共用工具函式
"""
import time
import os

def timestamp_str(fmt: str = "%Y%m%d_%H%M%S") -> str:
    """產生時間戳字串"""
    return time.strftime(fmt)

def ensure_dir(path: str) -> str:
    """確保目錄存在，若不存在則建立"""
    os.makedirs(path, exist_ok=True)
    return path