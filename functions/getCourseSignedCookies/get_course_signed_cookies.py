import json
import os

import boto3


cdn = boto3.client("cloudfront")
dynamodb = boto3.client("dynamodb")

TABLE_NAME = os.getenv("TABLE_NAME")

def lambda_handler(event, context):
    """
    Return a CloudFront distro signed cookies to access a video file in an S3 bucket.
    """
    body = event["body"]
    user_id = event["requestContext"]["authorizer"]["claims"]["cognito:username"]
    video_id = body["video_id"]

    if (not user_enrolled_in_course(user_id, video_id)):
        return {
            "statusCode": 403,
            "body": json.dumps({
                "error": "User is not enrolled in the course. Access denied."
            }),
        }
    #TODO: Generate the pre-signed Cloudfront cookies. Use SSM secure strings to store the RSA private key.
    #PLAN: Give access to the full course directory to the user.

#TODO: Add logging for cases
def user_enrolled_in_course(user_id: str, video_id: str) -> bool:
    """
    Validate if a user is enrolled in the course that owns the video.
    """
    def get_course_id_from_video(video_id: str) -> str | None:
        """
        Retrieve the course ID the video belong to.
        If the video does not exist, return None.
        Returns the course ID including the "COURSE#" prefix.
        """
        response = dynamodb.query(
            TableName=TABLE_NAME,
            KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
            ExpressionAttributeValues={
                ":pk": {"S": f"VIDEO#{video_id}"},
                ":sk": {"S": "COURSE#"},
            },
            ProjectionExpresssion="SK",
        )
        if response["Count"] == 0:
            return None
        course_id = response["Items"][0]["SK"]["S"]
        return course_id
    def is_enrolled(user_id: str, course_id: str) -> bool:
        """
        Check if a user is enrolled in a course.
        Expected course_id format: 'COURSE#<id>'
        """
        #TODO: Consider if user's enrollment is active or not.
        response = dynamodb.get_item(
            TableName=TABLE_NAME,
            Key={
                "PK": {"S": f"USER#{user_id}"},
                "SK": {"S": f"{course_id}"}
            }
        )
        return response["Count"] > 0
    course_id = get_course_id_from_video(video_id)
    if not course_id:
        return False
    return is_enrolled(user_id, course_id)

    