import json
import sys
from flask import request
import logging
from datetime import datetime
from pythonjsonlogger import jsonlogger

logger = logging.getLogger(__name__)
logHandler = logging.StreamHandler()


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record["timestamp"] = now
        if log_record.get('level'):
            log_record["level"] = log_record.get("level").upper()
        else:
            log_record["level"] = record.levelname
        if request:
            request_json = log_request_info()
            log_record["X-Request-ID"] = request_json["request_id"]
            log_record["X-Forwarded-For"] = request_json["forwarded_for"]
            log_record["X-Forwarded-Host"] = request_json["forwarded_host"]
            log_record["X-Forwarded-Proto"] = request_json["protocol"]
            log_record["remote-address"] = request_json["remote_address"]


def setup_logger(logger):
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(X-Request-ID)s %(X-Forwarded-For)s %(X-Forwarded-Host)s "
        "%(X-Forwarded-Proto)s %(remote-address)s %(message)s %(pathname)s %(funcName)s %(lineno)s"
    )
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)


def log_request_info():
    request_id = request.headers.get("X-Request-ID")
    forwarded_for = request.headers.get("X-Forwarded-For")
    remote_address = request.remote_addr
    forwarded_host = request.host.split(":", 1)[0]
    protocol = request.headers.get("X-Forwarded-Proto")
    return {
        "request_id": request_id,
        "forwarded_for": forwarded_for,
        "remote_address": remote_address,
        "forwarded_host": forwarded_host,
        "protocol": protocol,
    }