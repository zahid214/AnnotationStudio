"""
Core annotation models and data structures
"""

from dataclasses import dataclass, asdict
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
import json
from datetime import datetime

class AnnotationType(Enum):
    RECTANGLE = "rectangle"
    POLYGON = "polygon"
    CIRCLE = "circle"
    LINE = "line"

class ExportFormat(Enum):
    YOLO = "yolo"
    COCO = "coco"
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    PASCAL_VOC = "pascal_voc"

@dataclass
class Point:
    x: float
    y: float
    
    def to_dict(self):
        return {"x": self.x, "y": self.y}

@dataclass
class BoundingBox:
    x: float
    y: float
    width: float
    height: float
    
    def to_dict(self):
        return {"x": self.x, "y": self.y, "width": self.width, "height": self.height}

@dataclass
class Polygon:
    points: List[Point]
    
    def to_dict(self):
        return {"points": [p.to_dict() for p in self.points]}

@dataclass
class Annotation:
    id: str
    annotation_type: AnnotationType
    label: str
    confidence: float = 1.0
    bbox: Optional[BoundingBox] = None
    polygon: Optional[Polygon] = None
    color: str = "#FF0000"
    metadata: Dict[str, Any] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self):
        data = {
            "id": self.id,
            "type": self.annotation_type.value,
            "label": self.label,
            "confidence": self.confidence,
            "color": self.color,
            "created_at": self.created_at,
            "metadata": self.metadata
        }
        if self.bbox:
            data["bbox"] = self.bbox.to_dict()
        if self.polygon:
            data["polygon"] = self.polygon.to_dict()
        return data

@dataclass
class ImageData:
    file_path: str
    image_name: str
    width: int
    height: int
    annotations: List[Annotation] = None
    metadata: Dict[str, Any] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.annotations is None:
            self.annotations = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def add_annotation(self, annotation: Annotation):
        self.annotations.append(annotation)
    
    def to_dict(self):
        return {
            "file_path": self.file_path,
            "image_name": self.image_name,
            "width": self.width,
            "height": self.height,
            "annotations": [a.to_dict() for a in self.annotations],
            "metadata": self.metadata,
            "created_at": self.created_at
        }

@dataclass
class VideoData:
    file_path: str
    video_name: str
    frame_count: int
    fps: float
    width: int
    height: int
    annotations: Dict[int, List[Annotation]] = None  # frame_number -> annotations
    metadata: Dict[str, Any] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.annotations is None:
            self.annotations = {}
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def add_annotation(self, frame_number: int, annotation: Annotation):
        if frame_number not in self.annotations:
            self.annotations[frame_number] = []
        self.annotations[frame_number].append(annotation)
    
    def to_dict(self):
        return {
            "file_path": self.file_path,
            "video_name": self.video_name,
            "frame_count": self.frame_count,
            "fps": self.fps,
            "width": self.width,
            "height": self.height,
            "annotations": {
                str(k): [a.to_dict() for a in v] 
                for k, v in self.annotations.items()
            },
            "metadata": self.metadata,
            "created_at": self.created_at
        }

@dataclass
class Project:
    project_name: str
    project_id: str
    description: str = ""
    labels: List[str] = None
    images: List[ImageData] = None
    videos: List[VideoData] = None
    metadata: Dict[str, Any] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []
        if self.images is None:
            self.images = []
        if self.videos is None:
            self.videos = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def add_image(self, image: ImageData):
        self.images.append(image)
    
    def add_video(self, video: VideoData):
        self.videos.append(video)
    
    def add_label(self, label: str):
        if label not in self.labels:
            self.labels.append(label)
    
    def to_dict(self):
        return {
            "project_name": self.project_name,
            "project_id": self.project_id,
            "description": self.description,
            "labels": self.labels,
            "images": [img.to_dict() for img in self.images],
            "videos": [vid.to_dict() for vid in self.videos],
            "metadata": self.metadata,
            "created_at": self.created_at
        }
