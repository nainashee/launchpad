import json
import logging
import os

import boto3

from auth import AuthError, log_request, verify_firebase_jwt

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MODEL_ID      = os.environ.get("MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
PROFILE_TABLE = os.environ.get("PROFILE_TABLE", "")

bedrock  = boto3.client("bedrock-runtime", region_name="us-east-1")
dynamodb = boto3.resource("dynamodb")

MAX_INPUT_CHARS = 5_000

SYSTEM_PROMPT = """You are an expert at writing professional outreach messages for job seekers.
Write concise, genuine, non-generic messages that get responses.

For LinkedIn: 300 characters max, conversational, specific to the role.
For email: Subject line + body, under 150 words, professional but warm.

Do NOT use phrases like "I hope this message finds you well" or "I am reaching out because".
Be direct, specific, and human."""


def handler(event, context):
    uid = "anonymous"
    try:
        uid = verify_firebase_jwt(event)
    except AuthError as e:
        log_request(uid, "outreach", "auth_error", reason=e.message)
        return _response(401, {"error": e.message})

    body = json.loads(event.get("body") or "{}")
    job_description = body.get("jobDescription", "").strip()
    outreach_type   = body.get("type", "linkedin")

    if not job_description:
        log_request(uid, "outreach", "validation_error", reason="missing jobDescription")
        return _response(400, {"error": "jobDescription is required"})

    if len(job_description) > MAX_INPUT_CHARS:
        log_request(uid, "outreach", "validation_error", reason="input too long")
        return _response(400, {"error": f"jobDescription exceeds {MAX_INPUT_CHARS} character limit"})

    profile = _get_profile(uid, body)

    try:
        message = _call_bedrock(profile, job_description, outreach_type)
        log_request(uid, "outreach", "success", type=outreach_type)
        return _response(200, {"message": message, "type": outreach_type})
    except Exception as e:
        logger.error("Bedrock error for user %s: %s", uid, e)
        log_request(uid, "outreach", "error", reason=str(e))
        return _response(500, {"error": "Failed to generate message. Please try again."})


def _get_profile(uid, body):
    profile = {}
    if PROFILE_TABLE:
        try:
            table  = dynamodb.Table(PROFILE_TABLE)
            result = table.get_item(Key={"userId": uid})
            profile = result.get("Item", {})
        except Exception as e:
            logger.warning("Could not fetch profile: %s", e)

    return {
        "name":         body.get("name",         profile.get("name", "the applicant")),
        "targetTitles": body.get("targetTitles",  profile.get("targetTitles", [])),
        "skills":       body.get("skills",        profile.get("skills", [])),
        "linkedInUrl":  body.get("linkedInUrl",   profile.get("linkedInUrl", "")),
    }


def _call_bedrock(profile, job_description, outreach_type):
    skills_str = ", ".join(profile["skills"]) if profile["skills"] else "software engineering"
    titles_str = ", ".join(profile["targetTitles"]) if profile["targetTitles"] else "software engineering roles"

    user_message = (
        f"Write a {outreach_type} outreach message for this job:\n\n"
        f"{job_description}\n\n"
        f"About the sender:\n"
        f"- Name: {profile['name']}\n"
        f"- Target roles: {titles_str}\n"
        f"- Key skills: {skills_str}\n"
    )
    if profile["linkedInUrl"]:
        user_message += f"- LinkedIn: {profile['linkedInUrl']}\n"

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_message}],
    }

    response = bedrock.invoke_model(modelId=MODEL_ID, body=json.dumps(payload))
    result   = json.loads(response["body"].read())
    return result["content"][0]["text"].strip()


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://jobs.naindigital.com",
        },
        "body": json.dumps(body),
    }
