import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    logger.info("mock-interview invoked")

    body = json.loads(event.get("body") or "{}")
    user_id = body.get("userId", "")
    job_description = body.get("jobDescription", "")
    conversation = body.get("conversation", [])  # list of {"role": "user/assistant", "content": "..."}

    if not user_id or not job_description:
        return _response(400, {"error": "userId and jobDescription are required"})

    # TODO:
    # 1. Build system prompt: "You are a technical interviewer for <role>..."
    # 2. Pass full conversation history to Bedrock (Claude) for multi-turn support
    # 3. Return interviewer's next question or feedback

    return _response(200, {
        "message": "mock-interview placeholder — Bedrock integration coming soon",
        "userId": user_id,
        "turns": len(conversation),
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
