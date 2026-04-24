import json
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

APPLICATIONS_TABLE = os.environ.get("APPLICATIONS_TABLE", "")


def handler(event, context):
    logger.info("tracker invoked: %s %s", event.get("requestContext", {}).get("http", {}).get("method"), event.get("rawPath"))

    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    path = event.get("rawPath", "")

    if method == "POST" and path == "/applications":
        return _create(event)
    elif method == "GET" and path == "/applications":
        return _list(event)
    elif method == "GET" and "/applications/" in path:
        return _get(event)
    elif method == "PUT" and "/applications/" in path:
        return _update(event)
    elif method == "DELETE" and "/applications/" in path:
        return _delete(event)
    else:
        return _response(404, {"error": "route not found"})


def _create(event):
    # TODO: parse body, generate ULID applicationId, write to DynamoDB
    return _response(201, {"message": "create placeholder"})


def _list(event):
    # TODO: query DynamoDB by userId (from query params or auth context)
    return _response(200, {"message": "list placeholder", "applications": []})


def _get(event):
    # TODO: get single application by userId + applicationId
    return _response(200, {"message": "get placeholder"})


def _update(event):
    # TODO: update application fields (status, followUpDate, fitScore, etc.)
    return _response(200, {"message": "update placeholder"})


def _delete(event):
    # TODO: delete application by userId + applicationId
    return _response(200, {"message": "delete placeholder"})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }
