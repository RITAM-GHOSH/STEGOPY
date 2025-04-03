# StegaPy - Python Steganography Tool

StegaPy is a steganography application for hiding and extracting text data within images. It uses least significant bit (LSB) steganography to embed text in image files with minimal visual impact. The application includes both a command-line interface and a web-based interface.

## Features

- Hide text messages within common image formats (PNG, JPG)
- Extract hidden text from steganographic images
- Preservation of image quality while embedding data
- Optional authentication with 4-digit codes for secure message sharing
- Capacity estimation for images
- Support for both direct text input and text files
- Comprehensive error handling
- User-friendly web interface
- Real-time capacity checking

## Setup Instructions for VS Code

### Prerequisites

- Python 3.8 or higher
- Visual Studio Code
- Git (optional, for cloning the repository)

### Required Libraries

```
flask==2.0.1
flask-sqlalchemy==3.0.0
gunicorn==23.0.0
numpy==1.23.5
pillow==10.0.0
psycopg2-binary==2.9.5
email-validator==2.0.0
```

### Installation Steps

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   # Or download and extract the ZIP file
   ```

2. **Open the project in VS Code**
   ```bash
   cd steganography-app
   code .
   ```

3. **Set up a virtual environment (recommended)**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install the required packages**
   ```bash
   # Install each package individually
   pip install flask==2.0.1
   pip install flask-sqlalchemy==3.0.0
   pip install gunicorn==23.0.0
   pip install numpy==1.23.5
   pip install pillow==10.0.0
   pip install psycopg2-binary==2.9.5
   pip install email-validator==2.0.0
   
   # Or if you have a requirements.txt file:
   # pip install -r requirements.txt
   ```

5. **Create necessary folders**
   ```bash
   mkdir -p uploads outputs
   ```

### Running the Application in VS Code

#### 1. Run the Web Interface

- **Option 1: Using Flask's development server**
   ```bash
   # Windows
   $env:FLASK_APP = "main.py"
   $env:FLASK_ENV = "development"
   flask run --host=0.0.0.0 --port=5000

   # macOS/Linux
   export FLASK_APP=main.py
   export FLASK_ENV=development
   flask run --host=0.0.0.0 --port=5000
   ```

- **Option 2: Using Gunicorn (recommended for Linux/macOS)**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

- **Option 3: Run directly from Python**
   ```bash
   python main.py
   ```

- Then navigate to http://localhost:5000 in your browser

#### 2. Using the Command-Line Interface

You can use the CLI tool instead of the web interface:

```bash
# Hide a message in an image
python cli.py -e -i input.png -t "Your secret message" -o output.png

# Extract a message from an image
python cli.py -d -i encoded_image.png

# Extract a message that requires authentication
python cli.py -d -i encoded_image.png -a 1234  # Where 1234 is the auth code

# Check image capacity
python cli.py --capacity -i input.png
```

## Using the Web Interface

The web interface features:
- Simple file upload for images
- Text input for messages to hide
- Option to enable/disable authentication with 4-digit codes
- Automatic capacity checking
- Direct download of encoded images
- Clean display of decoded messages

### Authentication Feature

When enabled:
1. A random 4-digit code is generated when you encode a message
2. You must share this code with the recipient
3. The recipient needs to enter this code to decode the message

## Command-Line Usage

### Basic Commands

```bash
# Encode a message
python cli.py -e -i input.png -t "Your secret message" -o output.png

# Decode a message
python cli.py -d -i encoded_image.png

# Check image capacity
python cli.py --capacity -i input.png
```

## Project Structure

```
steganography-app/
├── cli.py                 # Command-line interface for the application
├── main.py                # Flask web application
├── stegano.py             # Core steganography algorithms
├── utils.py               # Utility functions
├── backup.py              # Script for creating backups
├── export_code.py         # Script for exporting code
├── templates/             # Web interface HTML templates
│   ├── base.html          # Base template with common elements
│   ├── index.html         # Home page
│   ├── encode.html        # Page for encoding messages
│   ├── decode.html        # Page for decoding messages
│   ├── auth_decode.html   # Authentication page for protected messages
│   ├── download.html      # Download page for encoded images
│   ├── results.html       # Page showing decoded message results
│   ├── about.html         # About page
│   ├── 404.html           # 404 error page
│   └── 500.html           # 500 error page
├── uploads/               # Temporary storage for uploaded images
└── outputs/               # Storage for encoded images
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```
   ModuleNotFoundError: No module named 'numpy'
   ```
   Solution: Make sure you've installed all required packages with the commands in the Installation section.

2. **Permission Issues**
   ```
   PermissionError: [Errno 13] Permission denied: 'uploads/'
   ```
   Solution: Ensure the application has write permissions to the uploads and outputs directories.
   ```bash
   chmod 755 uploads outputs
   ```

3. **Port Already in Use**
   ```
   OSError: [Errno 98] Address already in use
   ```
   Solution: Change the port number or find and terminate the process using the current port.
   ```bash
   # Find the process using port 5000
   lsof -i :5000
   # Kill the process
   kill <PID>
   ```

4. **Import Errors in VS Code**
   If VS Code shows import errors but the application runs fine, you may need to select the correct Python interpreter:
   1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
   2. Type "Python: Select Interpreter"
   3. Choose the interpreter from your virtual environment

## Security Considerations

- StegaPy uses LSB (Least Significant Bit) steganography, which is effective for casual use but may not be suitable for high-security applications.
- The 4-digit authentication code adds a basic layer of security but is not encryption.
- For high-security applications, consider using additional encryption methods before encoding.
- Always use secure channels to share the authentication code with recipients.

## Conclusion

StegaPy provides a simple yet effective way to hide text messages within images. This tool can be useful for:
- Educational purposes to learn about steganography
- Sending hidden messages to friends or colleagues
- Adding watermarks or metadata to images
- Basic information hiding for privacy needs

For any issues, feature requests, or contributions, please contact the repository maintainer.

## License

[MIT License](LICENSE)
