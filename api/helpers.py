import glob
import cloudinary_api
import airtable_api
import threading
from credentials import creds
import time
import os
import cloudinary
import cloudinary.uploader

# Configuration       
cloudinary.config( 
    cloud_name = creds['CLOUDINARY_CLOUDNAME'], 
    api_key = creds['CLOUDINARY_API_KEY'], 
    api_secret = creds['CLOUDINARY_API_SECRET'], # Click 'View Credentials' below to copy your API secret
    secure=True
)

def get_gen_result(gen_id):
    results=sorted(glob.glob("/home/flowingbe/ComfyUI/output/temporal/product-{id}_*".format(id=gen_id)))
    return results


def upload_generation_results(gen_id):
    #get path to model pics
    inference_result_path = get_gen_result(gen_id)[0]
    
    result_url = cloudinary_api.upload_cloudinary(inference_result_path, f"product-{gen_id}")
    
    return result_url


def delayed_delete(cloudinary_ids,model_pics):
    print("DELETION PROCESS STARTED. SLEEP 10.")
    time.sleep(10)
    for pic in model_pics:
        os.system('sudo rm -rf {pic}'.format(pic=pic))

    for public_id in cloudinary_ids:
        cloudinary_api.delete_image_cloudordinary(public_id)

    print("DELETION PROCESS FINISHED.")
    
def upload_image(file):
    try:
        # Read the binary data
        image_binary = file.read()
        
        # Open the image using PIL
        image = Image.open(io.BytesIO(image_binary))
        
        # Apply any transformations
        transformed_image = image
        
        # Convert the image back to binary
        buffered = io.BytesIO()
        transformed_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue())
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload("data:image/png;base64," + img_str.decode())
        print(result['secure_url'])
        return jsonify({
            'secure_url': result['secure_url'],
            'public_id': result['public_id']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# def upload_model(user_id,gen_id,model_setup):
#     #get path to model pics
#     model_pics = get_model_pics(gen_id)
    
#     #create list of cloudinary ids & urls
#     model_urls = []
#     cloudinary_ids=[]

#     #upload model pics to cloudinary
#     for pic in model_pics:
#         public_id = pic.split("_")[-1].split(".")[0]
#         model_urls += [cloudinary_api.upload_cloudinary(pic, public_id)]
#         cloudinary_ids += [public_id]
    
#     #push model to airtable
#     resp = airtable_api.push_model_to_airtable(user_id, model_urls,model_setup)
    

#     threading.Thread(target=delayed_delete, args=(cloudinary_ids,model_pics)).start()
    
#     return resp