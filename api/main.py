from flask import Flask, jsonify, request
import comfy_controllers
import workflows.workflows as workflows
import random
import comfy_controllers
import helpers
import os
import json
import cloudinary_api
from flask_cors import CORS
from PIL import Image
import io
import base64
from credentials import creds
import cloudinary
import cloudinary.uploader



# Configuration       
cloudinary.config( 
    cloud_name = creds['CLOUDINARY_CLOUDNAME'], 
    api_key = creds['CLOUDINARY_API_KEY'], 
    api_secret = creds['CLOUDINARY_API_SECRET'], # Click 'View Credentials' below to copy your API secret
    secure=True
)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
temporal_files_path='/home/flowingbe/ComfyUI/output/temporal_files'


def parse_and_validate_post_request(request):
    data = request.get_json()  # Parse the incoming JSON data
    if not data:
        return None, {"error": "Invalid JSON"}, 400
    return data, None, None


@app.route('/generate', methods=['POST'])
def generate():
    # Validate Post request

    
    data, error_response, status_code = parse_and_validate_post_request(request)
    if error_response:
        return jsonify(error_response), status_code
    
    # Add random generation id and seed
    data['gen_id']=str(random.randint(0, 10000))

    if 'seed' not in data.keys():
        data['seed']=str(random.randint(0, 999999999999999))

    
    # Format the JSON template with the values
    if 'lightmaskurl' not in data.keys():
        data['lightmaskurl'] = 'https://res.cloudinary.com/dtsxndikq/image/upload/v1721567795/studio.png'
        
    formatted_workflow, error = workflows.format_workflow(workflows.generate,data)
    
    if error:
       return jsonify({"error": error}), 400
    else:
        print("suceeded")
    
    
    # Push to comfy queue
    comfy_response = comfy_controllers.push_queue(formatted_workflow)
    

    
    prompt_id=comfy_response['prompt_id']

    # Check prompt status
    prompt_status = comfy_controllers.check_prompt_status(prompt_id)
    if prompt_status == 'Failed':
        return jsonify({"error": "Prompt failed"}), 400
    else:
        image_url = helpers.upload_generation_results(data['gen_id'])
        return jsonify({'image_url': image_url})
    

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    if request.method == 'OPTIONS':
        # Handles preflight requests
        return '', 204
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        try:
            # Read the binary data
            image_binary = file.read()
            
            # Open the image using PIL
            image = Image.open(io.BytesIO(image_binary))
            
            
            # Convert the image back to binary
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue())
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload("data:image/png;base64," + img_str.decode())
            
            return jsonify({
                'secure_url': result['secure_url'],
                'public_id': result['public_id']
            }), 200
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9099, debug=True)