import logging
import boto3
import os
from datetime import datetime

dynamo = boto3.client("dynamodb", region_name="us-east-1")

table_name = os.getenv("DYNAMO_TABLE")

logger = logging.getLogger()
logger.setLevel("INFO")

def lambda_handler(event, context):
    """
    Enroll a student to a Course
    """
    body = event["body"]
    student_id = body["student"]
    course_id = body["course"]
    enrollment_date = datetime.datetime.now()

    student_enrollment = {
        "SK": {"S": f"STUDENT#{student_id}"},
        "PK": {"S": f"COURSE#{course_id}"},
        "type": {"S": "ENROLLMENT"},
        "enrollment_date": {"S": enrollment_date.isoformat()},
        "status": {"S": "ACTIVE"}
    }

    course_enrollment = {
        "SK": {"S": f"COURSE#{course_id}"},
        "PK": {"S": f"STUDENT#{student_id}"},
        "type": {"S": "ENROLLMENT"},
        "enrollment_date": {"S": enrollment_date.isoformat()},
        "status": {"S": "ACTIVE"}
    }

    try:
        dynamo.transact_write_items(
            TransactItems=[
                {
                    "Put": {
                        "TableName": table_name,
                        "Item": student_enrollment
                    } 
                },
                {
                    "Put": {
                        "TableName": table_name,
                        "Item": course_enrollment
                    }
                }   
            ]
        )
        logger.info(f"Student with id {student_id} was successfully enrolled to course {course_id}")
        return {
            "statusCode": 200
        },
    except Exception as e:
        logger.exception("Student's enrollment couldn't be saved to DynamoDB.")
        return {
            "statusCode": 500,
            "message": "Student couldn't be enrolled to course"
        }

