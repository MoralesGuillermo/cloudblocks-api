import json
import boto3

def lambda_handler(event, context):
    """
    TO-DO
    """
        return {
        "statusCode": 200,
        "body": json.dumps({
            "hello": "world"
        }),
    }
