"""
Export utilities for various annotation formats
"""

import json
import csv
from typing import List, Dict, Any
from src.models.annotation import (
    Project, ImageData, VideoData, Annotation, 
    ExportFormat, AnnotationType
)
from xml.etree.ElementTree import Element, SubElement, tostring
from pathlib import Path

class ExportManager:
    
    @staticmethod
    def export_yolo(image_data: ImageData, output_path: str):
        """Export annotations in YOLO format"""
        annotations = image_data.annotations
        lines = []
        
        for ann in annotations:
            if ann.bbox:
                # YOLO format: <class_id> <x_center> <y_center> <width> <height> (normalized)
                x_center = (ann.bbox.x + ann.bbox.width / 2) / image_data.width
                y_center = (ann.bbox.y + ann.bbox.height / 2) / image_data.height
                width = ann.bbox.width / image_data.width
                height = ann.bbox.height / image_data.height
                
                class_id = 0  # Can be extended to use label mapping
                lines.append(f"{class_id} {x_center} {y_center} {width} {height}")
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))
    
    @staticmethod
    def export_coco(project: Project, output_path: str):
        """Export annotations in COCO format"""
        coco_data = {
            "info": {
                "description": project.description,
                "version": "1.0",
                "year": 2024
            },
            "licenses": [],
            "images": [],
            "annotations": [],
            "categories": [
                {"id": idx, "name": label, "supercategory": "object"}
                for idx, label in enumerate(project.labels)
            ]
        }
        
        ann_id = 1
        for img_idx, image in enumerate(project.images, 1):
            img_info = {
                "id": img_idx,
                "file_name": image.image_name,
                "height": image.height,
                "width": image.width
            }
            coco_data["images"].append(img_info)
            
            for annotation in image.annotations:
                cat_id = project.labels.index(annotation.label) if annotation.label in project.labels else 0
                
                if annotation.bbox:
                    ann_info = {
                        "id": ann_id,
                        "image_id": img_idx,
                        "category_id": cat_id,
                        "bbox": [annotation.bbox.x, annotation.bbox.y, annotation.bbox.width, annotation.bbox.height],
                        "area": annotation.bbox.width * annotation.bbox.height,
                        "iscrowd": 0
                    }
                    coco_data["annotations"].append(ann_info)
                    ann_id += 1
        
        with open(output_path, 'w') as f:
            json.dump(coco_data, f, indent=2)
    
    @staticmethod
    def export_json(image_data: ImageData, output_path: str):
        """Export annotations in JSON format"""
        data = image_data.to_dict()
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def export_csv(image_data: ImageData, output_path: str):
        """Export annotations in CSV format"""
        rows = []
        for ann in image_data.annotations:
            row = {
                'Label': ann.label,
                'Type': ann.annotation_type.value,
                'Confidence': ann.confidence,
                'Color': ann.color
            }
            if ann.bbox:
                row.update({
                    'X': ann.bbox.x,
                    'Y': ann.bbox.y,
                    'Width': ann.bbox.width,
                    'Height': ann.bbox.height
                })
            rows.append(row)
        
        if rows:
            keys = rows[0].keys()
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(rows)
    
    @staticmethod
    def export_xml(image_data: ImageData, output_path: str):
        """Export annotations in Pascal VOC XML format"""
        root = Element('annotation')
        
        # Add filename
        filename_elem = SubElement(root, 'filename')
        filename_elem.text = image_data.image_name
        
        # Add size
        size_elem = SubElement(root, 'size')
        SubElement(size_elem, 'width').text = str(image_data.width)
        SubElement(size_elem, 'height').text = str(image_data.height)
        SubElement(size_elem, 'depth').text = '3'
        
        # Add objects
        for ann in image_data.annotations:
            if ann.bbox:
                obj_elem = SubElement(root, 'object')
                SubElement(obj_elem, 'name').text = ann.label
                SubElement(obj_elem, 'confidence').text = str(ann.confidence)
                
                bndbox = SubElement(obj_elem, 'bndbox')
                SubElement(bndbox, 'xmin').text = str(int(ann.bbox.x))
                SubElement(bndbox, 'ymin').text = str(int(ann.bbox.y))
                SubElement(bndbox, 'xmax').text = str(int(ann.bbox.x + ann.bbox.width))
                SubElement(bndbox, 'ymax').text = str(int(ann.bbox.y + ann.bbox.height))
        
        tree_str = tostring(root, encoding='unicode')
        with open(output_path, 'w') as f:
            f.write(tree_str)
    
    @staticmethod
    def export(image_data: ImageData, output_path: str, format: ExportFormat):
        """Main export function"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        if format == ExportFormat.YOLO:
            ExportManager.export_yolo(image_data, output_path)
        elif format == ExportFormat.JSON:
            ExportManager.export_json(image_data, output_path)
        elif format == ExportFormat.CSV:
            ExportManager.export_csv(image_data, output_path)
        elif format == ExportFormat.XML or format == ExportFormat.PASCAL_VOC:
            ExportManager.export_xml(image_data, output_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")
