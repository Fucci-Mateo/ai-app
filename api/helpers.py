import glob
import cloudinary_api
import threading
from credentials import creds
import time
import os
import cloudinary
import cloudinary.uploader
import logging
import json


# Configuration       
cloudinary.config( 
    cloud_name = creds['CLOUDINARY_CLOUDNAME'], 
    api_key = creds['CLOUDINARY_API_KEY'], 
    api_secret = creds['CLOUDINARY_API_SECRET'], # Click 'View Credentials' below to copy your API secret
    secure=True
)     
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)

def get_gen_result(gen_id):
    results=sorted(glob.glob("/home/flowingbe/ComfyUI/output/temporal/product-{id}_*".format(id=gen_id)))
    return results


def upload_generation_results(gen_id):
    #get path to model pics
    inference_result_path = get_gen_result(gen_id)[0]
    result_url = cloudinary_api.upload_cloudinary(inference_result_path, f"product-{gen_id}")
    return result_url


def result_delayed_delete(gen_id,sleep):
    print("DELETION PROCESS STARTED FOR SYSTEM, ID: {}. SLEEP {}s.".format(gen_id,sleep))
    time.sleep(sleep)
    pic = get_gen_result(gen_id)[0]
    os.system('sudo rm -rf {pic}'.format(pic=pic))
    cloudinary_api.delete_image_cloudordinary(f"product-{gen_id}")
    logging.info(json.dumps({'gen_id': gen_id, 'cloudinary_id': f"product-{gen_id}", 'deleted': True, 'platform': 'system & cloudinary'}))
    print("DELETION PROCESS FINISHED.")


def cloudinary_delayed_delete(public_id,sleep):
    print("DELETION PROCESS STARTED FOR CLOUDINARY, ID: {}. SLEEP {}s.".format(public_id,sleep))
    time.sleep(sleep)
    cloudinary_api.delete_image_cloudordinary(public_id)
    logging.info(json.dumps({'public_id': public_id, 'deleted': True, 'platform': 'cloudinary'}))
    print("DELETION PROCESS FINISHED.")


def defer_delete(method,id,sleep):
    if method == "generation":
        threading.Thread(target=result_delayed_delete, args=(id,sleep)).start()
    elif method == "resource":
        threading.Thread(target=cloudinary_delayed_delete, args=(id,sleep)).start()
    else:
        print("Invalid method for deletion.")


def couldinary_upload_img_str(img_str):
    return cloudinary.uploader.upload("data:image/png;base64," + img_str.decode())


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