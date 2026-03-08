# SECV3213 Fundamental of Image Processing
# Assignment 3: Course Project
# iPixelo: A Mobile-Inspired Image Editing and Enhancement Application
# Group Name: Innovators
# Group Member: 1. Chuah Chun Yi    A23CS0070
#               2. Chong Jun Hong   A23CS0066
#               3. Tai Yi Tian      A23CS0272

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QFileDialog, QStackedWidget, QSizePolicy,
    QToolButton, QButtonGroup, QSlider, QLineEdit, QGridLayout, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPixmap, QColor, QIcon

# --- Helper Class: Clickable Label for Thumbnails ---
class ClickableLabel(QLabel):
    clicked = pyqtSignal(str) # Signal sends the file path when clicked

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path

    def mousePressEvent(self, event):
        # When user clicks this label, emit the signal with the file path
        self.clicked.emit(self.file_path)

# --- PAGE 1: HOME PAGE (Your existing code, adapted) ---
class IPixeloHome(QWidget):
    # Signal to tell the Main Window: "Hey, an image was selected!"
    image_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        
        # Main Layout (Vertical)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Top Bar (Header)
        self.setup_header()

        # 2. Body Section
        self.setup_body()

    def setup_header(self):
        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(60)
        self.header_frame.setStyleSheet("background-color: white;")
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.logo_label = QLabel() 
        logo_pixmap = QPixmap("../project/img/iPexilo.png")
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(logo_pixmap)
        
        header_layout.addWidget(self.logo_label)
        self.main_layout.addWidget(self.header_frame)

    def setup_body(self):
        self.body_widget = QWidget()
        self.body_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #f3e6e8, stop:1 #e0c3fc
                );
            }
        """)
        
        body_layout = QVBoxLayout(self.body_widget)
        body_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title & Subtitle
        title = QLabel("Welcome to iPixelo")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: black; background: transparent;") 
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body_layout.addWidget(title)

        subtitle = QLabel("Upload and edit your image in here!")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: #555555; background: transparent;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body_layout.addWidget(subtitle)

        body_layout.addSpacing(20)

        # White Card
        self.card = QFrame()
        self.card.setFixedSize(700, 400)
        self.card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.6);
                border-radius: 20px;
            }
        """)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(50, 40, 50, 10)
        card_layout.setSpacing(15)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Upload Area
        self.upload_area = QFrame()
        self.upload_area.setFixedSize(600, 250) 
        self.upload_area.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.87); 
                border-radius: 15px;
                border: 1px solid #e0e0e0; 
            }
        """)
        
        upload_area_layout = QVBoxLayout(self.upload_area)
        upload_area_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_area_layout.setSpacing(15)

        # Upload Icon
        icon_label = QLabel() 
        icon_pixmap = QPixmap("../project/img/upload_icon.png")
        if not icon_pixmap.isNull():
            icon_pixmap = icon_pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("border: none; background: transparent;") 
        upload_area_layout.addWidget(icon_label)

        # Upload Button
        self.upload_btn = QPushButton("Upload Image")
        self.upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.upload_btn.setFixedSize(200, 45)
        self.upload_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        # Connect Button to File Dialog
        self.upload_btn.clicked.connect(self.open_file_dialog)
        upload_area_layout.addWidget(self.upload_btn)
        
        card_layout.addWidget(self.upload_area)
        
        # Thumbnails Section
        thumbs_container = QWidget()
        thumbs_container.setStyleSheet("background: transparent;")
        
        thumbs_layout = QHBoxLayout(thumbs_container)
        thumbs_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hint_text = QLabel("No image?\nTry one of these:")
        hint_text.setFont(QFont("Arial", 10))
        hint_text.setStyleSheet("color: black; background: transparent;")
        thumbs_layout.addWidget(hint_text)
        thumbs_layout.addSpacing(10)

        image_paths = [
            "../project/img/banana.png",   
            "../project/img/women.png",
            "../project/img/dog.png",
            "../project/img/biker.png"
        ]

        for path in image_paths:
            # Use our custom ClickableLabel
            thumb = ClickableLabel(path) 
            thumb.setFixedSize(70, 70)
            thumb.setCursor(Qt.CursorShape.PointingHandCursor)
            
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    70, 70,
                    Qt.AspectRatioMode.IgnoreAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                thumb.setPixmap(pixmap)
            else:
                thumb.setStyleSheet("background-color: grey; border-radius: 5px;")
            
            # Connect the click signal
            thumb.clicked.connect(self.select_image) 
            thumbs_layout.addWidget(thumb)

        card_layout.addWidget(thumbs_container)
        body_layout.addWidget(self.card)
        
        footer_label = QLabel("By uploading an image, you are agree to our\nTerm of Service.")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setFont(QFont("Arial", 8))
        footer_label.setStyleSheet("color: black; margin-bottom: 20px; background: transparent;")
        body_layout.addWidget(footer_label)

        self.main_layout.addWidget(self.body_widget)

    def open_file_dialog(self):
        """Opens a file dialog for the user to pick an image."""
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_name:
            self.select_image(file_name)

    def select_image(self, file_path):
        """Emits the signal so the Main Window knows to switch pages."""
        print(f"Selected: {file_path}")
        self.image_selected.emit(file_path)


# --- PAGE 2: EDITOR PAGE ---
class IPixeloEditor(QWidget):
    go_back = pyqtSignal() # Signal to go back to home

    def __init__(self):
        super().__init__()
        self.current_image_path = None
        
        # Main Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # 1. Header (Back, Logo, Save)
        self.setup_header()

        # 2. Main Work Area
        self.setup_workspace()

    def setup_header(self):
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("background-color: white;")
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 0, 10, 0) 
        
        # --- 1. LEFT CONTAINER (Fixed Width for centering) ---
        left_container = QWidget()
        left_container.setFixedWidth(120) 
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # RESET BUTTON (Formerly Back Button)
        self.reset_btn = QPushButton()
        self.reset_btn.setFixedSize(40, 40)
        self.reset_btn.setIcon(QIcon("../project/img/reset_icon.png"))
        self.reset_btn.setIconSize(QSize(30, 30))
        self.reset_btn.setStyleSheet("border: none; background: transparent;")
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # CHANGE: Connect to reset_image instead of go_back
        self.reset_btn.clicked.connect(self.reset_image)
        
        left_layout.addWidget(self.reset_btn)
        header_layout.addWidget(left_container)
        
        # --- SPRING 1 ---
        header_layout.addStretch()

        # --- 2. CENTER: Logo ---
        self.logo_label = QLabel()
        pix = QPixmap("../project/img/iPexilo.png")
        if not pix.isNull():
            pix = pix.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(pix)
        header_layout.addWidget(self.logo_label)

        # --- SPRING 2 ---
        header_layout.addStretch()

        # --- 3. RIGHT CONTAINER ---
        right_container = QWidget()
        right_container.setFixedWidth(120) 
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setFixedSize(100, 40)
        self.save_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #d6a4fc;
                color: black;
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover { background-color: #c084f5; }
        """)
        right_layout.addWidget(self.save_btn)
        header_layout.addWidget(right_container)
        
        self.layout.addWidget(header)

    def reset_image(self):
        """Reloads the original image, effectively resetting any edits."""
        if self.current_image_path:
            print(f"Resetting image: {self.current_image_path}")
            self.load_image(self.current_image_path)

    def setup_workspace(self):
        workspace = QWidget()
        workspace.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #f3e6e8, stop:1 #e0c3fc
                );
            }
        """)
        ws_layout = QHBoxLayout(workspace)
        ws_layout.setContentsMargins(20, 20, 20, 20)

        # --- LEFT SIDE: Image Canvas ---
        self.image_canvas = QLabel()
        self.image_canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        ws_layout.addWidget(self.image_canvas, stretch=3)

        # --- RIGHT SIDE: Tools Panel ---
        tools_panel = QWidget()
        tools_panel.setStyleSheet("background: transparent;")
        tools_layout = QVBoxLayout(tools_panel)
        tools_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 1. Top Icons Row
        icons_row = QHBoxLayout()
        icons_row.setSpacing(15)

        tools_data = [
            ("Crop",   "../project/img/crop_icon.png", 0),
            ("Rotate", "../project/img/rotate_icon.png", 1),
            ("Flip",   "../project/img/vertical_flip_icon.png", 2), 
            ("Adjust", "../project/img/adjust_icon.png", 3),
            ("Filter", "../project/img/filter_icon.png", 4), 
            ("Text",   "../project/img/text_icon.png", 5)
        ]

        self.main_tool_bg = QButtonGroup(self)
        self.main_tool_bg.setExclusive(True)

        for i, (name, icon_path, page_index) in enumerate(tools_data):
            btn = QToolButton()
            btn.setText(name)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(32, 32))
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setFixedSize(70, 70)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            btn.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    border: none;
                    color: black;
                    font-family: Arial;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 5px;
                    border-radius: 35px;
                }
                QToolButton:checked {
                    background-color: #d6a4fc;
                }
                QToolButton:hover {
                    background-color: rgba(255, 255, 255, 0.4);
                }
            """)
            
            if page_index is not None:
                btn.clicked.connect(lambda checked, idx=page_index: self.switch_tool_page(idx))
            
            self.main_tool_bg.addButton(btn, i)
            icons_row.addWidget(btn)
        
        self.main_tool_bg.button(0).setChecked(True)

        tools_layout.addLayout(icons_row)
        tools_layout.addSpacing(20)

        # 2. Tool Options Stack
        self.options_stack = QStackedWidget()
        
        # ================= PAGE 0: CROP =================
        crop_page = QWidget()
        crop_page_layout = QVBoxLayout(crop_page)
        crop_page_layout.setContentsMargins(0, 0, 0, 0)
        
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(10)
        
        self.crop_btn_group = QButtonGroup(self)
        self.crop_btn_group.setExclusive(True)
        ratios = ["Original", "16:9", "4:3", "Custom"]
        
        for i, text in enumerate(ratios):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setFixedSize(90, 35)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: black;
                    border: none;
                    font-family: Arial;
                    font-size: 12px;
                    font-weight: bold;
                    border-radius: 17px;
                }
                QPushButton:checked {
                    background-color: #d6a4fc;
                }
                QPushButton:hover {
                    background-color: rgba(214, 164, 252, 0.3);
                }
            """)
            self.crop_btn_group.addButton(btn, i)
            buttons_row.addWidget(btn)
        
        self.crop_btn_group.button(0).setChecked(True)
        buttons_row.addStretch()
        crop_page_layout.addLayout(buttons_row)
        crop_page_layout.addStretch()
        self.options_stack.addWidget(crop_page)

        # ================= PAGE 1: ROTATE =================
        rotate_page = QWidget()
        rotate_layout = QVBoxLayout(rotate_page)
        rotate_layout.setContentsMargins(0, 10, 0, 0)

        labels_layout = QHBoxLayout()
        l_start = QLabel("-180")
        l_end = QLabel("180")
        self.rotate_value_label = QLabel("0") 
        self.rotate_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        for l in [l_start, self.rotate_value_label, l_end]:
            l.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            l.setStyleSheet("color: black;")
        
        labels_layout.addWidget(l_start)
        labels_layout.addStretch()
        labels_layout.addWidget(self.rotate_value_label)
        labels_layout.addStretch()
        labels_layout.addWidget(l_end)
        rotate_layout.addLayout(labels_layout)

        self.rotate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rotate_slider.setRange(-180, 180)
        self.rotate_slider.setValue(0)
        self.rotate_slider.setFixedHeight(30)
        self.rotate_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rotate_slider.setStyleSheet(self.get_slider_style())
        self.rotate_slider.valueChanged.connect(lambda val: self.rotate_value_label.setText(str(val)))

        rotate_layout.addWidget(self.rotate_slider)
        rotate_layout.addStretch()
        self.options_stack.addWidget(rotate_page)

        # ================= PAGE 2: FLIP =================
        flip_page = QWidget()
        flip_page_v_layout = QVBoxLayout(flip_page)
        flip_page_v_layout.setContentsMargins(0, 0, 0, 0)
        
        flip_buttons_row = QHBoxLayout()
        flip_buttons_row.addStretch() 
        
        flip_buttons_data = [
            ("Horizontal", "../project/img/horizontal_flip_icon.png"),
            ("Vertical",   "../project/img/vertical_flip_icon.png")
        ]

        for name, icon_path in flip_buttons_data:
            btn = QToolButton()
            btn.setText(name)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(40, 40)) 
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setFixedSize(90, 80)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    border: none;
                    color: black;
                    font-family: Arial;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 5px;
                }
                QToolButton:hover {
                    background-color: rgba(255, 255, 255, 0.4);
                    border-radius: 10px;
                }
            """)
            
            flip_buttons_row.addWidget(btn)
            flip_buttons_row.addSpacing(20)

        flip_buttons_row.addStretch()
        flip_page_v_layout.addLayout(flip_buttons_row)
        flip_page_v_layout.addStretch() 
        self.options_stack.addWidget(flip_page)

        # ================= PAGE 3: ADJUST =================
        adjust_page = QWidget()
        adjust_layout = QVBoxLayout(adjust_page)
        adjust_layout.setContentsMargins(0, 0, 0, 0)
        adjust_layout.setSpacing(10)

        adjust_sub_tools = [
            ("Brightness", "../project/img/brightness_icon.png", 0),
            ("Blur",       "../project/img/blur_icon.png", 1),
            ("Noise\nReduction", "../project/img/noise_reduction_icon.png", 2),
            ("Sharpness",  "../project/img/sharpness_icon.png", 3),
            ("Saturation", "../project/img/saturation_icon.png", 4)
        ]

        adjust_icons_layout = QHBoxLayout()
        adjust_icons_layout.setSpacing(15)
        adjust_icons_layout.addStretch()

        self.adjust_btn_group = QButtonGroup(self)
        self.adjust_btn_group.setExclusive(True)
        self.adjust_slider_stack = QStackedWidget()

        for i, (name, icon_path, stack_idx) in enumerate(adjust_sub_tools):
            btn = QToolButton()
            btn.setText(name)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(28, 28))
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            width = 80 if "Noise" in name else 70
            btn.setFixedSize(width, 70) 
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            btn.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    border: none;
                    color: black;
                    font-family: Arial;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 5px;
                    border-radius: 35px;
                }
                QToolButton:checked {
                    background-color: #d6a4fc; 
                }
                QToolButton:hover {
                    background-color: rgba(255, 255, 255, 0.4);
                }
            """)
            btn.clicked.connect(lambda checked, idx=stack_idx: self.adjust_slider_stack.setCurrentIndex(idx))
            self.adjust_btn_group.addButton(btn, i)
            adjust_icons_layout.addWidget(btn)

        adjust_icons_layout.addStretch()
        adjust_layout.addLayout(adjust_icons_layout)

        self.adjust_slider_stack.addWidget(self.create_slider_widget(-100, 100, 0, "-100", "100"))
        self.adjust_slider_stack.addWidget(self.create_slider_widget(0, 20, 0, "0", "20"))
        self.adjust_slider_stack.addWidget(self.create_slider_widget(0, 20, 0, "0", "20"))
        self.adjust_slider_stack.addWidget(self.create_slider_widget(0, 20, 0, "0", "20"))
        self.adjust_slider_stack.addWidget(self.create_slider_widget(-100, 100, 0, "-100", "100"))

        adjust_layout.addWidget(self.adjust_slider_stack)

        self.roi_checkbox = QCheckBox("Apply to selected region (ROI)")
        self.roi_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.roi_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 11px;
                color: black;
                padding-left: 4px;
            }
        """)
        adjust_layout.addWidget(self.roi_checkbox)
        
        self.roi_status_label = QLabel("ROI mode disabled")
        self.roi_status_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #555555;
                padding-left: 6px;
            }
        """)
        adjust_layout.addWidget(self.roi_status_label)

        adjust_layout.addStretch()
        self.adjust_btn_group.button(0).setChecked(True)
        self.options_stack.addWidget(adjust_page)

        # ================= PAGE 4: FILTER =================
        filter_page = QWidget()
        filter_layout = QVBoxLayout(filter_page)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_thumbs_row = QHBoxLayout()
        filter_thumbs_row.setSpacing(20)
        filter_thumbs_row.addStretch()

        filters_data = [
            ("Original", "../project/img/dog.png"), 
            ("Bright",   "../project/img/Bright.jpeg"),
            ("B&W",      "../project/img/B&W.jpeg"),
            ("Cool",     "../project/img/Cool.jpeg")
        ]

        self.filter_btn_group = QButtonGroup(self)
        self.filter_btn_group.setExclusive(True)

        for i, (name, img_path) in enumerate(filters_data):
            btn = QToolButton()
            btn.setText(name)
            btn.setIcon(QIcon(img_path))
            btn.setIconSize(QSize(70, 70)) 
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setFixedSize(90, 110)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    border: 3px solid transparent; 
                    color: black;
                    font-family: Arial;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 5px;
                    border-radius: 10px;
                }
                QToolButton:checked {
                    border: 3px solid #d6a4fc; 
                    background-color: rgba(255, 255, 255, 0.3);
                }
                QToolButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """)
            self.filter_btn_group.addButton(btn, i)
            filter_thumbs_row.addWidget(btn)

        self.filter_btn_group.button(0).setChecked(True)
        filter_thumbs_row.addStretch()
        filter_layout.addLayout(filter_thumbs_row)
        filter_layout.addStretch()
        self.options_stack.addWidget(filter_page)

        # ================= PAGE 5: TEXT =================
        text_page = QWidget()
        text_layout = QVBoxLayout(text_page)
        text_layout.setContentsMargins(0, 10, 0, 0)
        text_layout.setSpacing(15)

        # 1. Text Input Field
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter text here...")
        self.text_input.setFixedHeight(40)
        self.text_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.7);
                color: black; 
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 5px 10px;
                font-family: Arial;
                font-size: 14px;
            }
        """)
        text_layout.addWidget(self.text_input)

        # 2. Position Selection (Grid)
        pos_layout = QHBoxLayout()
        pos_grid_widget = QWidget()
        pos_grid = QGridLayout(pos_grid_widget)
        pos_grid.setContentsMargins(0,0,0,0)
        pos_grid.setSpacing(5)

        positions = [
            ("Top-Left", 0, 0), ("Top-Center", 0, 1), ("Top-Right", 0, 2),
            ("Mid-Left", 1, 0), ("Center", 1, 1),     ("Mid-Right", 1, 2),
            ("Bot-Left", 2, 0), ("Bot-Center", 2, 1), ("Bot-Right", 2, 2),
            ("Custom",   3, 1) 
        ]
        
        self.pos_btn_group = QButtonGroup(self)
        self.pos_btn_group.setExclusive(True)

        for name, r, c in positions:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setFixedSize(80, 25)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255,255,255,0.5); 
                    border: 1px solid #999; 
                    border-radius: 5px; 
                    font-size: 10px;
                    color: black;
                }
                QPushButton:checked { background-color: #d6a4fc; border: 1px solid #888; font-weight: bold; }
            """)
            
            if name == "Custom":
                btn.clicked.connect(self.show_custom_coords)
            else:
                btn.clicked.connect(self.hide_custom_coords)
            
            self.pos_btn_group.addButton(btn)
            pos_grid.addWidget(btn, r, c)

        pos_layout.addWidget(pos_grid_widget)
        
        # 3. Custom Coordinates Inputs
        self.custom_coords_widget = QWidget()
        self.custom_coords_widget.setHidden(True)
        coords_layout = QVBoxLayout(self.custom_coords_widget)
        coords_layout.setContentsMargins(0,0,0,0)
        
        self.x_input = QSpinBox()
        self.x_input.setPrefix("X: ")
        self.x_input.setRange(0, 3000)
        self.x_input.setFixedHeight(30)
        
        self.y_input = QSpinBox()
        self.y_input.setPrefix("Y: ")
        self.y_input.setRange(0, 3000)
        self.y_input.setFixedHeight(30)
        
        for sb in [self.x_input, self.y_input]:
            sb.setFixedWidth(80)
            # Simplified style to prevent button clipping
            sb.setStyleSheet("color: black; background: white;")

        coords_layout.addWidget(self.x_input)
        coords_layout.addWidget(self.y_input)
        pos_layout.addWidget(self.custom_coords_widget)
        
        pos_layout.addStretch()
        text_layout.addLayout(pos_layout)

        # 4. Color & Rotation Row
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)

        # Color Buttons
        colors_layout = QHBoxLayout()
        colors = [
            ("Black", "#000000"), ("White", "#FFFFFF"), 
            ("Red", "#FF0000"), ("Yellow", "#FFD700"), 
            ("Orange", "#FFA500"), ("Blue", "#0000FF")
        ]
        
        self.color_group = QButtonGroup(self)
        self.color_group.setExclusive(True)
        
        for name, hex_code in colors:
            btn = QPushButton()
            btn.setFixedSize(25, 25)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {hex_code};
                    border: 2px solid #999;
                    border-radius: 12px;
                }}
                QPushButton:checked {{
                    border: 3px solid #d6a4fc; 
                }}
            """)
            self.color_group.addButton(btn)
            colors_layout.addWidget(btn)
        
        self.color_group.buttons()[0].setChecked(True)
        bottom_row.addLayout(colors_layout)

        # Rotation Input
        rot_layout = QHBoxLayout()
        rot_label = QLabel("Angle:")
        rot_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        # ADDED color: black;
        rot_label.setStyleSheet("color: black;")
        
        self.rot_input = QSpinBox()
        self.rot_input.setRange(-360, 360)
        self.rot_input.setSuffix("°")
        self.rot_input.setFixedWidth(70)
        self.rot_input.setFixedHeight(30)
        # Simplified style to prevent button clipping
        self.rot_input.setStyleSheet("color: black; background: white;")
        
        rot_layout.addWidget(rot_label)
        rot_layout.addWidget(self.rot_input)
        bottom_row.addLayout(rot_layout)
        
        bottom_row.addStretch()
        text_layout.addLayout(bottom_row)
        
        text_layout.addStretch()
        self.options_stack.addWidget(text_page)

        # ================= END PAGES =================

        tools_layout.addWidget(self.options_stack)
        tools_layout.addStretch()

        ws_layout.addWidget(tools_panel, stretch=1)
        self.layout.addWidget(workspace)

    def show_custom_coords(self):
        self.custom_coords_widget.setHidden(False)

    def hide_custom_coords(self):
        self.custom_coords_widget.setHidden(True)

    def get_slider_style(self):
        return """
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 3px;
                background: black;
                margin: 2px 0;
                border-radius: 1px;
            }
            QSlider::handle:horizontal {
                background: #8f8f8f;
                border: 1px solid #5c5c5c;
                width: 24px;
                height: 24px;
                border-radius: 12px; 
                margin: -11px 0;
            }
        """

    def create_slider_widget(self, min_val, max_val, default_val, left_text, right_text):
        #Helper to create the slider UI for Adjust tools.
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # Labels
        labels_layout = QHBoxLayout()
        l_start = QLabel(left_text)
        l_end = QLabel(right_text)
        val_label = QLabel(str(default_val))
        val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        for l in [l_start, val_label, l_end]:
            l.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            l.setStyleSheet("color: black;")

        labels_layout.addWidget(l_start)
        labels_layout.addStretch()
        labels_layout.addWidget(val_label)
        labels_layout.addStretch()
        labels_layout.addWidget(l_end)
        layout.addLayout(labels_layout)

        # Slider
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default_val)
        slider.setFixedHeight(30)
        slider.setCursor(Qt.CursorShape.PointingHandCursor)
        slider.setStyleSheet(self.get_slider_style())
        
        # Update center text when slider moves
        slider.valueChanged.connect(lambda val: val_label.setText(str(val)))
        
        layout.addWidget(slider)
        return container

    def switch_tool_page(self, index):
        #Switches the bottom options area based on tool clicked.
        self.options_stack.setCurrentIndex(index)
        
    def load_image(self, file_path):
        #Loads the image file into the canvas.
        self.current_image_path = file_path
        pixmap = QPixmap(file_path)
        
        if not pixmap.isNull():
            # Scale it to fit the view for now (simple display)
            # In a real app, you'd calculate aspect ratios dynamically
            scaled_pix = pixmap.scaled(600, 500, Qt.AspectRatioMode.KeepAspectRatio)
            self.image_canvas.setPixmap(scaled_pix)


# --- MAIN CONTROLLER ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iPixelo")
        self.resize(1001, 650)

        # The Stacked Widget holds multiple pages (Home, Editor)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Initialize Pages
        self.home_page = IPixeloHome()
        self.editor_page = IPixeloEditor()

        # Add pages to stack
        self.stack.addWidget(self.home_page)   # Index 0
        self.stack.addWidget(self.editor_page) # Index 1

        # Connect Signals
        # When home page selects image -> Load it in Editor -> Switch to Editor
        self.home_page.image_selected.connect(self.go_to_editor)
        
        # When editor back button is clicked -> Switch to Home
        self.editor_page.go_back.connect(self.go_to_home)

    def go_to_editor(self, file_path):
        self.editor_page.load_image(file_path)
        self.stack.setCurrentIndex(1) # Show Editor

    def go_to_home(self):
        self.stack.setCurrentIndex(0) # Show Home

# Run main.py
if __name__ == "__main__":
    import os
    import subprocess
    import sys

    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(current_dir, "main.py")
    subprocess.run([sys.executable, main_script])