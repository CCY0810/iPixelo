# SECV3213 Fundamental of Image Processing
# Assignment 3: Course Project
# iPixelo: A Mobile-Inspired Image Editing and Enhancement Application
# Group Name: Innovators
# Group Member: 1. Chuah Chun Yi    A23CS0070
#               2. Chong Jun Hong   A23CS0066
#               3. Tai Yi Tian      A23CS0272

import sys
import cv2 as cv

from PyQt6.QtWidgets import QApplication, QSlider, QToolButton
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QTimer

from user_interface import MainWindow as UIBase
from image_processor import (
    resize_image,
    crop_image,
    rotate_image,
    flip_image,
    adjust_brightness,
    blur_image,
    noise_reduction,
    adjust_sharpness,
    adjust_saturation,
    apply_filter,
    add_text,
    select_roi
)


class MainWindow(UIBase):
    def __init__(self):
        super().__init__()

        self.base_img = None    # Original file content (never changes)
        # Global Edit State
        self.edit_state = {
            'crop': {'mode': 'original', 'rect': None},
            'rotate': 0,
            'flip': {'horizontal': False, 'vertical': False},
            # Adjust tools state
            'adjust': {
                0: {'val': 0, 'roi': None},
                1: {'val': 0, 'roi': None},
                2: {'val': 0, 'roi': None},
                3: {'val': 0, 'roi': None},
                4: {'val': 0, 'roi': None}
            },
            'filter': 'original',
            'text': {
                'content': "",
                'position': "center",
                'color': (0, 0, 0),
                'angle': 0,
                'custom_xy': None
            }
        }
        
        # Compatibility/Alias for existing code that uses self.adjust_state
        # Points the old variable to the dictionary inside new state
        self.adjust_state = self.edit_state['adjust']
        self.current_filter = "original" 
        self.current_adjust_index = 0

        # ---------------- ROI STATUS ----------------
        self.editor_page.roi_checkbox.stateChanged.connect(
            self.toggle_roi_mode
        )

        # ---------------- WIRING ----------------
        # Connect tool change to commit logic
        self.editor_page.main_tool_bg.idClicked.connect(self.on_tool_changed)
        self.editor_page.adjust_btn_group.idClicked.connect(self.on_adjust_changed)
        
        # Clickable Logo to Return Home
        self.editor_page.logo_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.editor_page.logo_label.mousePressEvent = self.on_logo_clicked

        self.bind_crop()
        self.bind_rotate()
        self.bind_flip()
        self.bind_adjust()
        self.bind_filter()
        self.bind_text()
        self.bind_reset_save()

    # Image Load & Display
    def go_to_editor(self, file_path):
        # Read image from file
        img = cv.imread(file_path)
        if img is None:
            return

        # Resize and initialize image states
        self.base_img = resize_image(img)
        # Resize and initialize image states
        self.base_img = resize_image(img)
        # self.processed_img and self.current_img will be derived from base_img via pipeline
        self.current_img = self.base_img.copy()

        # Update display and reset UI
        self.reset_ui_controls() 
        # Force switch to first tool (Crop)
        self.editor_page.main_tool_bg.button(0).setChecked(True)
        self.editor_page.switch_tool_page(0)
        self.on_tool_changed(0) 
        
        self.update_canvas()
        self.stack.setCurrentIndex(1)

    # Effect Pipeline
    def run_effect_pipeline(self):
        """
        Applies ALL active effects from scratch on the base image.
        Order: Base -> Crop -> Rotate -> Flip -> Adjust -> Filter -> Text
        """
        if self.base_img is None:
            return None
            
        img = self.base_img.copy()
        
        # 1. Rotate
        rot = self.edit_state['rotate']
        if rot != 0:
            img = rotate_image(img, rot)
            
        # 2. Flip
        flip = self.edit_state['flip']
        if flip['horizontal']:
            img = flip_image(img, 'horizontal')
        if flip['vertical']:
            img = flip_image(img, 'vertical')

        # 3. Crop
        crop = self.edit_state['crop']
        if crop['mode'] != 'original':
             img = crop_image(img, crop['mode'], crop['rect'])

        # 4. Adjustments
        # Adjust expects the image to apply effects on
        # Loop through adjust keys sorted to ensure consistent order if needed
        for i in range(5):
            state = self.edit_state['adjust'][i]
            val = state['val']
            roi = state['roi']
            
            if val != 0:
                if i == 0: img = adjust_brightness(img, val, roi)
                elif i == 1: img = blur_image(img, abs(val), roi)
                elif i == 2: img = noise_reduction(img, abs(val), roi)
                elif i == 3: img = adjust_sharpness(img, abs(val), roi)
                
                
        # Saturation (4)
        s4 = self.edit_state['adjust'][4]
        if s4['val'] != 0:
             img = adjust_saturation(img, s4['val'], s4['roi'])

        # 5. Filter
        if self.edit_state['filter'] != 'original':
             img = apply_filter(img, self.edit_state['filter'], None)
             
        # 6. Text
        txt = self.edit_state['text']
        if txt['content']:
             img = add_text(
                 img, 
                 txt['content'], 
                 txt['position'], 
                 txt['color'], 
                 txt['angle'], 
                 txt['custom_xy']
             )
             
        # Update current image
        self.current_img = img
        return img


    # Update Canvas
    def update_canvas(self):
        # Check if there is an image to display
        if self.current_img is None:
            return

        # Convert BGR to RGB
        rgb = cv.cvtColor(self.current_img, cv.COLOR_BGR2RGB)
        h, w, ch = rgb.shape

        # Create QImage from data
        qimg = QImage(
            rgb.data,
            w,
            h,
            ch * w,
            QImage.Format.Format_RGB888
        )

        # Create QPixmap and set to label
        pixmap = QPixmap.fromImage(qimg)
        self.editor_page.image_canvas.setPixmap(
            pixmap.scaled(
                self.editor_page.image_canvas.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    # Tool Changed
    def on_tool_changed(self, idx):
        self.current_tool_index = idx
        
        # Load UI from State for the new tool page
        # UI reflects the current edit_state for that tool
        
        # 0: Crop
        if idx == 0:
             mode = self.edit_state['crop']['mode']
             # Find button index
             btn_idx = 0
             if mode == '16:9': btn_idx = 1
             elif mode == '4:3': btn_idx = 2
             elif mode == 'custom': btn_idx = 3
             
             if self.editor_page.crop_btn_group.button(btn_idx):
                 self.editor_page.crop_btn_group.button(btn_idx).setChecked(True)
                 
        # 1: Rotate
        elif idx == 1:
             val = self.edit_state['rotate']
             self.editor_page.rotate_slider.blockSignals(True)
             self.editor_page.rotate_slider.setValue(val)
             self.editor_page.rotate_slider.blockSignals(False)
             self.editor_page.rotate_value_label.setText(str(val))
             
        # 2: Flip
    
        # 3: Adjust
        elif idx == 3:
             # Default to first sub-tool or last used? 
             # Update the current visible slider
             sub_idx = self.editor_page.adjust_slider_stack.currentIndex()
             self.on_adjust_changed(sub_idx)
             
        # 4: Filter
        elif idx == 4:
             name = self.edit_state['filter']
             # Find button with this name
             for btn in self.editor_page.filter_btn_group.buttons():
                 if btn.text().lower() == name or (name=='bw' and btn.text()=='B&W'):
                     btn.setChecked(True)
                     break
                     
        # 5: Text
        elif idx == 5:
             # Restore text input content
             txt = self.edit_state['text']
             self.editor_page.text_input.blockSignals(True)
             self.editor_page.text_input.setText(txt['content'])
             self.editor_page.rot_input.blockSignals(True)
             self.editor_page.rot_input.setValue(txt['angle'])
             self.editor_page.text_input.blockSignals(False)
             self.editor_page.rot_input.blockSignals(False)
    
    # Adjust Changed
    def on_adjust_changed(self, idx):
        # Update the current visible slider
        if idx != self.current_adjust_index:
            
            # Find the new slider
            slider = (
                self.editor_page.adjust_slider_stack
                .widget(idx)
                .findChild(type(self.editor_page.rotate_slider))
            )
            
            if slider:
                # Retreive stored state
                state = self.adjust_state.get(idx, {'val': 0, 'roi': None})
                val = state['val']
                roi = state['roi']
                
                # Restore Slider
                slider.setValue(val)
                
                # Restore ROI / Checkbox
                self.active_roi = roi
                self.editor_page.roi_checkbox.blockSignals(True)
                if roi:
                    self.editor_page.roi_checkbox.setChecked(True)
                    self.editor_page.roi_status_label.setText(f"ROI Selected: {roi}")
                else:
                    self.editor_page.roi_checkbox.setChecked(False)
                    self.editor_page.roi_status_label.setText("ROI mode disabled")
                self.editor_page.roi_checkbox.blockSignals(False)
            
            self.current_adjust_index = idx


    # Reset UI
    def reset_ui_controls(self):
        # Clears the global state to default
        self.edit_state = {
            'crop': {'mode': 'original', 'rect': None},
            'rotate': 0,
            'flip': {'horizontal': False, 'vertical': False},
            'adjust': {
                0: {'val': 0, 'roi': None},
                1: {'val': 0, 'roi': None},
                2: {'val': 0, 'roi': None},
                3: {'val': 0, 'roi': None},
                4: {'val': 0, 'roi': None}
            },
            'filter': 'original',
            'text': {
                'content': "",
                'position': "center",
                'color': (0, 0, 0),
                'angle': 0,
                'custom_xy': None
            }
        }
        self.adjust_state = self.edit_state['adjust']
        
        # Reset Sliders UI
        self.editor_page.rotate_slider.setValue(0)
        for i in range(self.editor_page.adjust_slider_stack.count()):
            slider = (
                self.editor_page.adjust_slider_stack
                .widget(i)
                .findChild(type(self.editor_page.rotate_slider))
            )
            if slider: slider.setValue(0)

        # Reset Text UI
        self.editor_page.text_input.clear()
        self.editor_page.rot_input.setValue(0)
        
        # Reset Filter UI
        self.editor_page.filter_btn_group.button(0).setChecked(True)
        
        # Reset Crop UI
        if self.editor_page.crop_btn_group.button(0):
            self.editor_page.crop_btn_group.button(0).setChecked(True)
        
        # Reset ROI UI
        self.active_roi = None
        self.editor_page.roi_checkbox.blockSignals(True)
        self.editor_page.roi_checkbox.setChecked(False)
        self.editor_page.roi_checkbox.blockSignals(False)
        self.editor_page.roi_status_label.setText("ROI mode disabled")

    # ROI Status
    def toggle_roi_mode(self):
        # Check current state of ROI checkbox
        is_checked = self.editor_page.roi_checkbox.isChecked()

        if is_checked:
            # Trigger ROI selection deferred to let UI update first
            print("ROI mode ON - Launching selector...")
            # Use QTimer to allow the checkbox state to fully commit before blocking
            QTimer.singleShot(50, self.launch_roi_selector)
        else:
            # ROI mode turn OFF
            self.active_roi = None
            self.editor_page.roi_status_label.setText("ROI mode disabled")
            
            # Update ROI state for the current tool
            if self.editor_page.main_tool_bg.checkedId() == 3: # Adjust Tool
                 idx = self.current_adjust_index
                 self.adjust_state[idx]['roi'] = None
            
            # Refresh view
            self.update_current_view()

    def launch_roi_selector(self):
        roi = select_roi(self.current_img, "Select ROI")
        
        # If selection successful
        if roi:
            self.active_roi = roi
            self.editor_page.roi_status_label.setText(f"ROI Selected: {roi}")
            
            # Update ROI state for the current tool
            if self.editor_page.main_tool_bg.checkedId() == 3: # Adjust Tool
                 idx = self.current_adjust_index
                 self.adjust_state[idx]['roi'] = self.active_roi
        else:
            # User cancelled selection
            self.editor_page.roi_checkbox.setChecked(False)
            self.active_roi = None
            self.editor_page.roi_status_label.setText("ROI Selection Cancelled")
        
        # Refresh view
        self.update_current_view()

    # Update Current View
    def update_current_view(self):
        # Refresh the current canvas based on active tool settings
        idx = self.editor_page.adjust_slider_stack.currentIndex()
        
        if self.editor_page.main_tool_bg.checkedId() == 3: # Adjust Tool
             # Find active slider
             slider_widget = self.editor_page.adjust_slider_stack.currentWidget()
             slider = slider_widget.findChild(type(self.editor_page.rotate_slider))
             if slider:
                 self.apply_adjust(idx, slider.value())
        
        elif self.editor_page.main_tool_bg.checkedId() == 4: # Filter Tool
             # Re-apply current filter
             btn = self.editor_page.filter_btn_group.checkedButton()
             if btn:
                 name = btn.text().lower()
                 if name == "b&w": name = "bw"
                 self.apply_filter(name)

    # Crop
    def bind_crop(self):
        # Connect crop buttons
        self.editor_page.crop_btn_group.idClicked.connect(
            self.apply_crop
        )

    # Apply Crop
    def apply_crop(self, idx):
        modes = ["original", "16:9", "4:3", "custom"]
        chosen_mode = modes[idx]
        
        rect = None
        if chosen_mode == "custom":
            # Generate a preview image for selection
            # New Pipeline Order: Base -> Rotate -> Flip -> Crop -> Adjust
            # Coordinate system for Crop is result of Rotate -> Flip.
            preview_img = self.base_img.copy()

            # 1. Rotate
            rot = self.edit_state['rotate']
            if rot != 0:
                preview_img = rotate_image(preview_img, rot)
                
            # 2. Flip
            flip = self.edit_state['flip']
            if flip['horizontal']:
                preview_img = flip_image(preview_img, 'horizontal')
            if flip['vertical']:
                preview_img = flip_image(preview_img, 'vertical')
            
            # Apply Adjustments
            for i in range(5):
                state = self.edit_state['adjust'][i]
                if state['val'] != 0:
                    val = state['val']
                    # Pass None for roi to apply globally
                    if i == 0: preview_img = adjust_brightness(preview_img, val, None)
                    elif i == 1: preview_img = blur_image(preview_img, abs(val), None)
                    elif i == 2: preview_img = noise_reduction(preview_img, abs(val), None)
                    elif i == 3: preview_img = adjust_sharpness(preview_img, abs(val), None)
                    elif i == 4: preview_img = adjust_saturation(preview_img, val, None)
            
            # Apply Filter
            if self.edit_state['filter'] != 'original':
                 preview_img = apply_filter(preview_img, self.edit_state['filter'], None)

            roi = select_roi(preview_img, "Select ROI to Crop")
            if roi:
                rect = roi
            else:
                # If Cancelled, revert to original
                self.editor_page.crop_btn_group.button(0).setChecked(True)
                chosen_mode = "original"
        
        self.edit_state['crop']['mode'] = chosen_mode
        self.edit_state['crop']['rect'] = rect
        
        self.run_effect_pipeline()
        self.update_canvas()

    # Rotate
    def bind_rotate(self):
        self.editor_page.rotate_slider.valueChanged.connect(
            self.apply_rotate
        )

    # Apply Rotate
    def apply_rotate(self, value):
        self.edit_state['rotate'] = value
        self.run_effect_pipeline()
        self.update_canvas()

    # Flip
    def bind_flip(self):
        flip_page = self.editor_page.options_stack.widget(2)
        buttons = flip_page.findChildren(QToolButton)

        # Order matches UI: Horizontal, Vertical
        buttons[0].clicked.connect(
            lambda: self.apply_flip("horizontal")
        )
        buttons[1].clicked.connect(
            lambda: self.apply_flip("vertical")
        )

    # Apply Flip
    def apply_flip(self, mode):
        # Toggle flip state
        if mode == "horizontal":
            self.edit_state['flip']['horizontal'] = not self.edit_state['flip']['horizontal']
        elif mode == "vertical":
             self.edit_state['flip']['vertical'] = not self.edit_state['flip']['vertical']

        self.run_effect_pipeline()
        self.update_canvas()

    # Adjust
    def bind_adjust(self):
        for idx in range(self.editor_page.adjust_slider_stack.count()):
            slider = (
                self.editor_page.adjust_slider_stack
                .widget(idx)
                .findChild(type(self.editor_page.rotate_slider))
            )

            slider.valueChanged.connect(
                lambda v, i=idx: self.apply_adjust(i, v)
            )

    # Apply Adjust
    def apply_adjust(self, idx, value):
        # Update state
        self.edit_state['adjust'][idx]['val'] = value
        self.edit_state['adjust'][idx]['roi'] = self.active_roi
        
        # Run pipeline
        self.run_effect_pipeline()
        self.update_canvas()

    # Bind Filter
    def bind_filter(self):
        names = ["original", "bright", "bw", "cool"]

        for btn, name in zip(
            self.editor_page.filter_btn_group.buttons(),
            names
        ):
            btn.clicked.connect(
                lambda _, n=name: self.apply_filter(n)
            )

    # Apply Filter
    def apply_filter(self, name):
        self.edit_state['filter'] = name
        self.run_effect_pipeline()
        self.update_canvas()

    # Bind Text
    def bind_text(self):
        self.editor_page.text_input.textChanged.connect(self.apply_text)
        self.editor_page.rot_input.valueChanged.connect(self.apply_text)
        
        # Connect Custom X/Y inputs for real-time preview
        self.editor_page.x_input.valueChanged.connect(self.apply_text)
        self.editor_page.y_input.valueChanged.connect(self.apply_text)

        for btn in self.editor_page.pos_btn_group.buttons():
            btn.clicked.connect(self.apply_text)

        for btn in self.editor_page.color_group.buttons():
            btn.clicked.connect(self.apply_text)

    # Apply Text
    def apply_text(self):
        text_content = self.editor_page.text_input.text()
        
        # Gather all text params from UI
        pos_btn = self.editor_page.pos_btn_group.checkedButton()
        position = pos_btn.text().lower().replace(" ", "-") if pos_btn else "center"
        
        color_buttons = self.editor_page.color_group.buttons()
        # Safe breakdown for checked button
        checked = self.editor_page.color_group.checkedButton()
        color_index = color_buttons.index(checked) if checked in color_buttons else 0

        color_map = [
            (0, 0, 0),        # Black
            (255, 255, 255),  # White
            (0, 0, 255),      # Red
            (0, 255, 255),    # Yellow
            (0, 165, 255),    # Orange
            (255, 0, 0)       # Blue
        ]

        angle = self.editor_page.rot_input.value()

        custom_xy = None
        if position == "custom":
            custom_xy = (
                self.editor_page.x_input.value(),
                self.editor_page.y_input.value()
            )
            
        # Update State
        self.edit_state['text'] = {
            'content': text_content,
            'position': position,
            'color': color_map[color_index],
            'angle': angle,
            'custom_xy': custom_xy
        }

        # Run pipeline
        self.run_effect_pipeline()
        self.update_canvas()

    # Save Image
    def save_image(self):
        if self.current_img is None:
            return

        from PyQt6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_path:
            # OpenCV saves as BGR, our current_img is already BGR
            cv.imwrite(file_path, self.current_img)
            print(f"Image saved to {file_path}")

    # Logo Clicked
    def on_logo_clicked(self, event):
        # Return to Home Page (Upload Screen)
        self.stack.setCurrentIndex(0)

    # Reset & Save
    def bind_reset_save(self):
        self.editor_page.reset_btn.clicked.connect(self.reset_image)
        self.editor_page.save_btn.clicked.connect(self.save_image)

    # Reset Image
    def reset_image(self):
        self.reset_ui_controls()
        self.run_effect_pipeline()
        self.update_canvas()

# Run the app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
