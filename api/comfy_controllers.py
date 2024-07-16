import requests
import json
import time 

base_url=   'http://34.116.202.145:8188'
prompt_endpoint= '/prompt'
queue_endpoint= '/queue'
history_endpoint= '/history'

def push_queue(workflow):
    #create payload
    data={ 'prompt':workflow }
    response = requests.post(base_url + prompt_endpoint, json=data,headers={'Content-Type': 'application/json'})
    print(response.text)
    #check response
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception('Failed to push workflow to queue')
    
def get_queue():
    response = requests.get(base_url + queue_endpoint)
    response = json.loads(response.text)
    
    #check response
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception('Failed to get queue')

def get_history():
    params={'max_items':200}
    response = requests.get(base_url + history_endpoint,params=params)
    response = json.loads(response.text)
    
    return response

def check_prompt_status(prompt_id):
    time_running = 0 
    
    while time_running < 600:
        try:
            history=get_history()
            status=history[prompt_id]['status']['status_str']
            return status
        except:
            time.sleep(3)
            time_running+=3
    return 'Failed'