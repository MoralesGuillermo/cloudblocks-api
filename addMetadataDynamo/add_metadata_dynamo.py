import json
import logging
import boto3


s3 = boto3.client("s3")
dynamo = boto3.client("dynamodb")

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

    # TODO: Add the object's metadata to DynamoDB
