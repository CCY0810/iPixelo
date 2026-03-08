# SECV3213 Fundamental of Image Processing
# Assignment 3: Course Project
# iPixelo: A Mobile-Inspired Image Editing and Enhancement Application
# Group Name: Innovators
# Group Member: 1. Chuah Chun Yi    A23CS0070
#               2. Chong Jun Hong   A23CS0066
#               3. Tai Yi Tian      A23CS0272

import cv2 as cv
import numpy as np

# ROI Selection
def select_roi(img, title="Select ROI"):
    # Select ROI
    roi = cv.selectROI(title, img, showCrosshair=True, fromCenter=False)
    
    # Close ROI window
    cv.destroyWindow(title)
    
    # Allow OpenCV to process any pending events
    cv.waitKey(1)
    
    # Check if ROI selection is selected
    if roi == (0, 0, 0, 0):
        return None
    
    return roi


# Resize image to fit within the screen
def resize_image(img):
    # Set maximum size for width and height
    max_size=900
    # Get current image dimensions
    h, w = img.shape[:2]
    # Compute scaling factor
    scale = min(1.0, max_size / max(h, w))
    # Resize image if necessary
    if scale < 1.0:
        return cv.resize(img, (int(w * scale), int(h * scale)))
    return img


# =============
# 1. Crop Image
# =============
def crop_image(img, mode, custom_rect=None):
    result = img.copy()

    # 16:9 aspect ratio
    if mode == "16:9":
        # Get image dimensions
        h, w = img.shape[:2]
        aspect = 16 / 9

    # 4:3 aspect ratio
    elif mode == "4:3":
        # Get image dimensions
        h, w = img.shape[:2]
        aspect = 4 / 3

    # Custom aspect ratio
    elif mode == "custom":
        if custom_rect is None:
             return img
        
        x, y, cw, ch = custom_rect
        return img[y:y+ch, x:x+cw]

    # Original aspect ratio
    else:
        return img

    # Calculate new dimensions based on aspect ratio
    if w / h > aspect:
        new_w = int(h * aspect)
        new_h = h
    else:
        new_w = w
        new_h = int(w / aspect)

    # Calculate center of image
    x = (w - new_w) // 2
    y = (h - new_h) // 2

    # Crop image based on new dimensions
    return img[y:y+new_h, x:x+new_w]


# ===============
# 2. Rotate Image
# ===============
def rotate_image(img, angle):
    # Get image dimensions
    h, w = img.shape[:2]
    # Calculate center of image
    center = (w // 2, h // 2)
    # Get rotation matrix
    M = cv.getRotationMatrix2D(center, angle, 1.0)
    # Apply rotation
    return cv.warpAffine(img, M, (w, h))


# =============
# 3. Flip Image
# =============
def flip_image(img, mode):
    # Flip image horizontally
    if mode == "horizontal":
        return cv.flip(img, 1)
    
    # Flip image vertically 
    elif mode == "vertical":
        return cv.flip(img, 0)
    
    return img


# ====================
# 4. Adjust Brightness
# ====================
def adjust_brightness(img, level, roi=None):
    brightness = level
    # Calculate brightness factor
    factor = 1 + (brightness / 100.0)
    result = img.copy()

    # Apply brightness adjustment to selected region
    if roi:
        # Get ROI dimensions
        x, y, w, h = roi
        # Apply brightness adjustment to selected region
        region = result[y:y+h, x:x+w].astype(np.float32)
        region *= factor
        # Clip values to valid range
        result[y:y+h, x:x+w] = np.clip(region, 0, 255).astype(np.uint8)
    
    # Apply brightness adjustment to entire image
    else:
        # Clip values to valid range
        result = np.clip(img.astype(np.float32) * factor, 0, 255).astype(np.uint8)

    return result


# =============
# 5. Blur Image
# =============
def blur_image(img, level, roi=None):
    result = img.copy()

    # Compute kernel size
    if level > 0:
        ksize = (level * 2 + 1, level * 2 + 1)

        # Apply Gaussian blur to selected region
        if roi:
            # Get ROI dimensions
            x, y, w, h = roi
            result[y:y+h, x:x+w] = cv.GaussianBlur(result[y:y+h, x:x+w], ksize, 0)
        
        # Apply Gaussian blur to entire image
        else:
            result = cv.GaussianBlur(img, ksize, 0)

    return result


# ==================
# 6. Noise Reduction
# ==================
def noise_reduction(img, level, roi=None):
    result = img.copy()

    # Compute d and sigma
    if level > 0:
        d = 9
        sigma = level * 5

        # Apply bilateral filter to selected region
        if roi:
            # Get ROI dimensions
            x, y, w, h = roi
            result[y:y+h, x:x+w] = cv.bilateralFilter(result[y:y+h, x:x+w], d, sigma, sigma)
        
        # Apply bilateral filter to entire image
        else:
            result = cv.bilateralFilter(img, d, sigma, sigma)

    return result


# ==================
# 7. Adjust Sharpness
# ==================
def adjust_sharpness(img, level, roi=None):
    result = img.copy()

    # Compute alpha
    if level > 0:
        alpha = level / 10.0

        # Apply sharpening to selected region
        if roi:
            # Get ROI dimensions
            x, y, w, h = roi
            # Get ROI region
            roi_region = result[y:y+h, x:x+w]
            # Apply Gaussian blur
            blur = cv.GaussianBlur(roi_region, (3, 3), 1.0)
            # Apply Sharpening
            result[y:y+h, x:x+w] = cv.addWeighted(roi_region, 1.0 + alpha, blur, -alpha, 0)
        
        # Apply sharpening to entire image
        else:
            # Apply Gaussian blur
            blur = cv.GaussianBlur(result, (3, 3), 1.0)
            # Apply Sharpening
            result = cv.addWeighted(result, 1.0 + alpha, blur, -alpha, 0)

    return result


# ==================
# 8. Adjust Saturation
# ==================
def adjust_saturation(img, level, roi=None):
    # Compute saturation factor
    saturation = level
    factor = 1.0 + (saturation / 100.0)
    result = img.copy()

    # Apply saturation adjustment to selected region
    if roi:
        # Get ROI dimensions
        x, y, w, h = roi
        # Convert ROI to HSV
        hsv_roi = cv.cvtColor(result[y:y+h, x:x+w], cv.COLOR_BGR2HSV).astype(np.float32)
        # Adjust saturation channel
        hsv_roi[..., 1] = np.clip(hsv_roi[..., 1] * factor, 0, 255)
        # Convert back to BGR and update result
        result[y:y+h, x:x+w] = cv.cvtColor(hsv_roi.astype(np.uint8), cv.COLOR_HSV2BGR)
    
    # Apply saturation adjustment to entire image
    else: 
        # Convert entire image to HSV
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV).astype(np.float32)
        # Adjust saturation channel
        hsv[..., 1] = np.clip(hsv[..., 1] * factor, 0, 255)
        # Convert back to BGR
        result = cv.cvtColor(hsv.astype(np.uint8), cv.COLOR_HSV2BGR)

    return result


