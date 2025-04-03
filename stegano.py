"""
Core steganography functionality for hiding and extracting text in images.
"""
import os
import numpy as np
from PIL import Image
import logging
import random
import hashlib

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class SteganographyError(Exception):
    """Custom exception for steganography operations."""
    pass

class Steganography:
    """
    Class that provides methods for encoding and decoding text in images.
    """
    
    @staticmethod
    def generate_auth_code():
        """
        Generate a random 4-digit authentication code.
        
        Returns:
            str: 4-digit authentication code
        """
        return str(random.randint(1000, 9999))
    
    @staticmethod
    def verify_auth_code(input_code, stored_code):
        """
        Verify if the input authentication code matches the stored code.
        
        Args:
            input_code: Code provided by the user
            stored_code: Original code generated during encoding
            
        Returns:
            bool: True if codes match, False otherwise
        """
        return input_code == stored_code
    
    @staticmethod
    def text_to_binary(text):
        """Convert text to binary representation."""
        if not text:
            return ""
        binary = ''.join(format(ord(char), '08b') for char in text)
        # Add delimiter to know where the text ends
        binary += '1111111111111110'  # 16-bit delimiter
        return binary
    
    @staticmethod
    def binary_to_text(binary):
        """Convert binary representation back to text."""
        if not binary:
            return ""
        
        # Look for the delimiter
        delimiter_index = binary.find('1111111111111110')
        if delimiter_index != -1:
            binary = binary[:delimiter_index]
        
        # Process 8 bits at a time to recover characters
        text = ""
        for i in range(0, len(binary), 8):
            if i + 8 <= len(binary):
                byte = binary[i:i+8]
                text += chr(int(byte, 2))
        return text
    
    @staticmethod
    def can_encode(image_path, text):
        """
        Check if the image has enough capacity to encode the text.
        
        Args:
            image_path: Path to the image file
            text: Text to encode
            
        Returns:
            bool: True if the image can store the text, False otherwise
        """
        try:
            with Image.open(image_path) as img:
                # Get image dimensions
                width, height = img.size
                
                # Calculate max capacity (3 color channels, 1 bit per channel)
                max_bits = width * height * 3 * 1
                
                # Calculate required bits (8 bits per character + delimiter)
                required_bits = len(text) * 8 + 16  # 16 bits for delimiter
                
                return max_bits >= required_bits
        except Exception as e:
            raise SteganographyError(f"Error checking image capacity: {str(e)}")
    
    @staticmethod
    def encode(image_path, text, output_path=None):
        """
        Hide text data within an image and generate a 4-digit auth code.
        
        Args:
            image_path: Path to the original image
            text: Text to hide in the image
            output_path: Path to save the steganographic image
            
        Returns:
            tuple: (Path to the output image, authentication code)
        """
        try:
            if not text:
                raise SteganographyError("No text provided for encoding")
            
            # Generate the 4-digit authentication code
            auth_code = Steganography.generate_auth_code()
            
            # Add the auth code as a prefix to the text with a separator
            secured_text = f"AUTH:{auth_code}:{text}"
            
            # Prepare output path
            if not output_path:
                name, ext = os.path.splitext(image_path)
                # Force PNG format to avoid compression issues
                output_path = f"{name}_encoded.png"
            
            # Check if we can encode the text in the image
            if not Steganography.can_encode(image_path, secured_text):
                raise SteganographyError("Text is too large for this image")
            
            # Open image and convert to RGB
            with Image.open(image_path) as img:
                # Convert image to RGB if not already
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Get image as numpy array
                img_array = np.array(img)
                height, width, channels = img_array.shape
                
                # Convert text to binary
                binary_text = Steganography.text_to_binary(secured_text)
                
                # Flatten the image array for easier looping
                flattened = img_array.reshape(-1)
                
                # Counter for binary text position
                binary_index = 0
                binary_length = len(binary_text)
                
                # Loop through pixels and hide data
                for i in range(0, len(flattened), 1):
                    if binary_index < binary_length:
                        # LSB encoding: Replace the least significant bit
                        if binary_text[binary_index] == '1':
                            # Set LSB to 1 (ensure it's 1)
                            if flattened[i] % 2 == 0:  # If LSB is 0
                                flattened[i] += 1
                        else:
                            # Set LSB to 0 (ensure it's 0)
                            if flattened[i] % 2 == 1:  # If LSB is 1
                                flattened[i] -= 1
                        
                        binary_index += 1
                    else:
                        # We've encoded all our data
                        break
                
                # Reshape back to original dimensions
                img_array_modified = flattened.reshape(height, width, channels)
                
                # Create a new image from the modified array
                encoded_img = Image.fromarray(img_array_modified.astype('uint8'), 'RGB')
                
                # Save the image
                encoded_img.save(output_path)
                
                # Return both the path and the authentication code
                return output_path, auth_code
                
        except SteganographyError as e:
            raise e
        except Exception as e:
            raise SteganographyError(f"Error encoding message: {str(e)}")
    
    @staticmethod
    def decode(image_path, auth_code=None):
        """
        Extract hidden text from a steganographic image with authentication.
        
        Args:
            image_path: Path to the steganographic image
            auth_code: Optional authentication code for decoding
            
        Returns:
            str or tuple: Extracted text or auth_required flag with auth code
        """
        try:
            # Open the image
            with Image.open(image_path) as img:
                # Convert image to RGB if not already
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Get image as numpy array
                img_array = np.array(img)
                
                # Flatten the array
                flattened = img_array.reshape(-1)
                
                # Extract the LSB from each byte
                binary_message = ""
                for i in range(len(flattened)):
                    binary_message += str(flattened[i] & 1)
                    
                    # Look for the delimiter as we go to stop early if possible
                    if len(binary_message) >= 16 and binary_message[-16:] == '1111111111111110':
                        binary_message = binary_message[:-16]  # Remove the delimiter
                        break
                
                # Convert binary back to text
                full_text = Steganography.binary_to_text(binary_message)
                
                # Check if the text has authentication information
                if full_text.startswith("AUTH:"):
                    parts = full_text.split(":", 2)
                    if len(parts) == 3:
                        stored_auth_code = parts[1]
                        actual_message = parts[2]
                        
                        # If no auth code is provided, return a flag indicating auth is required
                        if auth_code is None:
                            return {"auth_required": True, "stored_code": stored_auth_code}
                        
                        # Verify the authentication code
                        if Steganography.verify_auth_code(auth_code, stored_auth_code):
                            return actual_message
                        else:
                            raise SteganographyError("Invalid authentication code")
                
                # Handle the NOAUTH case (messages explicitly encoded without auth)
                elif full_text.startswith("NOAUTH:"):
                    parts = full_text.split(":", 1)
                    if len(parts) == 2:
                        return parts[1]
                
                # If there's no authentication code in the text, return it as is
                return full_text
                
        except Exception as e:
            raise SteganographyError(f"Error decoding message: {str(e)}")
