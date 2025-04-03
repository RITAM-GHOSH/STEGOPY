"""
Command-line interface for the steganography application.
"""
import argparse
import os
import sys
import logging
from stegano import Steganography, SteganographyError
from utils import (
    validate_image_path, 
    validate_output_path, 
    display_progress, 
    estimate_encoding_capacity,
    is_likely_steganographic_image,
    safe_text_read
)

def parse_arguments():
    """
    Parse command-line arguments for the steganography application.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="StegaPy - A Python-based steganography tool for hiding text in images",
        epilog="Example: python main.py -e -i input.png -t 'Secret message' -o output.png"
    )
    
    # Create group for encoding and decoding operations
    operation_group = parser.add_mutually_exclusive_group(required=True)
    operation_group.add_argument('-e', '--encode', action='store_true', help='Encode text into an image')
    operation_group.add_argument('-d', '--decode', action='store_true', help='Decode text from an image')
    
    # Image input is always required
    parser.add_argument('-i', '--image', required=True, help='Path to the input image')
    
    # Text argument for encoding
    text_group = parser.add_mutually_exclusive_group()
    text_group.add_argument('-t', '--text', help='Text to encode in the image')
    text_group.add_argument('-f', '--file', help='Text file containing data to encode')
    
    # Output image path for encoding
    parser.add_argument('-o', '--output', help='Path for the output image (encoding only)')
    
    # Additional options
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--capacity', action='store_true', help='Show the image capacity without encoding/decoding')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.encode and not (args.text or args.file):
        parser.error("Encoding requires either --text or --file argument")
    
    if args.output and not args.encode:
        parser.error("--output can only be used with --encode")
    
    return args

def show_capacity(image_path):
    """
    Show the estimated capacity of the image for steganography.
    
    Args:
        image_path: Path to the image file
    """
    if not validate_image_path(image_path):
        print(f"Error: '{image_path}' is not a valid image file or is not supported.")
        sys.exit(1)
    
    capacity = estimate_encoding_capacity(image_path)
    print(f"Image capacity: Approximately {capacity} characters")

def run_encode(args):
    """
    Run the encoding operation.
    
    Args:
        args: Command-line arguments
    """
    # Validate input image
    if not validate_image_path(args.image):
        print(f"Error: '{args.image}' is not a valid image file or is not supported.")
        sys.exit(1)
    
    # Get text to encode
    text = ""
    if args.text:
        text = args.text
    elif args.file:
        try:
            text = safe_text_read(args.file)
        except Exception as e:
            print(f"Error reading text file: {str(e)}")
            sys.exit(1)
    
    # Validate output path if provided
    if args.output and not validate_output_path(args.output):
        print(f"Error: Cannot write to '{args.output}'. Check directory permissions.")
        sys.exit(1)
    
    # Check capacity
    try:
        if not Steganography.can_encode(args.image, text):
            print("Error: Text is too large for this image.")
            capacity = estimate_encoding_capacity(args.image)
            print(f"Maximum capacity: ~{capacity} characters. Your text: {len(text)} characters")
            sys.exit(1)
    except SteganographyError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    
    # Encode the message
    try:
        print("Encoding message into image...")
        output_path = Steganography.encode(args.image, text, args.output)
        print(f"Success! Encoded image saved at: {output_path}")
    except SteganographyError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def run_decode(args):
    """
    Run the decoding operation.
    
    Args:
        args: Command-line arguments
    """
    # Validate input image
    if not validate_image_path(args.image):
        print(f"Error: '{args.image}' is not a valid image file or is not supported.")
        sys.exit(1)
    
    # Check if image likely contains hidden data
    if not is_likely_steganographic_image(args.image):
        print("Warning: This image may not contain hidden data or uses a different steganography method.")
    
    # Decode the message
    try:
        print("Extracting hidden message from image...")
        extracted_text = Steganography.decode(args.image)
        
        if not extracted_text:
            print("No hidden message found or message is empty.")
            sys.exit(0)
        
        print("\nExtracted message:")
        print("-" * 40)
        print(extracted_text)
        print("-" * 40)
    except SteganographyError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def main():
    """Main entry point for the CLI application."""
    args = parse_arguments()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    # Show capacity if requested
    if args.capacity:
        show_capacity(args.image)
        sys.exit(0)
    
    # Run appropriate operation
    if args.encode:
        run_encode(args)
    elif args.decode:
        run_decode(args)

if __name__ == "__main__":
    main()
