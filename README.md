# 水果新鮮度及成熟度診斷系統（Android 移植版）

本專案是「水果新鮮度及成熟度診斷系統 v6.3.2」的 Android 移植版本，  
**完整保留原始業務邏輯（音訊處理、相似度計算、Gemini 客戶端）**，  
並以 **Kivy 框架重寫使用者介面**，可編譯為獨立 APK 安裝於 Android 裝置。

---

## ✨ 目前已實作功能

- 📸 **攝影機預覽與拍照**（使用 Kivy Camera）
- 🧠 **Gemini AI 圖片分析**：自動辨識水果種類、新鮮度、成熟度，並提供建議
- ⚙️ **模組化設計**：`modules/` 目錄包含完整演算法，易於擴充

---

## 🚧 待開發 / 已知限制

- ❌ 音訊錄製與比對（因 Android 權限與硬體差異暫未移植，但 `audio_processor.py` 已保留完整演算法）
- ❌ 多樣本批次比對
- ❌ 資料夾載入功能
- ⚠️ 使用 OpenCV 的 `CameraManager` 未整合至前端（目前使用 Kivy Camera）

---

## 📦 建置 APK（需要 Linux 或 WSL）

1. **安裝 Buildozer**  
   ```bash
   pip install buildozer