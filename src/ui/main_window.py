"""
Main application window with beautiful UI
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolBar,
    QPushButton, QLabel, QComboBox, QSpinBox, QFileDialog,
    QListWidget, QListWidgetItem, QColorDialog, QTabWidget,
    QScrollArea, QFrame, QStatusBar, QSplitter, QMenu, QMessageBox,
    QDialog, QLineEdit, QTextEdit
)
from PyQt6.QtGui import QIcon, QColor, QPixmap, QFont
from PyQt6.QtCore import Qt, pyqtSlot, QSize
from src.ui.canvas import AnnotationCanvas
from src.core.processing import ImageProcessor, VideoProcessor, FileValidator
from src.models.annotation import ImageData, AnnotationType, ExportFormat
from src.core.export import ExportManager
from pathlib import Path
import uuid

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AnnotationStudio - Professional Data Labeling")
        self.setGeometry(100, 100, 1600, 900)
        self.setStyleSheet(self.get_stylesheet())
        
        # Data
        self.current_image = None
        self.current_image_path = None
        self.canvas = None
        self.labels = []
        
        # Setup UI
        self.setup_ui()
        self.setWindowIcon(self.create_icon())
    
    def setup_ui(self):
        """Setup the main UI"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left sidebar - File browser and tools
        left_panel = self.create_left_panel()
        
        # Center - Canvas
        center_panel = self.create_center_panel()
        
        # Right sidebar - Properties and annotations list
        right_panel = self.create_right_panel()
        
        # Add to main layout with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 1)
        
        main_layout.addWidget(splitter)
        
        # Toolbar
        self.create_toolbar()
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_left_panel(self) -> QFrame:
        """Create left panel with file browser and tools"""
        panel = QFrame()
        panel.setStyleSheet("QFrame { background-color: #1a1f3a; border-right: 1px solid #333; }")
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Tools & Files")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #fff;")
        layout.addWidget(title)
        
        # Upload buttons
        upload_image_btn = QPushButton("📁 Load Image")
        upload_image_btn.clicked.connect(self.load_image)
        upload_image_btn.setStyleSheet(self.get_button_style())
        layout.addWidget(upload_image_btn)
        
        upload_video_btn = QPushButton("🎬 Load Video")
        upload_video_btn.clicked.connect(self.load_video)
        upload_video_btn.setStyleSheet(self.get_button_style())
        layout.addWidget(upload_video_btn)
        
        # Separator
        sep = QFrame()
        sep.setStyleSheet("background-color: #333;")
        sep.setFixedHeight(2)
        layout.addWidget(sep)
        
        # Annotation tools
        tool_title = QLabel("Annotation Tools")
        tool_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        tool_title.setStyleSheet("color: #a0aec0; margin-top: 15px;")
        layout.addWidget(tool_title)
        
        # Rectangle tool
        rect_btn = QPushButton("▭ Rectangle")
        rect_btn.clicked.connect(lambda: self.canvas.set_tool(AnnotationType.RECTANGLE) if self.canvas else None)
        rect_btn.setStyleSheet(self.get_button_style("primary"))
        layout.addWidget(rect_btn)
        
        # Polygon tool
        poly_btn = QPushButton("◇ Polygon (Free Hand)")
        poly_btn.clicked.connect(lambda: self.canvas.set_tool(AnnotationType.POLYGON) if self.canvas else None)
        poly_btn.setStyleSheet(self.get_button_style())
        layout.addWidget(poly_btn)
        
        # Circle tool
        circle_btn = QPushButton("● Circle")
        circle_btn.clicked.connect(lambda: self.canvas.set_tool(AnnotationType.CIRCLE) if self.canvas else None)
        circle_btn.setStyleSheet(self.get_button_style())
        layout.addWidget(circle_btn)
        
        # Separator
        sep2 = QFrame()
        sep2.setStyleSheet("background-color: #333;")
        sep2.setFixedHeight(2)
        layout.addWidget(sep2)
        
        # Actions
        action_title = QLabel("Actions")
        action_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        action_title.setStyleSheet("color: #a0aec0; margin-top: 15px;")
        layout.addWidget(action_title)
        
        undo_btn = QPushButton("↶ Undo")
        undo_btn.clicked.connect(self.undo_annotation)
        undo_btn.setStyleSheet(self.get_button_style())
        layout.addWidget(undo_btn)
        
        clear_btn = QPushButton("🗑 Clear All")
        clear_btn.clicked.connect(self.clear_annotations)
        clear_btn.setStyleSheet(self.get_button_style("danger"))
        layout.addWidget(clear_btn)
        
        layout.addStretch()
        return panel
    
    def create_center_panel(self) -> QFrame:
        """Create center panel with canvas"""
        panel = QFrame()
        panel.setStyleSheet("QFrame { background-color: #0f172a; }")
        layout = QVBoxLayout(panel)
        
        # Canvas
        scroll = QScrollArea()
        scroll.setStyleSheet("QScrollArea { border: none; }")
        self.canvas = AnnotationCanvas()
        scroll.setWidget(self.canvas)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        return panel
    
    def create_right_panel(self) -> QFrame:
        """Create right panel with properties and annotations"""
        panel = QFrame()
        panel.setStyleSheet("QFrame { background-color: #1a1f3a; border-left: 1px solid #333; }")
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Properties")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #fff;")
        layout.addWidget(title)
        
        # Label selector
        label_title = QLabel("Label")
        label_title.setStyleSheet("color: #a0aec0;")
        layout.addWidget(label_title)
        
        self.label_combo = QComboBox()
        self.label_combo.addItems(["person", "car", "bicycle", "building"])
        self.label_combo.currentTextChanged.connect(self.on_label_changed)
        self.label_combo.setStyleSheet(self.get_input_style())
        layout.addWidget(self.label_combo)
        
        # Color picker
        color_title = QLabel("Color")
        color_title.setStyleSheet("color: #a0aec0;")
        layout.addWidget(color_title)
        
        color_btn = QPushButton("🎨 Pick Color")
        color_btn.clicked.connect(self.pick_color)
        color_btn.setStyleSheet(self.get_button_style("secondary"))
        layout.addWidget(color_btn)
        
        # Confidence
        conf_title = QLabel("Confidence")
        conf_title.setStyleSheet("color: #a0aec0;")
        layout.addWidget(conf_title)
        
        self.confidence_spin = QSpinBox()
        self.confidence_spin.setRange(0, 100)
        self.confidence_spin.setValue(100)
        self.confidence_spin.setSuffix("%")
        self.confidence_spin.setStyleSheet(self.get_input_style())
        layout.addWidget(self.confidence_spin)
        
        # Separator
        sep = QFrame()
        sep.setStyleSheet("background-color: #333;")
        sep.setFixedHeight(2)
        layout.addWidget(sep)
        
        # Annotations list
        ann_title = QLabel("Annotations")
        ann_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        ann_title.setStyleSheet("color: #fff; margin-top: 15px;")
        layout.addWidget(ann_title)
        
        self.annotations_list = QListWidget()
        self.annotations_list.setStyleSheet(self.get_list_style())
        layout.addWidget(self.annotations_list)
        
        layout.addStretch()
        return panel
    
    def create_toolbar(self):
        """Create application toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setStyleSheet(self.get_toolbar_style())
        self.addToolBar(toolbar)
        
        # Export button
        export_menu = QMenu()
        export_menu.setStyleSheet(self.get_menu_style())
        
        yolo_action = export_menu.addAction("📊 YOLO Format")
        yolo_action.triggered.connect(self.export_yolo)
        
        json_action = export_menu.addAction("📄 JSON")
        json_action.triggered.connect(self.export_json)
        
        csv_action = export_menu.addAction("📋 CSV")
        csv_action.triggered.connect(self.export_csv)
        
        xml_action = export_menu.addAction("🏷 XML/Pascal VOC")
        xml_action.triggered.connect(self.export_xml)
        
        export_btn = QPushButton("💾 Export")
        export_btn.setMenu(export_menu)
        export_btn.setStyleSheet(self.get_button_style("success"))
        toolbar.addWidget(export_btn)
        
        toolbar.addSeparator()
        
        # About button
        about_btn = QPushButton("ℹ About")
        about_btn.clicked.connect(self.show_about)
        about_btn.setStyleSheet(self.get_button_style())
        toolbar.addWidget(about_btn)
    
    def load_image(self):
        """Load an image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", 
            "Images (*.jpg *.jpeg *.png *.bmp *.tiff);;All Files (*)"
        )
        
        if file_path and FileValidator.is_image_file(file_path):
            try:
                image, dims = ImageProcessor.load_image(file_path)
                resized = ImageProcessor.resize_image(image)
                
                pixmap = QPixmap()
                height, width = resized.shape[:2]
                bytes_per_line = 3 * width
                q_image = self.create_q_image_from_array(resized)
                pixmap = QPixmap.fromImage(q_image)
                
                self.current_image = resized
                self.current_image_path = file_path
                self.canvas.set_image(pixmap)
                
                self.statusBar().showMessage(f"Loaded: {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
    
    def load_video(self):
        """Load a video file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Video", "",
            "Videos (*.mp4 *.avi *.mov *.mkv);;All Files (*)"
        )
        
        if file_path and FileValidator.is_video_file(file_path):
            QMessageBox.information(self, "Video Support", 
                                   "Video frame extraction coming soon!")
    
    def on_label_changed(self, label: str):
        """Handle label change"""
        if self.canvas:
            self.canvas.set_label(label)
    
    def pick_color(self):
        """Open color picker"""
        color = QColorDialog.getColor()
        if color.isValid():
            if self.canvas:
                self.canvas.set_color(color)
    
    def undo_annotation(self):
        """Undo last annotation"""
        if self.canvas:
            self.canvas.undo()
            self.update_annotations_list()
    
    def clear_annotations(self):
        """Clear all annotations"""
        reply = QMessageBox.question(self, "Clear Annotations",
                                     "Are you sure you want to clear all annotations?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.canvas:
                self.canvas.clear_annotations()
                self.update_annotations_list()
    
    def update_annotations_list(self):
        """Update the annotations list widget"""
        if not self.canvas:
            return
        
        self.annotations_list.clear()
        for ann in self.canvas.get_annotations():
            item = QListWidgetItem(f"📍 {ann.label} ({ann.annotation_type.value})")
            item.setForeground(QColor("#a0aec0"))
            self.annotations_list.addItem(item)
    
    def export_yolo(self):
        """Export annotations in YOLO format"""
        if not self.current_image_path or not self.canvas.get_annotations():
            QMessageBox.warning(self, "Export", "No image or annotations to export!")
            return
        
        output_path, _ = QFileDialog.getSaveFileName(self, "Save YOLO", "", "Text Files (*.txt)")
        if output_path:
            try:
                image_data = ImageData(
                    self.current_image_path,
                    Path(self.current_image_path).name,
                    self.current_image.shape[1],
                    self.current_image.shape[0],
                    self.canvas.get_annotations()
                )
                ExportManager.export_yolo(image_data, output_path)
                QMessageBox.information(self, "Success", f"Exported to {output_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")
    
    def export_json(self):
        """Export annotations in JSON format"""
        if not self.current_image_path or not self.canvas.get_annotations():
            QMessageBox.warning(self, "Export", "No image or annotations to export!")
            return
        
        output_path, _ = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON Files (*.json)")
        if output_path:
            try:
                image_data = ImageData(
                    self.current_image_path,
                    Path(self.current_image_path).name,
                    self.current_image.shape[1],
                    self.current_image.shape[0],
                    self.canvas.get_annotations()
                )
                ExportManager.export_json(image_data, output_path)
                QMessageBox.information(self, "Success", f"Exported to {output_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")
    
    def export_csv(self):
        """Export annotations in CSV format"""
        if not self.current_image_path or not self.canvas.get_annotations():
            QMessageBox.warning(self, "Export", "No image or annotations to export!")
            return
        
        output_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if output_path:
            try:
                image_data = ImageData(
                    self.current_image_path,
                    Path(self.current_image_path).name,
                    self.current_image.shape[1],
                    self.current_image.shape[0],
                    self.canvas.get_annotations()
                )
                ExportManager.export_csv(image_data, output_path)
                QMessageBox.information(self, "Success", f"Exported to {output_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")
    
    def export_xml(self):
        """Export annotations in XML format"""
        if not self.current_image_path or not self.canvas.get_annotations():
            QMessageBox.warning(self, "Export", "No image or annotations to export!")
            return
        
        output_path, _ = QFileDialog.getSaveFileName(self, "Save XML", "", "XML Files (*.xml)")
        if output_path:
            try:
                image_data = ImageData(
                    self.current_image_path,
                    Path(self.current_image_path).name,
                    self.current_image.shape[1],
                    self.current_image.shape[0],
                    self.canvas.get_annotations()
                )
                ExportManager.export_xml(image_data, output_path)
                QMessageBox.information(self, "Success", f"Exported to {output_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.information(self, "About AnnotationStudio",
                              "AnnotationStudio v1.0\n\n"
                              "Professional data labeling tool for images and videos.\n\n"
                              "Features:\n"
                              "• Rectangle, Polygon, Circle annotation tools\n"
                              "• Export to YOLO, COCO, JSON, CSV, XML formats\n"
                              "• Beautiful modern UI\n"
                              "• Video frame extraction\n\n"
                              "© 2024 AnnotationStudio")
    
    @staticmethod
    def create_q_image_from_array(image_array):
        """Convert numpy array to QImage"""
        height, width, channel = image_array.shape
        bytes_per_line = 3 * width
        return image_array  # Return for conversion
    
    @staticmethod
    def get_stylesheet():
        """Return application stylesheet"""
        return """
        QMainWindow {
            background-color: #0f172a;
            color: #e2e8f0;
        }
        QToolBar {
            background-color: #1a1f3a;
            border-bottom: 1px solid #333;
        }
        QStatusBar {
            background-color: #1a1f3a;
            color: #a0aec0;
            border-top: 1px solid #333;
        }
        QScrollBar:vertical {
            background-color: #1a1f3a;
            width: 12px;
        }
        QScrollBar::handle:vertical {
            background-color: #475569;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #64748b;
        }
        """
    
    @staticmethod
    def get_button_style(btn_type="default"):
        """Get button stylesheet"""
        styles = {
            "default": """
                QPushButton {
                    background-color: #1e293b;
                    color: #e2e8f0;
                    border: 1px solid #334155;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #334155;
                    border: 1px solid #475569;
                }
                QPushButton:pressed {
                    background-color: #475569;
                }
            """,
            "primary": """
                QPushButton {
                    background-color: #6366f1;
                    color: #fff;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #818cf8;
                }
                QPushButton:pressed {
                    background-color: #4f46e5;
                }
            """,
            "secondary": """
                QPushButton {
                    background-color: #8b5cf6;
                    color: #fff;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #a78bfa;
                }
                QPushButton:pressed {
                    background-color: #7c3aed;
                }
            """,
            "success": """
                QPushButton {
                    background-color: #10b981;
                    color: #fff;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #34d399;
                }
                QPushButton:pressed {
                    background-color: #059669;
                }
            """,
            "danger": """
                QPushButton {
                    background-color: #ef4444;
                    color: #fff;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #f87171;
                }
                QPushButton:pressed {
                    background-color: #dc2626;
                }
            """
        }
        return styles.get(btn_type, styles["default"])
    
    @staticmethod
    def get_input_style():
        """Get input field stylesheet"""
        return """
            QComboBox, QSpinBox, QLineEdit {
                background-color: #0f172a;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 6px;
            }
            QComboBox:hover, QSpinBox:hover, QLineEdit:hover {
                border: 1px solid #475569;
            }
            QComboBox::drop-down {
                border: none;
            }
        """
    
    @staticmethod
    def get_toolbar_style():
        """Get toolbar stylesheet"""
        return """
            QToolBar {
                background-color: #1a1f3a;
                border-bottom: 1px solid #333;
                spacing: 10px;
                padding: 5px;
            }
        """
    
    @staticmethod
    def get_list_style():
        """Get list widget stylesheet"""
        return """
            QListWidget {
                background-color: #0f172a;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #1e293b;
            }
            QListWidget::item:selected {
                background-color: #6366f1;
            }
        """
    
    @staticmethod
    def get_menu_style():
        """Get menu stylesheet"""
        return """
            QMenu {
                background-color: #1a1f3a;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #6366f1;
            }
        """
    
    @staticmethod
    def create_icon():
        """Create application icon"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor("#6366f1"))
        return QIcon(pixmap)
