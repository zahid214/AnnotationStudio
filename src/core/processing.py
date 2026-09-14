"""
Image and Video processing utilities
"""

import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional

class ImageProcessor:
    
    @staticmethod
    def load_image(image_path: str) -> Tuple[np.ndarray, Tuple[int, int]]:
        """Load image and return it with dimensions"""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        height, width = image.shape[:2]
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), (width, height)
    
    @staticmethod
    def resize_image(image: np.ndarray, max_width: int = 1024, max_height: int = 768) -> np.ndarray:
        """Resize image to fit within max dimensions while maintaining aspect ratio"""
        height, width = image.shape[:2]
        
        if width <= max_width and height <= max_height:
            return image
        
        ratio = min(max_width / width, max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    @staticmethod
    def save_image(image: np.ndarray, output_path: str):
        """Save image in RGB format"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, image_bgr)

class VideoProcessor:
    
    @staticmethod
    def load_video_info(video_path: str) -> dict:
        """Get video information"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not load video: {video_path}")
        
        info = {
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'codec': int(cap.get(cv2.CAP_PROP_FOURCC))
        }
        cap.release()
        return info
    
    @staticmethod
    def get_frame(video_path: str, frame_number: int) -> np.ndarray:
        """Extract specific frame from video"""
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise ValueError(f"Could not read frame {frame_number}")
        
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    @staticmethod
    def extract_frames(video_path: str, output_dir: str, interval: int = 1):
        """Extract frames from video at specified interval"""
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        saved_frames = []
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % interval == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                output_path = f"{output_dir}/frame_{frame_count:06d}.jpg"
                ImageProcessor.save_image(frame_rgb, output_path)
                saved_frames.append(output_path)
            
            frame_count += 1
        
        cap.release()
        return saved_frames

class FileValidator:
    
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
    SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'}
    
    @staticmethod
    def is_image_file(file_path: str) -> bool:
        """Check if file is a supported image format"""
        return Path(file_path).suffix.lower() in FileValidator.SUPPORTED_IMAGE_FORMATS
    
    @staticmethod
    def is_video_file(file_path: str) -> bool:
        """Check if file is a supported video format"""
        return Path(file_path).suffix.lower() in FileValidator.SUPPORTED_VIDEO_FORMATS
    
    @staticmethod
    def validate_file(file_path: str) -> bool:
        """Check if file exists and is supported"""
        path = Path(file_path)
        if not path.exists():
            return False
        return FileValidator.is_image_file(file_path) or FileValidator.is_video_file(file_path)
