import json
import logging
import os

import boto3

from auth import AuthError, log_request, verify_firebase_jwt

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MODEL_ID = os.environ.get("MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

MAX_JD_CHARS  = 8_000
MAX_MSG_CHARS = 3_000


def handler(event, context):
    uid = "anonymous"
    try:
        uid = verify_firebase_jwt(event)
    except AuthError as e:
        log_request(uid, "interview", "auth_error", reason=e.message)
        return _response(401, {"error": e.message})

    body = json.loads(event.get("body") or "{}")
    job_description = body.get("jobDescription", "").strip()
    conversation    = body.get("conversation", [])

    if not job_description:
        log_request(uid, "interview", "validation_error", reason="missing jobDescription")
        return _response(400, {"error": "jobDescription is required"})

    if len(job_description) > MAX_JD_CHARS:
        log_request(uid, "interview", "validation_error", reason="jobDescription too long")
        return _response(400, {"error": f"jobDescription exceeds {MAX_JD_CHARS} character limit"})

    # Validate the last user message if continuing a conversation
    if conversation:
        last_user = next(
            (m["content"] for m in reversed(conversation) if m.get("role") == "user"), ""
        )
        if len(last_user) > MAX_MSG_CHARS:
            log_request(uid, "interview", "validation_error", reason="message too long")
            return _response(400, {"error": f"Message exceeds {MAX_MSG_CHARS} character limit"})

    system_prompt = _build_system_prompt(job_description)

    if not conversation:
        try:
            opening = _call_bedrock(system_prompt, [
                {"role": "user", "content": "Start the interview. Greet me briefly and ask your first question."}
            ])
            updated = [
                {"role": "user",      "content": "Start the interview."},
                {"role": "assistant", "content": opening},
            ]
            log_request(uid, "interview", "success", turn=0)
            return _response(200, {"response": opening, "conversation": updated})
        except Exception as e:
            logger.error("Bedrock error for user %s: %s", uid, e)
            log_request(uid, "interview", "error", reason=str(e))
            return _response(500, {"error": "Failed to start interview. Please try again."})

    try:
        reply   = _call_bedrock(system_prompt, conversation)
        updated = conversation + [{"role": "assistant", "content": reply}]
        turn    = len([m for m in updated if m["role"] == "assistant"])
        log_request(uid, "interview", "success", turn=turn)
        return _response(200, {"response": reply, "conversation": updated})
    except Exception as e:
        logger.error("Bedrock error for user %s: %s", uid, e)
        log_request(uid, "interview", "error", reason=str(e))
        return _response(500, {"error": "Failed to continue interview. Please try again."})


def _build_system_prompt(job_description):
    return f"""You are a senior technical interviewer conducting a mock job interview.

Job description:
{job_description}

Your role:
- Ask one question at a time — behavioural, technical, or situational based on the JD
- After the candidate answers, give brief constructive feedback (1-2 sentences), then ask the next question
- After 5-6 exchanges, wrap up with overall feedback on their interview performance
- Be professional but encouraging — this is practice, not a real interview
- Tailor questions specifically to the skills and responsibilities in the job description"""


def _call_bedrock(system_prompt, messages):
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "system": system_prompt,
        "messages": messages,
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
