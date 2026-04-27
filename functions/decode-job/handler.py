import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MODEL_ID = os.environ.get("MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

SYSTEM_PROMPT = """You are an expert job description analyst helping a job seeker evaluate opportunities.
Given a job description, extract key information and return ONLY valid JSON — no markdown, no explanation, just the JSON object.

Return this exact structure:
{
  "fitScore": <integer 1-10>,
  "summary": "<2-3 sentence summary of the role>",
  "requiredSkills": ["<skill>", ...],
  "niceToHaves": ["<skill>", ...],
  "redFlags": ["<concern>", ...],
  "keySignals": ["<positive signal>", ...]
}

fitScore guidance: 1-3 = poor fit, 4-6 = moderate, 7-8 = strong, 9-10 = exceptional match for a senior software engineer."""


def handler(event, context):
    logger.info("decode-job invoked")

    body = json.loads(event.get("body") or "{}")
    job_description = body.get("jobDescription", "").strip()

    if not job_description:
        return _response(400, {"error": "jobDescription is required"})

    try:
        result = _call_bedrock(job_description)
        return _response(200, result)
    except Exception as e:
        logger.error("Bedrock error: %s", e)
        return _response(500, {"error": "Failed to analyze job description. Please try again."})


def _call_bedrock(job_description):
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "system": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": f"Analyze this job description:\n\n{job_description}",
            }
        ],
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(payload),
    )

    result = json.loads(response["body"].read())
    text = result["content"][0]["text"].strip()

    # Strip markdown code fences if Claude adds them
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]

    return json.loads(text)


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }
