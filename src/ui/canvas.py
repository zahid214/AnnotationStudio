"""
Canvas widget for drawing and editing annotations
"""

from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QImage
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
import numpy as np
from src.models.annotation import (
    Annotation, BoundingBox, Polygon, Point, AnnotationType
)

class AnnotationCanvas(QWidget):
    
    annotation_created = pyqtSignal(Annotation)
    annotation_updated = pyqtSignal(Annotation)
    
    def __init__(self):
        super().__init__()
        self.image = None
        self.pixmap = None
        self.annotations = []
        self.current_annotation = None
        self.drawing = False
        self.start_point = None
        self.current_tool = AnnotationType.RECTANGLE
        self.current_label = "object"
        self.current_color = QColor(255, 0, 0)
        self.selected_annotation = None
        self.tool_colors = {
            AnnotationType.RECTANGLE: QColor(255, 0, 0, 100),
            AnnotationType.POLYGON: QColor(0, 255, 0, 100),
            AnnotationType.CIRCLE: QColor(0, 0, 255, 100),
            AnnotationType.LINE: QColor(255, 255, 0, 100)
        }
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        
    def set_image(self, pixmap: QPixmap):
        """Set the image to annotate"""
        self.pixmap = pixmap
        self.setFixedSize(pixmap.size())
        self.update()
    
    def set_tool(self, tool: AnnotationType):
        """Set the annotation tool"""
        self.current_tool = tool
    
    def set_label(self, label: str):
        """Set the current label"""
        self.current_label = label
    
    def set_color(self, color: QColor):
        """Set the drawing color"""
        self.current_color = color
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if self.pixmap is None:
            return
        
        self.drawing = True
        self.start_point = event.pos()
        
        if self.current_tool == AnnotationType.RECTANGLE:
            self.current_annotation = Annotation(
                id=f"ann_{len(self.annotations)}",
                annotation_type=AnnotationType.RECTANGLE,
                label=self.current_label,
                color=self.current_color.name()
            )
        elif self.current_tool == AnnotationType.POLYGON:
            if self.current_annotation is None:
                self.current_annotation = Annotation(
                    id=f"ann_{len(self.annotations)}",
                    annotation_type=AnnotationType.POLYGON,
                    label=self.current_label,
                    polygon=Polygon([]),
                    color=self.current_color.name()
                )
            # Add point to polygon
            self.current_annotation.polygon.points.append(
                Point(event.pos().x(), event.pos().y())
            )
    
    def mouseMoveEvent(self, event):
        """Handle mouse move"""
        if not self.drawing or self.pixmap is None:
            return
        
        if self.current_tool == AnnotationType.RECTANGLE and self.current_annotation:
            # Update bbox in real-time
            x1, y1 = self.start_point.x(), self.start_point.y()
            x2, y2 = event.pos().x(), event.pos().y()
            
            x = min(x1, x2)
            y = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            
            self.current_annotation.bbox = BoundingBox(x, y, width, height)
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if not self.drawing or self.pixmap is None:
            return
        
        self.drawing = False
        
        if self.current_tool == AnnotationType.RECTANGLE and self.current_annotation:
            if self.current_annotation.bbox and self.current_annotation.bbox.width > 5:
                self.annotations.append(self.current_annotation)
                self.annotation_created.emit(self.current_annotation)
                self.current_annotation = None
        
        self.update()
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click to finish polygon"""
        if self.current_tool == AnnotationType.POLYGON and self.current_annotation:
            if len(self.current_annotation.polygon.points) > 2:
                self.annotations.append(self.current_annotation)
                self.annotation_created.emit(self.current_annotation)
                self.current_annotation = None
                self.update()
    
    def paintEvent(self, event):
        """Paint the canvas"""
        if self.pixmap is None:
            return
        
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)
        
        # Draw existing annotations
        for ann in self.annotations:
            self._draw_annotation(painter, ann)
        
        # Draw current annotation being drawn
        if self.current_annotation:
            self._draw_annotation(painter, self.current_annotation, preview=True)
    
    def _draw_annotation(self, painter: QPainter, ann: Annotation, preview=False):
        """Draw an annotation on the canvas"""
        color = QColor(ann.color)
        if preview:
            color.setAlpha(100)
        
        pen = QPen(color)
        pen.setWidth(2)
        painter.setPen(pen)
        
        if ann.bbox:
            painter.drawRect(
                int(ann.bbox.x),
                int(ann.bbox.y),
                int(ann.bbox.width),
                int(ann.bbox.height)
            )
            # Draw label text
            painter.drawText(
                int(ann.bbox.x),
                int(ann.bbox.y) - 5,
                ann.label
            )
        
        elif ann.polygon and ann.polygon.points:
            points = [QPoint(int(p.x), int(p.y)) for p in ann.polygon.points]
            painter.drawPolyline(points)
            if len(points) > 2 and not preview:
                painter.drawLine(points[-1], points[0])
    
    def clear_annotations(self):
        """Clear all annotations"""
        self.annotations.clear()
        self.current_annotation = None
        self.update()
    
    def undo(self):
        """Remove last annotation"""
        if self.annotations:
            self.annotations.pop()
            self.update()
    
    def get_annotations(self):
        """Return all annotations"""
        return self.annotations
