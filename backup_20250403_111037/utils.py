"""
Utility functions for the steganography application.
"""
import os
import sys
import time
from PIL import Image

def validate_image_path(file_path):
    """
    Validate that the file exists and is a supported image format.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not os.path.exists(file_path):
        return False
    
    try:
        with Image.open(file_path) as img:
            format = img.format.lower() if img.format else ""
            return format in ['png', 'jpg', 'jpeg']
    except:
        return False

def validate_output_path(file_path):
    """
    Validate that the output directory exists and is writable.
    
    Args:
        file_path: Path where output will be written
        
    Returns:
        bool: True if valid, False otherwise
    """
    directory = os.path.dirname(file_path)
    if not directory:  # If no directory is specified, use current directory
        directory = "."
    
    return os.path.isdir(directory) and os.access(directory, os.W_OK)

def display_progress(current, total, bar_length=40):
    """
    Display a progress bar for long operations.
    
    Args:
        current: Current progress value
        total: Total value representing 100%
        bar_length: Length of the progress bar in characters
    """
    progress = min(1.0, float(current) / total)
    arrow = '=' * int(round(bar_length * progress))
    spaces = ' ' * (bar_length - len(arrow))
    
    sys.stdout.write(f"\rProgress: [{arrow}{spaces}] {int(progress * 100)}%")
    sys.stdout.flush()
    
    if progress >= 1.0:
        sys.stdout.write('\n')

def estimate_encoding_capacity(image_path):
    """
    Estimate how many characters can be hidden in the image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        int: Estimated number of characters that can be hidden
    """
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            # Each pixel has 3 color channels (R,G,B) and we use 1 bit per channel
            # 8 bits = 1 character, plus some overhead for the delimiter
            max_bits = width * height * 3
            # Leave some space for the delimiter
            max_chars = (max_bits - 16) // 8
            return max_chars
    except:
        return 0

def is_likely_steganographic_image(image_path):
    """
    Try to determine if the image likely contains hidden data.
    This is a heuristic and not foolproof.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        bool: True if the image likely contains hidden data
    """
    try:
        with Image.open(image_path) as img:
            if img.format.lower() != 'png':
                # JPEG compression disrupts steganography, so if it's not PNG, less likely
                return False
            
            # Check for patterns in LSBs that might indicate hidden data
            img_array = img.convert('RGB')
            pixels = list(img_array.getdata())
            
            # Sample a portion of the image pixels
            sample_size = min(1000, len(pixels))
            lsb_ones = 0
            
            for i in range(sample_size):
                r, g, b = pixels[i]
                # Count LSBs that are 1
                lsb_ones += (r & 1) + (g & 1) + (b & 1)
            
            # Calculate the ratio of 1s in the LSBs
            lsb_ratio = lsb_ones / (sample_size * 3)
            
            # In natural images, the distribution of 0s and 1s in LSBs is roughly equal
            # Significant deviation might indicate steganography
            return 0.45 <= lsb_ratio <= 0.55
    except:
        return False

def safe_text_read(file_path):
    """
    Safely read text from a file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        str: Text content of the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Error reading text file: {str(e)}")
