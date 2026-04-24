import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

PROFILE_TABLE = os.environ.get("PROFILE_TABLE", "")


def handler(event, context):
    logger.info("generate-outreach invoked")

    body = json.loads(event.get("body") or "{}")
    user_id = body.get("userId", "")
    job_description = body.get("jobDescription", "")
    outreach_type = body.get("type", "linkedin")  # "linkedin" or "email"

    if not user_id or not job_description:
        return _response(400, {"error": "userId and jobDescription are required"})

    # TODO:
    # 1. Fetch user profile from DynamoDB (skills, linkedInUrl, targetTitles)
    # 2. Call Bedrock (Claude) with profile + job description + outreach type
    # 3. Return drafted message

    return _response(200, {
        "message": "generate-outreach placeholder — Bedrock integration coming soon",
        "type": outreach_type,
        "userId": user_id,
    })


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }
