"""
音声ファイル処理モジュール
波形データ生成、音声情報取得を担当
"""

import numpy as np
from pathlib import Path
from pydub import AudioSegment


class AudioHandler:
    """音声ファイルのハンドラー"""
    
    def __init__(self, audio_path: str):
        """
        Args:
            audio_path: 音声ファイルのパス
        """
        self.audio_path = Path(audio_path)
        self._audio = None
        self._samples = None
    
    @property
    def audio(self) -> AudioSegment:
        """AudioSegmentのキャッシュ"""
        if self._audio is None:
            self._audio = AudioSegment.from_file(str(self.audio_path))
        return self._audio
    
    def get_info(self) -> dict:
        """音声ファイルの情報を取得"""
        audio = self.audio
        return {
            'duration': len(audio) / 1000.0,  # 秒単位
            'sample_rate': audio.frame_rate,
            'channels': audio.channels,
            'sample_width': audio.sample_width,  # バイト単位
            'file_name': self.audio_path.name,
            'file_size': self.audio_path.stat().st_size,
        }
    
    def get_samples(self) -> np.ndarray:
        """音声をnumpy配列として取得"""
        if self._samples is None:
            audio = self.audio
            samples = np.array(audio.get_array_of_samples())
            
            # ステレオの場合はモノラルに変換
            if audio.channels == 2:
                samples = samples.reshape((-1, 2)).mean(axis=1)
            
            # 正規化（-1.0 ~ 1.0）
            max_val = 2 ** (audio.sample_width * 8 - 1)
            self._samples = samples / max_val
        
        return self._samples
    
    def get_waveform_data(self, num_points: int = 2000) -> dict:
        """
        波形表示用のダウンサンプリングされたデータを取得
        
        Args:
            num_points: 出力するデータポイント数
            
        Returns:
            波形データ（min/max値のペア）
        """
        samples = self.get_samples()
        audio_info = self.get_info()
        
        total_samples = len(samples)
        
        if total_samples <= num_points:
            # サンプル数が少ない場合はそのまま返す
            return {
                'data': samples.tolist(),
                'duration': audio_info['duration'],
                'sample_rate': audio_info['sample_rate'],
                'num_points': len(samples)
            }
        
        # ダウンサンプリング（各ブロックの最大・最小値を取得）
        samples_per_point = total_samples // num_points
        waveform_data = []
        
        for i in range(num_points):
            start = i * samples_per_point
            end = min(start + samples_per_point, total_samples)
            chunk = samples[start:end]
            
            if len(chunk) > 0:
                waveform_data.append({
                    'min': float(chunk.min()),
                    'max': float(chunk.max())
                })
        
        return {
            'data': waveform_data,
            'duration': audio_info['duration'],
            'sample_rate': audio_info['sample_rate'],
            'num_points': num_points
        }
    
    def get_peaks(self, start_time: float, end_time: float, num_points: int = 500) -> dict:
        """
        指定区間の詳細な波形データを取得
        
        Args:
            start_time: 開始時間（秒）
            end_time: 終了時間（秒）
            num_points: 出力するデータポイント数
            
        Returns:
            波形データ
        """
        audio = self.audio
        samples = self.get_samples()
        sample_rate = audio.frame_rate
        
        start_sample = int(start_time * sample_rate)
        end_sample = int(end_time * sample_rate)
        
        # 範囲チェック
        start_sample = max(0, start_sample)
        end_sample = min(len(samples), end_sample)
        
        chunk = samples[start_sample:end_sample]
        
        if len(chunk) == 0:
            return {
                'data': [],
                'start_time': start_time,
                'end_time': end_time
            }
        
        total_samples = len(chunk)
        
        if total_samples <= num_points:
            return {
                'data': chunk.tolist(),
                'start_time': start_time,
                'end_time': end_time
            }
        
        samples_per_point = total_samples // num_points
        waveform_data = []
        
        for i in range(num_points):
            start = i * samples_per_point
            end = min(start + samples_per_point, total_samples)
            sub_chunk = chunk[start:end]
            
            if len(sub_chunk) > 0:
                waveform_data.append({
                    'min': float(sub_chunk.min()),
                    'max': float(sub_chunk.max())
                })
        
        return {
            'data': waveform_data,
            'start_time': start_time,
            'end_time': end_time
        }
