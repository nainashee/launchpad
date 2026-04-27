import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MODEL_ID = os.environ.get("MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")


def handler(event, context):
    logger.info("mock-interview invoked")

    body = json.loads(event.get("body") or "{}")
    job_description = body.get("jobDescription", "").strip()
    conversation = body.get("conversation", [])  # [{"role": "user"|"assistant", "content": "..."}]

    if not job_description:
        return _response(400, {"error": "jobDescription is required"})

    system_prompt = _build_system_prompt(job_description)

    # If this is the first turn, start the interview
    if not conversation:
        try:
            opening = _call_bedrock(system_prompt, [
                {"role": "user", "content": "Start the interview. Greet me briefly and ask your first question."}
            ])
            updated = [
                {"role": "user",      "content": "Start the interview."},
                {"role": "assistant", "content": opening},
            ]
            return _response(200, {"response": opening, "conversation": updated})
        except Exception as e:
            logger.error("Bedrock error: %s", e)
            return _response(500, {"error": "Failed to start interview. Please try again."})

    # Continuing an existing conversation
    try:
        reply = _call_bedrock(system_prompt, conversation)
        updated = conversation + [{"role": "assistant", "content": reply}]
        return _response(200, {"response": reply, "conversation": updated})
    except Exception as e:
        logger.error("Bedrock error: %s", e)
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
    result = json.loads(response["body"].read())
    return result["content"][0]["text"].strip()


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }
