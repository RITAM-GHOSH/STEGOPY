"""
Flask web application for steganography.
"""
import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from werkzeug.utils import secure_filename
from stegano import Steganography, SteganographyError
from utils import estimate_encoding_capacity, is_likely_steganographic_image

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

# Configure file upload settings
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main page of the application."""
    return render_template('index.html')

@app.route('/encode', methods=['GET', 'POST'])
def encode():
    """Handle encoding requests."""
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if the user submitted an empty form
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        # Get the secret message to encode
        message = request.form.get('message', '')
        if not message:
            flash('No message to hide', 'error')
            return redirect(request.url)
        
        # Process the file
        if file and allowed_file(file.filename):
            # Generate a unique filename
            original_filename = secure_filename(file.filename)
            unique_id = str(uuid.uuid4().hex)
            filename = f"{unique_id}_{original_filename}"
            
            # Save the uploaded file
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            # Generate the output filename
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}_encoded.png"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            try:
                # Check if the image has enough capacity
                if not Steganography.can_encode(input_path, message):
                    capacity = estimate_encoding_capacity(input_path)
                    flash(f'Text too large. Max capacity: ~{capacity} characters', 'error')
                    return redirect(request.url)
                
                # Check if authentication is required
                require_auth = request.form.get('requireAuth') == 'true'
                
                # Get the message
                if require_auth:
                    # Encode with authentication
                    output_file, auth_code = Steganography.encode(input_path, message, output_path)
                    session['auth_code'] = auth_code
                else:
                    # Encode without authentication by adding a dummy prefix that doesn't start with AUTH:
                    secured_text = f"NOAUTH:{message}"
                    output_file = Steganography.encode(input_path, secured_text, output_path)[0]
                    session['auth_code'] = None
                
                # Store the output filename in the session
                session['encoded_file'] = output_filename
                
                # Redirect to the download page
                flash('Message successfully encoded!', 'success')
                return redirect(url_for('download_encoded'))
                
            except SteganographyError as e:
                flash(f'Error encoding the message: {str(e)}', 'error')
                return redirect(request.url)
            finally:
                # Clean up the uploaded file
                if os.path.exists(input_path):
                    os.remove(input_path)
        
        else:
            flash('File type not allowed. Please upload a PNG or JPG file.', 'error')
            return redirect(request.url)
    
    # GET request - show the upload form
    return render_template('encode.html')

@app.route('/download-encoded')
def download_encoded():
    """Show the download page for encoded images."""
    encoded_file = session.get('encoded_file')
    auth_code = session.get('auth_code')
    
    if not encoded_file:
        flash('No encoded file available', 'error')
        return redirect(url_for('encode'))
    
    return render_template('download.html', filename=encoded_file, auth_code=auth_code)

@app.route('/decode', methods=['GET', 'POST'])
def decode():
    """Handle decoding requests."""
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if the user submitted an empty form
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        # Process the file
        if file and allowed_file(file.filename):
            # Generate a unique filename
            filename = secure_filename(file.filename)
            unique_id = str(uuid.uuid4().hex)
            filename = f"{unique_id}_{filename}"
            
            # Save the uploaded file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            try:
                # Check if the image likely contains hidden data
                if not is_likely_steganographic_image(file_path):
                    flash('Warning: This image may not contain hidden data', 'warning')
                
                # Try to decode the message (without auth code first)
                result = Steganography.decode(file_path)
                
                # Check if authentication is required
                if isinstance(result, dict) and result.get('auth_required'):
                    # Store the file path in the session for auth checking later
                    session['pending_decode_file'] = file_path
                    # Don't delete the file yet, we'll need it for the actual decoding
                    return redirect(url_for('auth_decode'))
                
                if not result:
                    flash('No hidden message found or message is empty', 'warning')
                    return redirect(request.url)
                
                # Store the decoded message and redirect to the results page
                session['decoded_message'] = result
                
                # Redirect to the results page
                return redirect(url_for('decode_results'))
                
            except SteganographyError as e:
                flash(f'Error decoding the message: {str(e)}', 'error')
                return redirect(request.url)
            finally:
                # Clean up the uploaded file only if we're not going to use it for auth decoding
                if not session.get('pending_decode_file') and os.path.exists(file_path):
                    os.remove(file_path)
        
        else:
            flash('File type not allowed. Please upload a PNG or JPG file.', 'error')
            return redirect(request.url)
    
    # GET request - show the upload form
    return render_template('decode.html')

@app.route('/auth-decode', methods=['GET', 'POST'])
def auth_decode():
    """Handle authentication for protected messages."""
    # Check if there's a pending decode
    file_path = session.get('pending_decode_file')
    if not file_path:
        flash('No image to decode', 'error')
        return redirect(url_for('decode'))
    
    if request.method == 'POST':
        # Get the auth code from the form
        auth_code = request.form.get('auth_code')
        if not auth_code:
            flash('Please enter the authentication code', 'error')
            return redirect(url_for('auth_decode'))
        
        try:
            # Decode with the auth code
            extracted_text = Steganography.decode(file_path, auth_code)
            
            # Store the decoded message
            session['decoded_message'] = extracted_text
            
            # Clean up
            if os.path.exists(file_path):
                os.remove(file_path)
            session.pop('pending_decode_file', None)
            
            # Redirect to results
            return redirect(url_for('decode_results'))
            
        except SteganographyError as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('auth_decode'))
    
    # GET request - show the auth form
    return render_template('auth_decode.html')

@app.route('/decode-results')
def decode_results():
    """Show the results of decoding."""
    message = session.get('decoded_message')
    if not message:
        flash('No decoded message available', 'error')
        return redirect(url_for('decode'))
    
    return render_template('results.html', message=message)

@app.route('/download/<filename>')
def download_file(filename):
    """Handle file downloads."""
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

@app.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(413)
def file_too_large(e):
    """Handle file size exceeded error."""
    flash('The file is too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def server_error(e):
    """Handle server errors."""
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)