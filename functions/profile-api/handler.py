import json
import logging
import os
from datetime import datetime, timezone

import boto3

from auth import AuthError, log_request, verify_firebase_jwt

logger = logging.getLogger()
logger.setLevel(logging.INFO)

PROFILE_TABLE = os.environ.get("PROFILE_TABLE", "")
MAX_BODY_BYTES = 5 * 1024  # 5 KB

dynamodb = boto3.resource("dynamodb")
table    = dynamodb.Table(PROFILE_TABLE)

# Fields the user may set via PUT /profile
# System-managed fields (masterResumeS3Key, parsedRoles, parseStatus, etc.)
# are written only by parse-resume Lambda and are excluded here.
ALLOWED_PUT_FIELDS = {
    "email", "name", "targetTitles", "skills",
    "githubUsername", "linkedInUrl", "onboardingComplete",
}


def handler(event, context):
    uid = "anonymous"
    try:
        uid = verify_firebase_jwt(event)
    except AuthError as e:
        log_request(uid, "profile", "auth_error", reason=e.message)
        return _response(401, {"error": e.message})

    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    path   = event.get("rawPath", "")

    if method == "GET" and path == "/profile":
        return _get_profile(uid)
    elif method == "PUT" and path == "/profile":
        return _put_profile(event, uid)
    elif method == "POST" and path == "/profile/upload-url":
        return _upload_url(uid)
    elif method == "POST" and path == "/profile/parse-resume":
        return _parse_resume(uid)
    else:
        return _response(404, {"error": "route not found"})


def _get_profile(uid):
    result = table.get_item(Key={"userId": uid})
    item   = result.get("Item", {"userId": uid})
    log_request(uid, "profile:get", "success")
    return _response(200, item)


def _put_profile(event, uid):
    raw = event.get("body") or ""
    if len(raw.encode("utf-8")) > MAX_BODY_BYTES:
        log_request(uid, "profile:put", "validation_error", reason="body too large")
        return _response(400, {"error": "request body too large"})

    body    = json.loads(raw or "{}")
    updates = {k: v for k, v in body.items() if k in ALLOWED_PUT_FIELDS}
    if not updates:
        log_request(uid, "profile:put", "validation_error", reason="no valid fields")
        return _response(400, {"error": "no valid fields to update"})

    updates["updatedAt"] = datetime.now(timezone.utc).isoformat()

    expr_parts, expr_names, expr_values = [], {}, {}
    for i, (key, value) in enumerate(updates.items()):
        name_ph, val_ph = f"#f{i}", f":v{i}"
        expr_parts.append(f"{name_ph} = {val_ph}")
        expr_names[name_ph] = key
        expr_values[val_ph] = value

    result = table.update_item(
        Key={"userId": uid},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values,
        ReturnValues="ALL_NEW",
    )
    log_request(uid, "profile:put", "success")
    return _response(200, result.get("Attributes", {}))


def _upload_url(uid):
    # Implemented in Step 0b — presigned S3 PUT URL + upload restrictions
    log_request(uid, "profile:upload-url", "not_implemented")
    return _response(501, {"error": "not yet implemented"})


def _parse_resume(uid):
    # Implemented in Step 0c — async Bedrock PDF extraction
    log_request(uid, "profile:parse-resume", "not_implemented")
    return _response(501, {"error": "not yet implemented"})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://jobs.naindigital.com",
        },
        "body": json.dumps(body, default=str),
    }
