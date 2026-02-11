# -*- coding: utf-8 -*-
"""
音訊處理模組：讀取 WAV、相似度計算（完整保留原始演算法）
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import stft
from fastdtw import fastdtw

# 嘗試導入 librosa（若無則降級）
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

def read_wav(path: str):
    """讀取 WAV 檔案，轉為 float64 並合併立體聲"""
    sr, data = wavfile.read(path)
    data = data.astype(np.float64)
    if data.ndim > 1:
        data = np.mean(data, axis=1)
    return sr, data

class SimilarityCalculator:
    """音訊相似度計算器（與原始程式完全相同）"""
    
    @staticmethod
    def mel_cosine_similarity(y1: np.ndarray, sr1: int, y2: np.ndarray, sr2: int) -> float:
        """Mel 頻譜餘弦相似度"""
        try:
            target_sr = 22050
            if LIBROSA_AVAILABLE:
                if sr1 != target_sr:
                    y1r = librosa.resample(y1.astype(np.float32), orig_sr=sr1, target_sr=target_sr)
                else:
                    y1r = y1.astype(np.float32)
                    
                if sr2 != target_sr:
                    y2r = librosa.resample(y2.astype(np.float32), orig_sr=sr2, target_sr=target_sr)
                else:
                    y2r = y2.astype(np.float32)
                    
                S1 = librosa.feature.melspectrogram(y=y1r, sr=target_sr, n_mels=64, hop_length=512)
                S2 = librosa.feature.melspectrogram(y=y2r, sr=target_sr, n_mels=64, hop_length=512)
                M1 = np.log1p(S1).mean(axis=1)
                M2 = np.log1p(S2).mean(axis=1)
            else:
                f1, t1, Z1 = stft(y1, fs=sr1, nperseg=1024)
                f2, t2, Z2 = stft(y2, fs=sr2, nperseg=1024)
                M1 = np.log1p(np.abs(Z1)).mean(axis=1)[:64]
                M2 = np.log1p(np.abs(Z2)).mean(axis=1)[:64]
                
            num = np.dot(M1, M2)
            den = (np.linalg.norm(M1) * np.linalg.norm(M2) + 1e-9)
            cos = num / den
            sim = (cos + 1) / 2
            return float(sim)
        except Exception as e:
            print(f"[相似度計算錯誤] {e}")
            return 0.0
    
    @staticmethod
    def mfcc_dtw_similarity(y1: np.ndarray, sr1: int, y2: np.ndarray, sr2: int) -> float:
        """MFCC + DTW 相似度"""
        try:
            target_sr = 22050
            if LIBROSA_AVAILABLE:
                if sr1 != target_sr:
                    y1r = librosa.resample(y1.astype(np.float32), orig_sr=sr1, target_sr=target_sr)
                else:
                    y1r = y1.astype(np.float32)
                    
                if sr2 != target_sr:
                    y2r = librosa.resample(y2.astype(np.float32), orig_sr=sr2, target_sr=target_sr)
                else:
                    y2r = y2.astype(np.float32)
                    
                mf1 = librosa.feature.mfcc(y=y1r, sr=target_sr, n_mfcc=13)
                mf2 = librosa.feature.mfcc(y=y2r, sr=target_sr, n_mfcc=13)
            else:
                f1, t1, Z1 = stft(y1, fs=sr1, nperseg=1024)
                f2, t2, Z2 = stft(y2, fs=sr2, nperseg=1024)
                mf1 = np.abs(Z1)[:13, :]
                mf2 = np.abs(Z2)[:13, :]
                
            seq1 = [tuple(col) for col in mf1.T]
            seq2 = [tuple(col) for col in mf2.T]
            distance, _ = fastdtw(seq1, seq2, dist=lambda x, y: np.linalg.norm(np.array(x) - np.array(y)))
            norm = max(len(seq1), len(seq2))
            sim = 1.0 / (1.0 + distance / (norm * 50.0))
            return float(sim)
        except Exception as e:
            print(f"[相似度計算錯誤] {e}")
            return 0.0
    
    @staticmethod
    def raw_segment_distance(y1: np.ndarray, y2: np.ndarray) -> float:
        """原始分段距離（越小越相似）"""
        try:
            min_len = min(len(y1), len(y2))
            if min_len <= 0:
                return float('inf')
                
            step = max(256, min_len // 2000)
            total = 0.0
            count = 0
            
            for i in range(0, min_len, step):
                seg1 = y1[i:i+step]
                seg2 = y2[i:i+step]
                L = min(len(seg1), len(seg2))
                if L == 0:
                    continue
                total += np.linalg.norm(seg1[:L] - seg2[:L])
                count += 1
                
            if count == 0:
                return float('inf')
            return float(total / count)
        except Exception as e:
            print(f"[相似度計算錯誤] {e}")
            return float('inf')