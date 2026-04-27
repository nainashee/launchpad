import json
import logging
import os
import uuid
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

APPLICATIONS_TABLE = os.environ.get("APPLICATIONS_TABLE", "")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(APPLICATIONS_TABLE)


def handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    path = event.get("rawPath", "")
    logger.info("%s %s", method, path)

    if method == "POST" and path == "/applications":
        return _create(event)
    elif method == "GET" and path == "/applications":
        return _list(event)
    elif method == "GET" and path.startswith("/applications/"):
        return _get(event)
    elif method == "PUT" and path.startswith("/applications/"):
        return _update(event)
    elif method == "DELETE" and path.startswith("/applications/"):
        return _delete(event)
    else:
        return _response(404, {"error": "route not found"})


def _create(event):
    body = json.loads(event.get("body") or "{}")
    user_id = body.get("userId", "default")

    if not body.get("companyName") or not body.get("roleTitle"):
        return _response(400, {"error": "companyName and roleTitle are required"})

    now = datetime.now(timezone.utc).isoformat()
    item = {
        "userId":        user_id,
        "applicationId": str(uuid.uuid4()),
        "companyName":   body["companyName"],
        "roleTitle":     body["roleTitle"],
        "status":        body.get("status", "applied"),
        "appliedDate":   body.get("appliedDate", now[:10]),
        "createdAt":     now,
    }
    if body.get("followUpDate"):
        item["followUpDate"] = body["followUpDate"]

    table.put_item(Item=item)
    logger.info("created application %s for user %s", item["applicationId"], user_id)
    return _response(201, item)


def _list(event):
    user_id = (event.get("queryStringParameters") or {}).get("userId", "default")
    result = table.query(KeyConditionExpression=Key("userId").eq(user_id))
    items = result.get("Items", [])
    logger.info("listed %d applications for user %s", len(items), user_id)
    return _response(200, {"applications": items})


def _get(event):
    application_id = (event.get("pathParameters") or {}).get("id", "")
    user_id = (event.get("queryStringParameters") or {}).get("userId", "default")
    result = table.get_item(Key={"userId": user_id, "applicationId": application_id})
    item = result.get("Item")
    if not item:
        return _response(404, {"error": "application not found"})
    return _response(200, item)


def _update(event):
    application_id = (event.get("pathParameters") or {}).get("id", "")
    user_id = (event.get("queryStringParameters") or {}).get("userId", "default")
    body = json.loads(event.get("body") or "{}")

    allowed = ["companyName", "roleTitle", "status", "appliedDate", "followUpDate", "fitScore"]
    updates = {k: v for k, v in body.items() if k in allowed}
    if not updates:
        return _response(400, {"error": "no valid fields to update"})

    updates["updatedAt"] = datetime.now(timezone.utc).isoformat()

    expr_parts, expr_names, expr_values = [], {}, {}
    for i, (key, value) in enumerate(updates.items()):
        name_ph, val_ph = f"#f{i}", f":v{i}"
        expr_parts.append(f"{name_ph} = {val_ph}")
        expr_names[name_ph] = key
        expr_values[val_ph] = value

    result = table.update_item(
        Key={"userId": user_id, "applicationId": application_id},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values,
        ReturnValues="ALL_NEW",
    )
    return _response(200, result.get("Attributes", {}))


def _delete(event):
    application_id = (event.get("pathParameters") or {}).get("id", "")
    user_id = (event.get("queryStringParameters") or {}).get("userId", "default")
    table.delete_item(Key={"userId": user_id, "applicationId": application_id})
    logger.info("deleted application %s", application_id)
    return _response(200, {"message": "deleted"})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, default=str),
    }
