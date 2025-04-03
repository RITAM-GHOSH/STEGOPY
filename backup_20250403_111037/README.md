# StegaPy - Python Steganography Tool

StegaPy is a steganography application for hiding and extracting text data within images. It uses least significant bit (LSB) steganography to embed text in image files with minimal visual impact. The application includes both a command-line interface and a web-based interface.

## Features

- Hide text messages within common image formats (PNG, JPG)
- Extract hidden text from steganographic images
- Preservation of image quality while embedding data
- Capacity estimation for images
- Support for both direct text input and text files
- Progress indicators for long operations
- Comprehensive error handling
- User-friendly web interface
- Real-time capacity checking

## Requirements

- Python 3.x
- Flask (for web interface)
- Pillow (PIL Fork)
- NumPy
- Gunicorn (for deploying web interface)

## Web Interface

The web interface provides an easy-to-use option for encoding and decoding messages without needing to use the command line. To run the web application:

```
gunicorn --bind 0.0.0.0:5000 main:app
```

Then navigate to http://localhost:5000 in your browser.

The web interface features:
- Simple file upload for images
- Text input for messages to hide
- Automatic capacity checking
- Direct download of encoded images
- Clean display of decoded messages

## Command-Line Usage

### Basic Commands

**Hide text in an image:**
