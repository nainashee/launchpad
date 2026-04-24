import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ASSETS_BUCKET = os.environ.get("ASSETS_BUCKET", "")
PROFILE_TABLE = os.environ.get("PROFILE_TABLE", "")


def handler(event, context):
    logger.info("tailor-resume invoked")

    body = json.loads(event.get("body") or "{}")
    user_id = body.get("userId", "")
    job_description = body.get("jobDescription", "")

    if not user_id or not job_description:
        return _response(400, {"error": "userId and jobDescription are required"})

    # TODO:
    # 1. Fetch user's masterResumeS3Key from Profile table
    # 2. Download master resume PDF from S3
    # 3. Call Bedrock (Claude) with resume + job description
    # 4. Save tailored resume to S3 under resumes/<userId>/<applicationId>.pdf
    # 5. Return the S3 key of the tailored resume

    return _response(200, {
        "message": "tailor-resume placeholder — Bedrock integration coming soon",
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
