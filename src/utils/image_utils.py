import cv2
import numpy as np
from PIL import Image

def load_image(file_path):
    """Load an image from file, handling both regular images and HEIC format."""
    if file_path.lower().endswith('.heic'):
        try:
            # Open HEIC image with Pillow
            pil_image = Image.open(file_path)
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            # Convert to numpy array
            return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"Error loading HEIC image: {e}")
            return None
    else:
        # Handle regular images with OpenCV
        image = cv2.imread(file_path)
        if image is not None:
            # Convert from BGR to RGB for display
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return None

def correct_perspective(image, points):
    """Apply free transformation to the image using the given points."""
    if len(points) != 4:
        return None
        
    # Define source points (in clockwise order)
    src_points = np.float32(points)
    
    # Calculate destination points
    # Find the width and height of the rectangle
    width = max(
        np.linalg.norm(src_points[1] - src_points[0]),
        np.linalg.norm(src_points[3] - src_points[2])
    )
    height = max(
        np.linalg.norm(src_points[2] - src_points[1]),
        np.linalg.norm(src_points[3] - src_points[0])
    )
    
    # Define destination points
    dst_points = np.float32([
        [0, 0],
        [width, 0],
        [width, height],
        [0, height]
    ])
    
    # Calculate perspective transform matrix
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    
    # Apply perspective transform
    return cv2.warpPerspective(image, matrix, (int(width), int(height)))

def rotate_image(image, clockwise=True):
    """Rotate the image 90 degrees in the specified direction."""
    if clockwise:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
