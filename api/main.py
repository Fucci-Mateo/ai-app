from flask import Flask, jsonify, request
import comfy_controllers
import workflows.workflows as workflows
import random
import comfy_controllers
import helpers
import os
import json

app = Flask(__name__)
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
    
    formatted_workflow, error = workflows.format_workflow(workflows.generate,data)
    if error:
       return jsonify({"error": error}), 400
       
    
    
    # Push to comfy queue
    comfy_response = comfy_controllers.push_queue(formatted_workflow)
    

    
    prompt_id=comfy_response['prompt_id']

    # Check prompt status
    prompt_status = comfy_controllers.check_prompt_status(prompt_id)
    if prompt_status == 'Failed':
        return jsonify({"error": "Prompt failed"}), 400
    else:
        return helpers.upload_generation_results(data['gen_id'])
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9099)