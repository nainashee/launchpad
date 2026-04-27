import json
import logging
import os
import uuid
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key

from auth import AuthError, log_request, verify_firebase_jwt

logger = logging.getLogger()
logger.setLevel(logging.INFO)

APPLICATIONS_TABLE = os.environ.get("APPLICATIONS_TABLE", "")

dynamodb = boto3.resource("dynamodb")
table    = dynamodb.Table(APPLICATIONS_TABLE)


def handler(event, context):
    uid = "anonymous"
    try:
        uid = verify_firebase_jwt(event)
    except AuthError as e:
        log_request(uid, "applications", "auth_error", reason=e.message)
        return _response(401, {"error": e.message})

    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    path   = event.get("rawPath", "")

    if method == "POST" and path == "/applications":
        return _create(event, uid)
    elif method == "GET" and path == "/applications":
        return _list(uid)
    elif method == "GET" and path.startswith("/applications/"):
        return _get(event, uid)
    elif method == "PUT" and path.startswith("/applications/"):
        return _update(event, uid)
    elif method == "DELETE" and path.startswith("/applications/"):
        return _delete(event, uid)
    else:
        return _response(404, {"error": "route not found"})


def _create(event, uid):
    body = json.loads(event.get("body") or "{}")

    if not body.get("companyName") or not body.get("roleTitle"):
        log_request(uid, "applications:create", "validation_error", reason="missing required fields")
        return _response(400, {"error": "companyName and roleTitle are required"})

    now  = datetime.now(timezone.utc).isoformat()
    item = {
        "userId":        uid,
        "applicationId": str(uuid.uuid4()),
        "companyName":   body["companyName"],
        "roleTitle":     body["roleTitle"],
        "status":        body.get("status", "applied"),
        "appliedDate":   body.get("appliedDate", now[:10]),
        "createdAt":     now,
    }
    if body.get("followUpDate"):
        item["followUpDate"] = body["followUpDate"]
    if body.get("fitScore") is not None:
        item["fitScore"] = body["fitScore"]
    if body.get("tailoredResumeKey"):
        item["tailoredResumeKey"] = body["tailoredResumeKey"]

    table.put_item(Item=item)
    log_request(uid, "applications:create", "success", applicationId=item["applicationId"])
    return _response(201, item)


def _list(uid):
    result = table.query(KeyConditionExpression=Key("userId").eq(uid))
    items  = result.get("Items", [])
    log_request(uid, "applications:list", "success", count=len(items))
    return _response(200, {"applications": items})


def _get(event, uid):
    application_id = (event.get("pathParameters") or {}).get("id", "")
    result = table.get_item(Key={"userId": uid, "applicationId": application_id})
    item   = result.get("Item")
    if not item:
        log_request(uid, "applications:get", "error", reason="not found", applicationId=application_id)
        return _response(404, {"error": "application not found"})
    log_request(uid, "applications:get", "success", applicationId=application_id)
    return _response(200, item)


def _update(event, uid):
    application_id = (event.get("pathParameters") or {}).get("id", "")
    body           = json.loads(event.get("body") or "{}")

    allowed = ["companyName", "roleTitle", "status", "appliedDate", "followUpDate", "fitScore", "tailoredResumeKey"]
    updates = {k: v for k, v in body.items() if k in allowed}
    if not updates:
        log_request(uid, "applications:update", "validation_error", reason="no valid fields")
        return _response(400, {"error": "no valid fields to update"})

    updates["updatedAt"] = datetime.now(timezone.utc).isoformat()

    expr_parts, expr_names, expr_values = [], {}, {}
    for i, (key, value) in enumerate(updates.items()):
        name_ph, val_ph = f"#f{i}", f":v{i}"
        expr_parts.append(f"{name_ph} = {val_ph}")
        expr_names[name_ph] = key
        expr_values[val_ph] = value

    result = table.update_item(
        Key={"userId": uid, "applicationId": application_id},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values,
        ReturnValues="ALL_NEW",
    )
    log_request(uid, "applications:update", "success", applicationId=application_id)
    return _response(200, result.get("Attributes", {}))


def _delete(event, uid):
    application_id = (event.get("pathParameters") or {}).get("id", "")
    table.delete_item(Key={"userId": uid, "applicationId": application_id})
    log_request(uid, "applications:delete", "success", applicationId=application_id)
    return _response(200, {"message": "deleted"})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://jobs.naindigital.com",
        },
        "body": json.dumps(body, default=str),
    }
