import logging
import boto3
import os
import uuid
from datetime import datetime


s3 = boto3.client("s3")
dynamo = boto3.client("dynamodb", region_name="us-east-1")

table_name = os.getenv("DYNAMO_TABLE")

logger = logging.getLogger()
logger.setLevel("INFO")

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
        logger.exception("Object metadata couldn't be retrieved. Trace:")
        raise 

    course_id = f"COURSE#{uuid.uuid4()}"
    # Course object
    course = {
        "PK": {"S": course_id},
        "SK": {"S": "METADATA"},
        "title": {"S": metadata["title"]},
        "file_size": {"N": str(object_size)},
        "file_url": {"S": bucket + "/" + object_key},
        "created_at": {"S": datetime.now()}
    }

    # Ownsership relationship. Professor owns course
    ownership = {
        "PK": {"S": course_id},
        "SK": {"S": f"PROFESSOR#{metadata["professor"]}"}
    }

    try:
        dynamo.transact_write_items(
            TransactItems=[
                {
                    "Put": {
                        "TableName": table_name,
                        "Item": course
                    } 
                },
                {
                    "Put": {
                        "TableName": table_name,
                        "Item": ownership
                    }
                }   
            ]
        )
        logger.info(f"Object {bucket + "/" + object_key} metadata successfully stored to DynamoDB. PK: {course_id}")      
    except Exception as e:
        logger.exception("Object's metadata couldn't be saved to DynamoDB. Trace:")


