import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

s3 = boto.client("s3")
prefix = "courses/"

MIN_VIDEO_SIZE = 1024
MAX_VIDEO_SIZE = 1 * 1024 * 1024 * 1024 

BUCKET =os.getenv("CONTENT_BUCKET")  
expiration = 900

def lambda_handler(event, context):
    """
    Return an S3 pre-signed URL to upload a course file to an S3 bucket.
    Function is thought to be used with cognito user pools for authentication
    and id retrieval.
    """
    body = event["body"]
    user_id = event["requestContext"]["authorizer"]["claims"]["cognito:username"]
    object_name = body["object_name"]
    # Meta-data
    fields = {
        "x-amz-meta-uploaded-by": user_id,
        "x-amz-meta-object-name": object_name
    }
    conditions = [
        ["content-length-range", MIN_VIDEO_SIZE, MAX_VIDEO_SIZE],
        {'x-amz-meta-uploaded-by': user_id},
        {'x-amz-meta-object-name': object_name}
    ]
    
    try:
        signed_url = s3.generate_presigned_post(
            BUCKET, 
            Fields=fields,
            Key=prefix + object_name,
            Conditions=conditions,
            ExpiresIn=expiration
        )
    except ClientError as e:
        logging.error(e)
        signed_url = ""
        code = 500
        return {
            "statusCode": code,
            "body": json.dumps({
                "error": "Failed to generate pre-signed URL"
            }),
        }
    return {
        "statusCode": 200,
        "body": json.dumps({
            "url": signed_url["url"]
        }),
    }
