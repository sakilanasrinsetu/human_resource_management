from rest_framework.exceptions import ValidationError
import re
import uuid
import mimetypes
import boto3
from django.conf import settings
from rest_framework import status
from utils.response_wrapper import ResponseWrapper

def image_upload(file, path):
    file = file
    path = path
    image_url = None
    
    IMAGE_CHAR_REPLACE = {" ": "", "_": ""}
    if not file or not path:
        raise False
    if file:
        filename = filename = re.sub(
                r"[ _]", lambda x: IMAGE_CHAR_REPLACE[x.group(0)], file.name
            )   #file.name
        filename = f'{uuid.uuid4().hex}-{filename}'
        file_type = mimetypes.guess_type(filename)[0]
        key = f'gprojukti-v2-test/{path}/{filename}'
        content = file.read()
        # upload image in digital ocean spaces
        
        digital_ocean_spaces = boto3.resource(
            's3',
            endpoint_url=settings.DIGITAL_OCEAN_SPACES_ENDPOINT_URL,
            aws_access_key_id=settings.DIGITAL_OCEAN_SPACES_ACCESS_KEY_ID,
            aws_secret_access_key=settings.DIGITAL_OCEAN_SPACES_SECRET_ACCESS_KEY
        )
        digital_ocean_spaces.Bucket(settings.DIGITAL_OCEAN_SPACES_BUCKET_NAME).put_object(Key=key, Body=content, ContentType=file_type).Acl().put(ACL='public-read')
        # context = {
        #     'url': f'https://gprmain.sgp1.cdn.digitaloceanspaces.com/{key}'
        # }
        image_url = f'https://gprmain.sgp1.cdn.digitaloceanspaces.com/{key}'
    return image_url