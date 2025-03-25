import os
import cv2
import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog,
    QDockWidget, QHBoxLayout, QToolBar, QTableWidget, QTableWidgetItem,
    QHeaderView, QMenuBar, QMenu, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, QMimeData
from PySide6.QtGui import (
    QImage, QPixmap, QPainter, QColor, QDragEnterEvent, QDropEvent,
    QAction, QKeySequence, QPen, QPalette, QColor
)

from .about_dialog import AboutDialog
from utils.icon_utils import load_icon
from utils.image_utils import load_image, correct_perspective, rotate_image
from utils.icon_utils import resource_path

class TransFormApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_variables()
        self.setup_ui_components()
        self.setup_event_handlers()

    def init_ui(self):
        """Initialize the main UI window."""
        self.setWindowTitle("TransForm - Image Transformation and Cropping")
        self.setGeometry(100, 100, 1024, 600)
        self.setMinimumSize(600, 400)
        
        # Set window transparency and blur
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.Window)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: rgba(28, 28, 30, 0.85);
                border-radius: 10px;
            }
            QMenuBar {
                background-color: rgba(28, 28, 30, 0.85);
                border-radius: 10px 10px 0 0;
            }
            QMenuBar::item {
                background-color: transparent;
                color: gray;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: rgba(58, 58, 60, 0.8);
                border-radius: 5px;
            }
        """)

    def init_variables(self):
        """Initialize instance variables."""
        self.image = None
        self.display_image = None
        self.points = []
        self.selected_point = None
        self.crosshair_size = 60
        self.mouse_pos = None
        self.mouse_x = None
        self.mouse_y = None
        self.pos_x = None
        self.pos_y = None
        self.orig_width = None 
        self.orig_height = None
        self.pixmap_width = None
        self.pixmap_height = None
        self.label_width = None
        self.label_height = None
        self.scaled_width = None
        self.scaled_height = None
        self.offset_x = None
        self.offset_y = None
        self.scale_x = 0.0
        self.scale_y = 0.0
        self.zoom_factor = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.is_panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.current_file_path = None

        # Load icons
        self.icons = {
            'load': load_icon('folder-open.png'),
            'rotate_ccw': load_icon('undo.png'),
            'rotate_cw': load_icon('redo.png'),
            'correct': load_icon('file-export.png'),
            'zoom_in': load_icon('plus.png'),
            'zoom_reset': load_icon('plus-minus.png'),
            'zoom_out': load_icon('minus.png')
        }

    def setup_ui_components(self):
        """Set up all UI components."""
        self.setup_main_widget()
        self.setup_menubar()
        self.setup_toolbar()
        self.setup_dock_widget()
        
        # Enable drag and drop
        self.setAcceptDrops(True)

    def setup_main_widget(self):
        """Set up the main widget and image label."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        main_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(28, 28, 30, 0.85);
                border-radius: 10px;
            }
        """)
        
        self.setup_image_label(layout)

    def setup_image_label(self, layout):
        """Set up the image display label."""
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: rgba(44, 44, 46, 0.8);
                border-radius: 6px;
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.image_label)
        
        # Create welcome container
        self.setup_welcome_container()
        
        # Connect resize event
        self.image_label.resizeEvent = self.on_image_label_resize
        
        # Set up mouse tracking
        self.image_label.setMouseTracking(True)
        self.image_label.mousePressEvent = self.mouse_press_event
        self.image_label.mouseMoveEvent = self.mouse_move_event
        self.image_label.mouseReleaseEvent = self.mouse_release_event

    def setup_welcome_container(self):
        """Set up the welcome screen container."""
        self.welcome_container = QWidget(self.image_label)
        self.welcome_container.setStyleSheet("background-color: transparent;")
        welcome_layout = QVBoxLayout(self.welcome_container)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.setSpacing(20)
        
        # Welcome image
        welcome_image = QLabel()
        welcome_image.setPixmap(QPixmap(resource_path('icons/welcome.png')).scaled(
            80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        welcome_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_image)
        
        # Welcome text
        welcome_text = QLabel("Drop image here to open")
        welcome_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_text.setStyleSheet("""
            QLabel {
                color: gray;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        welcome_layout.addWidget(welcome_text)
        
        self.welcome_container.setFixedSize(300, 200)
        self.welcome_container.show()

    def setup_menubar(self):
        """Set up the application menu bar."""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: rgba(28, 28, 30, 0.85);
                color: white;
            }
            QMenuBar::item {
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: rgba(58, 58, 60, 0.8);
                border-radius: 5px;
            }
            QMenu {
                background-color: rgba(28, 28, 30, 0.85);
                color: white;
                border: none;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: rgba(58, 58, 60, 0.8);
            }
        """)
        
        # Create File menu
        file_menu = menubar.addMenu("File")
        
        # Add Open action
        open_action = QAction("Open...", self)
        open_action.setShortcut(QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_O))
        open_action.triggered.connect(self.load_image)
        file_menu.addAction(open_action)
        
        # Add separator
        file_menu.addSeparator()
        
        # Add About action
        about_action = QAction("About TransForm", self)
        about_action.triggered.connect(self.show_about_dialog)
        file_menu.addAction(about_action)
        
        # Add separator
        file_menu.addSeparator()
        
        # Add Save Image action
        self.save_action = QAction("Save Image...", self)
        self.save_action.setShortcut(QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_S))
        self.save_action.triggered.connect(self.correct_perspective)
        self.save_action.setEnabled(False)  # Initially disabled until image loaded with 4 points
        file_menu.addAction(self.save_action)
        
        # Add separator
        file_menu.addSeparator()
        
        # Add Quit action
        quit_action = QAction("Quit", self)
        quit_action.setShortcut("Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

    def setup_toolbar(self):
        """Set up the application toolbar."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setStyleSheet("""
            QToolBar {
                border: none;
                spacing: 10px;
                padding: 5px;
            }
        """)
        self.addToolBar(toolbar)
        
        # Style for buttons
        button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 8px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(58, 58, 60, 0.8);
            }
            QPushButton:disabled {
                background-color: transparent;
                color: rgba(255, 255, 255, 0.3);
            }
        """
        
        # Add buttons to toolbar
        self.load_button = QPushButton(" Open Image")
        self.load_button.setIcon(self.icons['load'])
        self.load_button.setToolTip("Open Image (jpeg, png, heic)")
        self.load_button.clicked.connect(self.load_image)
        self.load_button.setMinimumHeight(30)
        self.load_button.setStyleSheet(button_style)
        toolbar.addWidget(self.load_button)
        
        # Add spacer to push remaining buttons to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.addWidget(spacer)
        
        # Zoom out button
        self.zoom_out_button = QPushButton("")
        self.zoom_out_button.setIcon(self.icons['zoom_out'])
        self.zoom_out_button.setToolTip("Zoom Out")
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.zoom_out_button.setEnabled(False)
        self.zoom_out_button.setMinimumHeight(30)
        self.zoom_out_button.setMinimumWidth(30)
        self.zoom_out_button.setStyleSheet(button_style)
        toolbar.addWidget(self.zoom_out_button)
        
        # Zoom reset button
        self.zoom_reset_button = QPushButton("")
        self.zoom_reset_button.setIcon(self.icons['zoom_reset'])
        self.zoom_reset_button.setToolTip("Reset Zoom")
        self.zoom_reset_button.clicked.connect(self.zoom_reset)
        self.zoom_reset_button.setEnabled(False)
        self.zoom_reset_button.setMinimumHeight(30)
        self.zoom_reset_button.setMinimumWidth(30)
        self.zoom_reset_button.setStyleSheet(button_style)
        toolbar.addWidget(self.zoom_reset_button)
        
        # Zoom in button
        self.zoom_in_button = QPushButton("")
        self.zoom_in_button.setIcon(self.icons['zoom_in'])
        self.zoom_in_button.setToolTip("Zoom In")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_in_button.setEnabled(False)
        self.zoom_in_button.setMinimumHeight(30)
        self.zoom_in_button.setMinimumWidth(30)
        self.zoom_in_button.setStyleSheet(button_style)
        toolbar.addWidget(self.zoom_in_button)
        
        # Rotate counter-clockwise button
        self.rotate_ccw_button = QPushButton("")
        self.rotate_ccw_button.setIcon(self.icons['rotate_ccw'])
        self.rotate_ccw_button.setToolTip("Rotate Counter Clockwise")
        self.rotate_ccw_button.clicked.connect(self.rotate_counter_clockwise)
        self.rotate_ccw_button.setEnabled(False)
        self.rotate_ccw_button.setMinimumHeight(30)
        self.rotate_ccw_button.setMinimumWidth(30)
        self.rotate_ccw_button.setStyleSheet(button_style)
        toolbar.addWidget(self.rotate_ccw_button)
        
        # Rotate clockwise button
        self.rotate_cw_button = QPushButton("")
        self.rotate_cw_button.setIcon(self.icons['rotate_cw'])
        self.rotate_cw_button.setToolTip("Rotate Clockwise")
        self.rotate_cw_button.clicked.connect(self.rotate_clockwise)
        self.rotate_cw_button.setEnabled(False)
        self.rotate_cw_button.setMinimumHeight(30)
        self.rotate_cw_button.setMinimumWidth(30)
        self.rotate_cw_button.setStyleSheet(button_style)
        toolbar.addWidget(self.rotate_cw_button)
        
        # Correct/save button
        self.correct_button = QPushButton(" Save Image")
        self.correct_button.setIcon(self.icons['correct'])
        self.correct_button.setToolTip("Save Image")
        self.correct_button.clicked.connect(self.correct_perspective)
        self.correct_button.setEnabled(False)
        self.correct_button.setMinimumHeight(30)
        self.correct_button.setStyleSheet(button_style)
        toolbar.addWidget(self.correct_button)


    def get_adaptive_text_color():
        """Returns a color suitable for the current system theme"""
        palette = app.palette()
        return palette.color(QPalette.WindowText)  # Text color adapts to light/dark mode


    def setup_dock_widget(self):
        """Set up the left dock widget for coordinates and preview."""
        # Create left dock widget
        left_dock = QDockWidget(self)
        left_dock.setTitleBarWidget(QWidget())
        left_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        left_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        left_dock.setMinimumWidth(150)
        left_dock.resize(200, left_dock.height())
        
        # Set dock widget styling
        left_dock.setWindowFlags(Qt.WindowType.Widget)
        left_dock.setStyleSheet("""
            QDockWidget {
                background-color: rgba(28, 28, 30, 0.85);
                border-radius: 10px;
            }
            QDockWidget::title {
                background: transparent;
                padding: 0px;
                margin: 0px;
            }
            QDockWidget::separator {
                width: 1px;
                background: black;
            }
        """)
        
        # Create dock widget content
        left_dock_widget = QWidget()
        left_dock_layout = QVBoxLayout(left_dock_widget)
        left_dock_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add information heading
        info_heading = QLabel("Image Information")
        info_heading.setStyleSheet("""
            QLabel {
                color: gray;
                font-size: 12px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        left_dock_layout.addWidget(info_heading)
        
        # Create table for coordinate display
        self.coord_table = QTableWidget()
        self.coord_table.setColumnCount(2)
        self.coord_table.horizontalHeader().setVisible(False)
        self.coord_table.verticalHeader().setVisible(False)
        self.coord_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.coord_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.coord_table.setShowGrid(False)
        self.coord_table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 1px;
                color: {get_adaptive_text_color().name()};
                font-size: 11px;
                margin-left: 4px;
            }
            QTableWidget::item {
                padding: 1px;
            }
        """)
        self.coord_table.verticalHeader().setDefaultSectionSize(14)
        self.coord_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.coord_table.setContentsMargins(0, 0, 0, 0)
        left_dock_layout.addWidget(self.coord_table)
        
        # Add preview heading
        preview_heading = QLabel("Preview")
        preview_heading.setStyleSheet("""
            QLabel {
                color: gray;
                font-size: 12px;
                font-weight: bold;
                padding: 6px;
            }
        """)
        left_dock_layout.addWidget(preview_heading)
        
        # Add preview label
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border-radius: 6px;
            }
        """)
        left_dock_layout.addWidget(self.preview_label)
        
        # Set left dock widget
        left_dock.setWidget(left_dock_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, left_dock)

    def setup_event_handlers(self):
        """Set up event handlers for the application."""
        pass

    def on_image_label_resize(self, event):
        """Handle resize events for the image label."""
        # Center the welcome container in the image label
        if hasattr(self, 'welcome_container'):
            self.welcome_container.setGeometry(
                (self.image_label.width() - self.welcome_container.width()) // 2,
                (self.image_label.height() - self.welcome_container.height()) // 2,
                self.welcome_container.width(),
                self.welcome_container.height()
            )
        
        # Update the image display if an image is loaded
        if self.display_image is not None:
            self.update_display()
        
        # Call the original resize event if it exists
        if hasattr(self.image_label, '_resizeEvent'):
            self.image_label._resizeEvent(event)

    def update_coordinate_display(self):
        """Update the coordinate display table with current information."""
        # Create list of rows
        rows = []
        
        # Add scaling information
        if self.display_image is not None:
            pixmap = self.image_label.pixmap()
            if pixmap is not None:
                rows.append(("Image Size", f"{self.orig_width} x {self.orig_height}"))
                rows.append(("Display Size", f"{self.scaled_width:.0f} x {self.scaled_height:.0f}"))
                rows.append(("Zoom", f"{self.zoom_factor * 100:.0f}%"))
                
                # Add mouse position if available
                if self.mouse_x is not None and self.mouse_y is not None:
                    rows.append(("Mouse", f"{self.mouse_x:.0f}, {self.mouse_y:.0f}"))
                
                # Add point coordinates
                for i, point in enumerate(self.points):
                    rows.append((f"Point {i+1}", f"{point[0]:.0f}, {point[1]:.0f}"))
        
        # Update table
        self.coord_table.setRowCount(len(rows))
        for i, (key, value) in enumerate(rows):
            self.coord_table.setItem(i, 0, QTableWidgetItem(key))
            self.coord_table.setItem(i, 1, QTableWidgetItem(value))

    def update_display(self):
        """Update the image display with current zoom and pan settings."""
        if self.display_image is None:
            return
        
        # Get image dimensions
        self.label_width = self.image_label.width()
        self.label_height = self.image_label.height()
        
        # Calculate scaled dimensions based on zoom factor
        self.scaled_width = self.orig_width * self.zoom_factor
        self.scaled_height = self.orig_height * self.zoom_factor
        
        # Create a larger pixmap for drawing
        pixmap = QPixmap(int(self.scaled_width), int(self.scaled_height))
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Create a painter for the pixmap
        painter = QPainter(pixmap)
        
        # Draw the image
        image = QImage(
            self.display_image.data,
            self.display_image.shape[1],
            self.display_image.shape[0],
            self.display_image.shape[1] * 3,
            QImage.Format.Format_RGB888
        )
        painter.drawImage(0, 0, image.scaled(
            int(self.scaled_width),
            int(self.scaled_height),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        
        # Draw points
        for i, point in enumerate(self.points):
            # Calculate scaled point position
            x = int(point[0] * self.zoom_factor)
            y = int(point[1] * self.zoom_factor)
            
            # Set color based on selection
            if self.selected_point == i:
                pen = QPen(QColor(255, 0, 0), 2)  # Red outline for selected point with 2px width
                painter.setPen(pen)
                painter.setBrush(Qt.GlobalColor.transparent)
            else:
                pen = QPen(QColor(255, 255, 255), 2)  # White outline for normal points with 2px width
                painter.setPen(pen)
                painter.setBrush(Qt.GlobalColor.transparent)
            
            # Draw circle instead of crosshair
            circle_radius = int(15 * self.zoom_factor)  # Adjust radius as needed
            painter.drawEllipse(x - circle_radius, y - circle_radius, 
                               circle_radius * 2, circle_radius * 2)
            
            # Draw point number
            painter.drawText(x + circle_radius + 2, y - 5, str(i + 1))
        
        # Draw lines connecting the 4 points if all 4 points are present
        if len(self.points) == 4:
            # Set line color and width - white with 50% transparency
            pen = QPen(QColor(255, 255, 255, 50), 2)  # White
            painter.setPen(pen)
            
            # Connect the points in sequence (1-2-3-4-1)
            for i in range(4):
                # Get current and next point (wrapping around to the first point)
                current_point = self.points[i]
                next_point = self.points[(i + 1) % 4]
                
                # Calculate scaled positions
                x1 = int(current_point[0] * self.zoom_factor)
                y1 = int(current_point[1] * self.zoom_factor)
                x2 = int(next_point[0] * self.zoom_factor)
                y2 = int(next_point[1] * self.zoom_factor)
                
                # Draw the connecting line
                painter.drawLine(x1, y1, x2, y2)
        
        # End painting
        painter.end()
        
        # Calculate the position to center the image in the label
        offset_x = max(0, (self.label_width - self.scaled_width) // 2)
        offset_y = max(0, (self.label_height - self.scaled_height) // 2)
        
        # Apply pan offset
        offset_x += self.pan_offset_x
        offset_y += self.pan_offset_y
        
        # Store offsets for mouse position calculation
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        # Create a pixmap for the label with the correct size
        label_pixmap = QPixmap(self.label_width, self.label_height)
        label_pixmap.fill(Qt.GlobalColor.transparent)
        
        # Draw the image pixmap onto the label pixmap
        label_painter = QPainter(label_pixmap)
        label_painter.drawPixmap(offset_x, offset_y, pixmap)
        label_painter.end()
        
        # Set the pixmap to the label
        self.image_label.setPixmap(label_pixmap)
        
        # Update preview if we have 4 points
        if len(self.points) == 4:
            self.update_preview()
        
        # Update coordinate display
        self.update_coordinate_display()

    def update_preview(self):
        """Update the free transformation preview."""
        if self.image is None or len(self.points) != 4:
            return
        
        # Apply free transformation
        corrected = self.apply_perspective_correction()
        if corrected is None:
            return
        
        # No need to convert to RGB as the image is already in RGB format
        h, w = corrected.shape[:2]
        bytes_per_line = 3 * w
        q_img = QImage(corrected.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Scale to fit preview label
        preview_width = self.preview_label.width()
        preview_height = self.preview_label.height()
        
        # Calculate scaling to fit preview area while maintaining aspect ratio
        scale_w = preview_width / w
        scale_h = preview_height / h
        scale = min(scale_w, scale_h)
        
        # Create scaled pixmap
        pixmap = QPixmap.fromImage(q_img).scaled(
            int(w * scale),
            int(h * scale),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Set pixmap to preview label
        self.preview_label.setPixmap(pixmap)

    def apply_perspective_correction(self):
        """Apply free transformation to the image."""
        from utils.image_utils import correct_perspective
        
        if self.image is None or len(self.points) != 4:
            return None
        
        return correct_perspective(self.image, self.points)

    def mouse_press_event(self, event):
        """Handle mouse press events."""
        if self.display_image is None:
            return
        
        # Calculate image coordinates from mouse position
        mouse_x = event.position().x() - self.offset_x
        mouse_y = event.position().y() - self.offset_y
        
        # Convert to original image coordinates
        img_x = mouse_x / self.zoom_factor
        img_y = mouse_y / self.zoom_factor
        
        # Check if right mouse button is pressed (for panning)
        if event.button() == Qt.MouseButton.RightButton:
            self.is_panning = True
            self.pan_start_x = event.position().x()
            self.pan_start_y = event.position().y()
            return
        
        # Check if we're clicking on a point
        self.selected_point = None
        selection_threshold = 20  # Pixels
        for i, point in enumerate(self.points):
            # Calculate distance to point
            dx = point[0] - img_x
            dy = point[1] - img_y
            distance = (dx * dx + dy * dy) ** 0.5
            
            # If close enough, select the point
            if distance < selection_threshold:
                self.selected_point = i
                break
        
        # If no point selected and we have less than 4 points, add a new one
        if self.selected_point is None and len(self.points) < 4:
            self.points.append([img_x, img_y])
            self.selected_point = len(self.points) - 1
        
        # Update display
        self.update_display()

    def mouse_move_event(self, event):
        """Handle mouse move events."""
        if self.display_image is None:
            return
        
        # Calculate image coordinates from mouse position
        mouse_x = event.position().x() - self.offset_x
        mouse_y = event.position().y() - self.offset_y
        
        # Convert to original image coordinates
        img_x = mouse_x / self.zoom_factor
        img_y = mouse_y / self.zoom_factor
        
        # Store mouse position for display
        self.mouse_x = img_x
        self.mouse_y = img_y
        
        # Handle panning
        if self.is_panning:
            # Calculate pan offset
            dx = event.position().x() - self.pan_start_x
            dy = event.position().y() - self.pan_start_y
            
            # Update pan offset
            self.pan_offset_x += dx
            self.pan_offset_y += dy
            
            # Update pan start position
            self.pan_start_x = event.position().x()
            self.pan_start_y = event.position().y()
            
            # Update display
            self.update_display()
            return
        
        # Handle point movement
        if self.selected_point is not None:
            # Update point position
            self.points[self.selected_point] = [img_x, img_y]
            
            # Update display
            self.update_display()
        else:
            # Just update coordinate display
            self.update_coordinate_display()

    def mouse_release_event(self, event):
        """Handle mouse release events."""
        # Stop panning
        if event.button() == Qt.MouseButton.RightButton:
            self.is_panning = False
        
        # Deselect point
        self.selected_point = None
        
        # Enable/disable correct button based on number of points
        self.correct_button.setEnabled(len(self.points) == 4)
        self.save_action.setEnabled(len(self.points) == 4)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events for drag and drop support."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Handle drop events for drag and drop support."""
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            self.load_image_from_path(file_path)

    def load_image(self):
        """Open a file dialog to load an image."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.heic)"
        )
        
        if file_path:
            self.load_image_from_path(file_path)

    def load_image_from_path(self, file_path):
        """Load an image from the specified path."""
        from utils.image_utils import load_image
        
        # Load image
        image = load_image(file_path)
        if image is None:
            return
        
        # Store image
        self.image = image
        self.display_image = image.copy()
        
        # Get image dimensions
        self.orig_height, self.orig_width = self.image.shape[:2]
        
        # Reset points and view
        self.reset_points_and_view()
        
        # Store file path
        self.current_file_path = file_path
        
        # Hide welcome container
        if hasattr(self, 'welcome_container'):
            self.welcome_container.hide()
        
        # Enable buttons
        self.zoom_in_button.setEnabled(True)
        self.zoom_out_button.setEnabled(True)
        self.zoom_reset_button.setEnabled(True)
        self.rotate_cw_button.setEnabled(True)
        self.rotate_ccw_button.setEnabled(True)
        self.correct_button.setEnabled(False)
        self.save_action.setEnabled(False)
        
        # Update display
        self.update_display()

    def calculate_fit_zoom_factor(self):
        """Calculate zoom factor to fit the image in the window."""
        if self.display_image is None:
            return 1.0
            
        # Calculate zoom factor to fit image in the window
        label_width = self.image_label.width()
        label_height = self.image_label.height()
        
        # Calculate scale factors for width and height
        scale_w = label_width / self.orig_width
        scale_h = label_height / self.orig_height
        
        # Use the smaller scale factor to ensure the entire image fits
        return min(scale_w, scale_h)

    def zoom_in(self):
        """Zoom in on the image."""
        if self.display_image is None:
            return
        
        # Increase zoom factor
        self.zoom_factor *= 1.2
        
        # Update display
        self.update_display()

    def zoom_out(self):
        """Zoom out on the image."""
        if self.display_image is None:
            return
        
        # Decrease zoom factor
        self.zoom_factor /= 1.2
        
        # Update display
        self.update_display()

    def zoom_reset(self):
        """Reset zoom to fit the image in the window."""
        if self.display_image is None:
            return
        
        # Calculate zoom factor to fit image in the window
        self.zoom_factor = self.calculate_fit_zoom_factor()
        
        # Reset pan offset
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        
        # Update display
        self.update_display()

    def rotate_clockwise(self):
        """Rotate the image clockwise."""
        if self.display_image is None:
            return
        
        from utils.image_utils import rotate_image
        
        # Rotate image
        self.image = rotate_image(self.image, clockwise=True)
        self.display_image = self.image.copy()
        
        # Update dimensions
        self.orig_height, self.orig_width = self.image.shape[:2]
        
        # Reset points and view
        self.reset_points_and_view()
        
        # Update display
        self.update_display()

    def rotate_counter_clockwise(self):
        """Rotate the image counter-clockwise."""
        if self.display_image is None:
            return
        
        from utils.image_utils import rotate_image
        
        # Rotate image
        self.image = rotate_image(self.image, clockwise=False)
        self.display_image = self.image.copy()
        
        # Update dimensions
        self.orig_height, self.orig_width = self.image.shape[:2]
        
        # Reset points and view
        self.reset_points_and_view()
        
        # Update display
        self.update_display()

    def reset_points_and_view(self):
        """Reset points, selected point, and view settings."""
        # Reset points and selected point
        self.points = []
        self.selected_point = None
        
        # Reset zoom and pan
        self.zoom_factor = self.calculate_fit_zoom_factor()
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        
        # Disable buttons that require points
        self.correct_button.setEnabled(False)
        self.save_action.setEnabled(False)

    def correct_perspective(self):
        """Apply free transformation and save the result."""
        if self.image is None or len(self.points) != 4:
            return
        
        # Apply free transformation
        corrected = self.apply_perspective_correction()
        if corrected is None:
            return
        
        # Open save dialog
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self,
            "Save Image",
            "",
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)"
        )
        
        if file_path:
            # Convert from RGB to BGR for saving with OpenCV
            corrected_bgr = cv2.cvtColor(corrected, cv2.COLOR_RGB2BGR)
            # Save image
            cv2.imwrite(file_path, corrected_bgr)

    def show_about_dialog(self):
        """Show the about dialog."""
        from ui.about_dialog import AboutDialog
        about_dialog = AboutDialog(self)
        about_dialog.exec()
