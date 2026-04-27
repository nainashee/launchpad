import json
import logging
import os
from datetime import datetime, timezone

import boto3

from auth import AuthError, log_request, verify_firebase_jwt

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MODEL_ID      = os.environ.get("MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
ASSETS_BUCKET = os.environ.get("ASSETS_BUCKET", "")
PROFILE_TABLE = os.environ.get("PROFILE_TABLE", "")

bedrock  = boto3.client("bedrock-runtime", region_name="us-east-1")
s3       = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

MAX_INPUT_CHARS = 8_000

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
    uid = "anonymous"
    try:
        uid = verify_firebase_jwt(event)
    except AuthError as e:
        log_request(uid, "tailor-resume", "auth_error", reason=e.message)
        return _response(401, {"error": e.message})

    body = json.loads(event.get("body") or "{}")
    job_description = body.get("jobDescription", "").strip()
    resume_text     = body.get("resumeText", "").strip()

    if not job_description:
        log_request(uid, "tailor-resume", "validation_error", reason="missing jobDescription")
        return _response(400, {"error": "jobDescription is required"})

    if len(job_description) > MAX_INPUT_CHARS:
        log_request(uid, "tailor-resume", "validation_error", reason="input too long")
        return _response(400, {"error": f"jobDescription exceeds {MAX_INPUT_CHARS} character limit"})

    if not resume_text:
        resume_text = _fetch_resume_from_s3(uid)

    if not resume_text:
        log_request(uid, "tailor-resume", "validation_error", reason="no resume found")
        return _response(400, {
            "error": "No resume found. Paste your resume text in the resumeText field, "
                     "or upload your master resume via your profile."
        })

    try:
        tailored = _call_bedrock(resume_text, job_description)
        s3_key = _save_to_s3(uid, tailored)
        log_request(uid, "tailor-resume", "success", input_chars=len(job_description))
        return _response(200, {"tailoredResume": tailored, "s3Key": s3_key})
    except Exception as e:
        logger.error("Bedrock error for user %s: %s", uid, e)
        log_request(uid, "tailor-resume", "error", reason=str(e))
        return _response(500, {"error": "Failed to tailor resume. Please try again."})


def _fetch_resume_from_s3(uid):
    if not PROFILE_TABLE or not ASSETS_BUCKET:
        return None
    try:
        table  = dynamodb.Table(PROFILE_TABLE)
        result = table.get_item(Key={"userId": uid})
        item   = result.get("Item", {})
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
    result   = json.loads(response["body"].read())
    return result["content"][0]["text"].strip()


def _save_to_s3(uid, tailored_text):
    if not ASSETS_BUCKET:
        return None
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    key = f"resumes/{uid}/tailored-{timestamp}.txt"
    try:
        s3.put_object(
            Bucket=ASSETS_BUCKET,
            Key=key,
            Body=tailored_text.encode("utf-8"),
            ContentType="text/plain",
        )
        return key
    except Exception as e:
        logger.warning("Could not save tailored resume to S3: %s", e)
        return None


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://jobs.naindigital.com",
        },
        "body": json.dumps(body),
    }
