from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import logging
import traceback
from chatbot_logic import process_message
from pdf_generator import generate_resume_pdf_simple

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Set up logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Directory for storing resumes
RESUME_DIR = os.path.join(os.getcwd(), 'resumes')
os.makedirs(RESUME_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        logging.debug(f"Received user message: {user_message}")
        
        # Process the message and get response
        chatbot_response, resume_data = process_message(user_message)
        
        response = {
            'reply': chatbot_response,
            'resume_data': resume_data  # This can be None or dict
        }
        
        logging.debug(f"Sending response: {response}")
        return jsonify(response)
    except Exception as e:
        error_msg = f"Error in /api/chat: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return jsonify({
            'error': 'An internal server error occurred',
            'details': str(e)
        }), 500

@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    try:
        resume_data = request.json.get('resume_data')
        
        if not resume_data:
            logging.error("No resume data provided in request")
            return jsonify({'error': 'No resume data provided'}), 400
        
        logging.debug(f"Resume data received: {json.dumps(resume_data, indent=2)}")
        
        # Generate a unique filename
        output_file = f"resume_{hash(str(resume_data))}.pdf"
        file_path = os.path.join(RESUME_DIR, output_file)
        
        logging.debug(f"Generating PDF at path: {file_path}")
        
        # Generate PDF
        pdf_path = generate_resume_pdf_simple(resume_data, output_file=file_path)
        
        if pdf_path and os.path.exists(pdf_path):
            logging.info(f"PDF generated successfully at: {pdf_path}")
            return jsonify({
                'success': True,
                'message': 'Resume generated successfully',
                'download_url': f'/download-resume/{os.path.basename(pdf_path)}'
            })
        else:
            logging.error("PDF generation failed - returned None or file does not exist")
            return jsonify({
                'success': False,
                'message': 'Failed to generate resume'
            }), 500
    except Exception as e:
        error_msg = f"Error generating resume: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return jsonify({
            'success': False,
            'message': f'Error generating resume: {str(e)}'
        }), 500

@app.route('/download-resume/<filename>')
def download_resume(filename):
    try:
        file_path = os.path.join(RESUME_DIR, filename)
        logging.debug(f"Attempting to send file: {file_path}")
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return jsonify({
                'error': 'Resume file not found',
                'details': 'The requested file does not exist'
            }), 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        error_msg = f"Error downloading file: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return jsonify({
            'error': 'Failed to download resume',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 