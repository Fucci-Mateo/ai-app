import requests
import json
from credentials import creds

url = "https://api.airtable.com/v0/"
base_id = creds['BASE_ID']
poses_table = creds['POSES_TABLE']
models_table = creds['MODELS_TABLE']



headers = {
    "Authorization": "Bearer {}".format(creds["AIRTABLE_TOKEN"]),
    "Content-Type": "application/json"
}

def push_pose_to_airtable(pose_name ,pose_image_url, skeleton_image_url):
    url = f"https://api.airtable.com/v0/{base_id}/{poses_table}"

    data = {"records": [{"fields": {"name": pose_name, "image": [{'url':pose_image_url}], "skeleton": [{'url':skeleton_image_url}]}}]}


    response = requests.post(url, headers=headers, json=data)
    return response.json()


def get_pose_by_name(pose_name):
    url = f"https://api.airtable.com/v0/{base_id}/{poses_table}"
    params = {
        'maxRecords': '1',
        'filterByFormula': "name='{}'".format(pose_name),
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()


def push_model_to_airtable(user_id,model_images,model_setup):
    if user_id is None:
        user_id = 1
    url = f"https://api.airtable.com/v0/{base_id}/{models_table}"
    data = {"records": [{
        "fields": {
            "images": [{'url':model_images[0]},{'url':model_images[1]},{'url':model_images[2]},{'url':model_images[3]}], 
            "user_id": int(user_id),
            "setup": json.dumps(model_setup)
            }
        }]
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

def get_model_images_by_id(model_id):
    url = f"https://api.airtable.com/v0/{base_id}/{models_table}"

    params = {
        'maxRecords': '1',
        'filterByFormula': "model_id={}".format(str(model_id)),
        'fields[]': 'images',
        'fields': 'setup' 
    }
    print(params)

    response = requests.get(url, headers=headers, params=params)

    model_images=response.json()['records'][0]['fields']['images']
    model_setup=response.json()['records'][0]['fields']['setup']
    
    img_urls=[]
    img_urls += [img['url'] for img in model_images]

    return img_urls, model_setup
