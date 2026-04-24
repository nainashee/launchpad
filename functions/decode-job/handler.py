import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    logger.info("decode-job invoked")

    body = json.loads(event.get("body") or "{}")
    job_description = body.get("jobDescription", "")

    if not job_description:
        return _response(400, {"error": "jobDescription is required"})

    # TODO:
    # 1. Call Bedrock (Claude) with job description
    # 2. Extract: required skills, nice-to-haves, culture signals, red flags, fit score
    # 3. Return structured analysis

    return _response(200, {
        "message": "decode-job placeholder — Bedrock integration coming soon",
        "jobDescription": job_description[:100],
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