# ===============
# 9. Apply Filter
# ================
def apply_filter(img, filter_name, roi=None):
    result = img.copy()

    if roi:
        x, y, w, h = roi
        region = result[y:y + h, x:x + w]
        
        if filter_name == "bright":
            region = cv.convertScaleAbs(region, alpha=1.15, beta=5)
        elif filter_name == "b&w" or filter_name == "bw":
            gray = cv.cvtColor(region, cv.COLOR_BGR2GRAY)
            region = cv.cvtColor(gray, cv.COLOR_GRAY2BGR)
        elif filter_name == "cool":
            cool = region.astype(np.float32)
            cool[:, :, 0] += 20
            cool[:, :, 2] -= 12
            region = np.clip(cool, 0, 255).astype(np.uint8)
            
        result[y:y + h, x:x + w] = region
        
    else:
        if filter_name == "bright":
            result = cv.convertScaleAbs(result, alpha=1.15, beta=5)
        elif filter_name == "b&w" or filter_name == "bw":
            gray = cv.cvtColor(result, cv.COLOR_BGR2GRAY)
            result = cv.cvtColor(gray, cv.COLOR_GRAY2BGR)
        elif filter_name == "cool":
            cool = result.astype(np.float32)
            cool[:, :, 0] += 20
            cool[:, :, 2] -= 12
            result = np.clip(cool, 0, 255).astype(np.uint8)

    return result


# ============
# 10. Add Text
# ============
def add_text(img, text, position, color_bgr, angle, custom_xy=None):
    h, w = img.shape[:2]
    result = img.copy()

    (tw, th), _ = cv.getTextSize(text, cv.FONT_HERSHEY_SIMPLEX, 2, 4)
    margin = 20

    positions = {
        "top-left": (margin, margin + th),
        "top-center": ((w - tw) // 2, margin + th),
        "top-right": (w - tw - margin, margin + th),
        "mid-left": (margin, (h + th) // 2),
        "center": ((w - tw) // 2, (h + th) // 2),
        "mid-right": (w - tw - margin, (h + th) // 2),
        "bot-left": (margin, h - margin),
        "bot-center": ((w - tw) // 2, h - margin),
        "bot-right": (w - tw - margin, h - margin)
    }

    if position == "custom" and custom_xy:
        x, y = custom_xy
    else:
        x, y = positions[position]

    mask = np.zeros((h, w), dtype=np.uint8)
    overlay = np.zeros_like(result)

    cv.putText(mask, text, (x, y), cv.FONT_HERSHEY_SIMPLEX, 2, 255, 4, cv.LINE_AA)
    cv.putText(overlay, text, (x, y), cv.FONT_HERSHEY_SIMPLEX, 2, color_bgr, 4, cv.LINE_AA)

    # Calculate center of the text for rotation pivot
    # putText origin (x,y) is bottom-left of the text
    # Bounding box is approximately (x, y - th) to (x + tw, y)
    cx = x + tw // 2
    cy = y - th // 2
    
    M = cv.getRotationMatrix2D((cx, cy), angle, 1.0)
    mask_r = cv.warpAffine(mask, M, (w, h))
    overlay_r = cv.warpAffine(overlay, M, (w, h))

    # Bitwise operations
    bg = cv.bitwise_and(result, result, mask=cv.bitwise_not(mask_r))
    fg = cv.bitwise_and(overlay_r, overlay_r, mask=mask_r)

    return cv.add(bg, fg)

# Run main.py
if __name__ == "__main__":
    import os
    import subprocess
    import sys

    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(current_dir, "main.py")
    subprocess.run([sys.executable, main_script])