import json
import logging
import os
from datetime import datetime
import uuid

import boto3


dynamodb = boto3.client("dynamodb")
logger = logging.getLogger().setLevel(logging.INFO)

TABLE_NAME = os.getenv("DYNAMO_TABLE")

def lambda_handler(event, context):
    """
    Create a new course record in DynamoDB
    """
    body = event["body"]
    user_id = event["requestContext"]["authorizer"]["claims"]["cognito:username"]
    course_data = json.loads(body["course_data"])
    if (not admin_user(user_id)):
        logger.error("User %s is not an admin. Denying request", user_id)
        return {
            "statusCode": 403,
            "body": json.dumps({
                "error": "User is not authorized to create a course."
            }),
        }
    if (not validate_course(course_data)):
        logger.error("Invalid course data: %s. Denying request", course_data)
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Invalid course data."
            }),
        }
    try:
        course_id = str(uuid.uuid4())
        dynamodb.put_item(
            TableName=TABLE_NAME,
            Item={
                "PK": {"S": f"COURSE#{course_id}"},
                "SK": {"S": "METADATA"},
                "title": {"S": course_data["title"]},
                "description": {"S": course_data["description"]},
                "tags": {"SS": course_data["tags"] if course_data.get("tags") else []},
                "created_at": {"S": datetime.now().isoformat()},
            }
        )
        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "Course created successfully.",
                "course_id": course_id
            }),
        }
    except Exception as e:
            logger.exception("Failed to create course record in DynamoDB.")
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "error": "Failed to create course record."
                }),
            }


def validate_course(course_data: dict) -> bool:
    """
    Validate the course data.
    """
    # TO-DO: Implement validation logic for course data
    return True

def admin_user(user_id: str) -> bool:
    """
    Check if the user is an admin.
    """
    # TO-DO: Implement logic to check if the user is an admin
    return True