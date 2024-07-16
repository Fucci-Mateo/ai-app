import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from credentials import creds

# Configuration       
cloudinary.config( 
    cloud_name = creds['CLOUDINARY_CLOUDNAME'], 
    api_key = creds['CLOUDINARY_API_KEY'], 
    api_secret = creds['CLOUDINARY_API_SECRET'], # Click 'View Credentials' below to copy your API secret
    secure=True
)

# Upload an image
def upload_cloudinary(path, public_id):
    upload_result = cloudinary.uploader.upload(path,
                                            public_id=public_id)
    return upload_result["secure_url"]

# Optimize delivery by resizing and applying auto-format and auto-quality
def auto_optimize_url(public_id):
    optimize_url, _ = cloudinary_url(public_id, fetch_format="auto", quality="auto")
    return optimize_url

# Transform the image: auto-crop to square aspect_ratio
def auto_crop_url(public_id):
    auto_crop_url, _ = cloudinary_url(public_id, width=500, height=500, crop="auto", gravity="auto")
    return auto_crop_url

# Delete an image
def delete_image_cloudordinary(public_id):
    if type(public_id)==list:
        for id in public_id:
            result=cloudinary.uploader.destroy(id)
            print(result)
    else:
        result=cloudinary.uploader.destroy(public_id)
    print(result)

