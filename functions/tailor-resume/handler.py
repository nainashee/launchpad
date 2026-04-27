import json
import logging
import os
from datetime import datetime, timezone

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MODEL_ID     = os.environ.get("MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
ASSETS_BUCKET = os.environ.get("ASSETS_BUCKET", "")
PROFILE_TABLE = os.environ.get("PROFILE_TABLE", "")

bedrock  = boto3.client("bedrock-runtime", region_name="us-east-1")
s3       = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

SYSTEM_PROMPT = """You are an expert resume writer and career coach.
Your task is to tailor a resume to a specific job description.

Guidelines:
- Keep all facts accurate — never invent experience or skills
- Reorder and reframe existing bullet points to match the job's language
- Emphasize the most relevant experience first
- Mirror keywords from the job description naturally
- Keep the output as clean, professional plain text
- Preserve all sections (Summary, Experience, Education, Skills)"""


def handler(event, context):
    logger.info("tailor-resume invoked")

    body = json.loads(event.get("body") or "{}")
    user_id = body.get("userId", "default")
    job_description = body.get("jobDescription", "").strip()
    resume_text = body.get("resumeText", "").strip()

    if not job_description:
        return _response(400, {"error": "jobDescription is required"})

    # Get resume text: body field takes priority, then S3 via profile
    if not resume_text:
        resume_text = _fetch_resume_from_s3(user_id)

    if not resume_text:
        return _response(400, {
            "error": "No resume found. Paste your resume text in the resumeText field, "
                     "or upload your master resume to S3 via your profile."
        })

    try:
        tailored = _call_bedrock(resume_text, job_description)
        s3_key = _save_to_s3(user_id, tailored)
        return _response(200, {"tailoredResume": tailored, "s3Key": s3_key})
    except Exception as e:
        logger.error("Error: %s", e)
        return _response(500, {"error": "Failed to tailor resume. Please try again."})


def _fetch_resume_from_s3(user_id):
    """Try to get master resume key from Profile table, then fetch from S3."""
    if not PROFILE_TABLE or not ASSETS_BUCKET:
        return None
    try:
        table = dynamodb.Table(PROFILE_TABLE)
        result = table.get_item(Key={"userId": user_id})
        item = result.get("Item", {})
        s3_key = item.get("masterResumeS3Key")
        if not s3_key:
            return None
        obj = s3.get_object(Bucket=ASSETS_BUCKET, Key=s3_key)
        return obj["Body"].read().decode("utf-8")
    except Exception as e:
        logger.warning("Could not fetch resume from S3: %s", e)
        return None


def _call_bedrock(resume_text, job_description):
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "system": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Here is my current resume:\n\n{resume_text}\n\n"
                    f"Here is the job description I am applying to:\n\n{job_description}\n\n"
                    "Please tailor my resume for this role. Return only the tailored resume text."
                ),
            }
        ],
    }
    response = bedrock.invoke_model(modelId=MODEL_ID, body=json.dumps(payload))
    result = json.loads(response["body"].read())
    return result["content"][0]["text"].strip()


def _save_to_s3(user_id, tailored_text):
    """Save tailored resume to S3 and return the key."""
    if not ASSETS_BUCKET:
        return None
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    key = f"resumes/{user_id}/tailored-{timestamp}.txt"
    try:
        s3.put_object(
            Bucket=ASSETS_BUCKET,
            Key=key,
            Body=tailored_text.encode("utf-8"),
            ContentType="text/plain",
        )
        return key
    except Exception as e:
        logger.warning("Could not save to S3: %s", e)
        return None


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }
