import logging
import os
import uuid
from datetime import datetime

import boto3

s3 = boto3.client("s3")
dynamo = boto3.client("dynamodb", region_name="us-east-1")

table_name = os.getenv("DYNAMO_TABLE")

logger = logging.getLogger()
logger.setLevel("INFO")

# TODO: Add validations for metadata fields.
def lambda_handler(event, context):
    """
    Add uploaded courses metadata to DynamoDB
    """
    record = event["Records"][0]
    bucket = record["bucket"]["name"]
    object_key = record["object"]["key"]
    object_size = record["object"]["size"]

    try:       
        # Retrieve objects metadata
        object_head = s3.head_object(
            Bucket=bucket,
            Key=object_key
        )
        metadata = object_head["Metadata"]
    except Exception as e:
        logger.exception("Video's metadata couldn't be retrieved. Trace:")
        raise 

    video_id = str(uuid.uuid4())
    # Video's metadata object. Stores video information.
    video = {
        "PK": {"S": f"VIDEO#{video_id}"},
        "SK": {"S": "METADATA"},
        "title": {"S": metadata["title"]},
        "file_size": {"N": str(object_size)},
        "file_url": {"S": bucket + "/" + object_key},
        "created_at": {"S": datetime.now()}
    }

    # Ownsership relationship. Course owns the video.
    # Purpose is to enable querying all videos that belong to a course
    ownership = {
        "PK": {"S": f"COURSE#{metadata['course_id']}"},
        "SK": {"S": f"VIDEO#{video_id}"},
    }

    # Master relationship. Which course the video belongs to.
    # Purpose is to enable querying to which course the video belongs to.
    master = {
        "PK": {"S": f"VIDEO#{video_id}"},
        "SK": {"S": f"COURSE#{metadata['course_id']}"},
    }

    try:
        dynamo.transact_write_items(
            TransactItems=[
                {
                    "Put": {
                        "TableName": table_name,
                        "Item": video
                    } 
                },
                {
                    "Put": {
                        "TableName": table_name,
                        "Item": ownership
                    }
                },
                {
                    "Put": {
                        "TableName": table_name,
                        "Item": master
                    }
                }
            ]
        )
        logger.info(f"Video {bucket + "/" + object_key} metadata successfully stored to DynamoDB. Video ID: {video_id}")      
    except Exception as e:
        logger.exception("Videos's metadata couldn't be saved to DynamoDB. Video ID: %s Trace:", video_id)


