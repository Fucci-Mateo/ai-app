import logging
from flask import Flask, jsonify, request
import comfy_controllers
import workflows.workflows as workflows
import random
import comfy_controllers
import helpers
from flask_cors import CORS
from PIL import Image
import io
import base64
import json




# Configuration       
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
temporal_files_path='/home/flowingbe/ComfyUI/output/temporal_files'


# Control Functions
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
        logging.info('error parsing request JSON')
        return jsonify(error_response), status_code
    
    # Add random generation id and seed
    data['gen_id']=str(random.randint(0, 10000))
    if 'seed' not in data.keys():
        data['seed']=str(random.randint(0, 999999999999999))

    
    # Format the JSON template with the values
    if 'lightmaskurl' not in data.keys():
        data['lightmaskurl'] = 'https://res.cloudinary.com/dtsxndikq/image/upload/v1721567795/studio.png'
    elif data['lightmaskurl'] == '':
        data['lightmaskurl'] = 'https://res.cloudinary.com/dtsxndikq/image/upload/v1721567795/studio.png'
            
        
    formatted_workflow, error = workflows.format_workflow(workflows.generate,data)
    if error:
       logging.error(error)
       return jsonify({"error": error}), 400
    else:
        print("workflow formatted succesfully")
    
    
    # Push to comfy queue
    comfy_response = comfy_controllers.push_queue(formatted_workflow)
    prompt_id=comfy_response['prompt_id']

    # Check prompt status
    prompt_status = comfy_controllers.check_prompt_status(prompt_id)
    if prompt_status == 'Failed':
        logging.info('Prompt failed: {}'.format(prompt_id))
        return jsonify({"error": "Prompt failed"}), 400
    else:
        logging.info('Prompt finished: {}'.format(prompt_id))
        image_url = helpers.upload_generation_results(data['gen_id']) ## upload result
        logging.info(json.dumps({'image_url': image_url,
                      'prompt_id': prompt_id,
                      'gen_id': data['gen_id']}))
        helpers.defer_delete("resource", data['gen_id'], 500) # Delete the result after 500 seconds
        
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
            result = helpers.couldinary_upload_img_str("data:image/png;base64," + img_str.decode())
            logging.info(json.dumps({'secure_url': result['secure_url'],
                                     'public_id': result['public_id'],
                                     'upload_success': True})
                                     )
            
            helpers.defer_delete("resource", result['public_id'], 100) # Delete the image after 100 seconds
            return jsonify({
                'secure_url': result['secure_url'],
                'public_id': result['public_id']
            }), 200
        
        except Exception as e:
            logging.error(json.dumps({'error': str(e)}) )
            return jsonify({'error': str(e)}), 500
        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9099)