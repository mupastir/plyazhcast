from datetime import datetime

import boto3

from app.constants import TIME_FORMAT


def load_date(episode: dict):
    date_created = episode.get("date_created", None)
    if date_created:
        date_created = datetime.strptime(date_created, TIME_FORMAT)
        episode["date_created"] = date_created
    return episode


def dump_date(episode: dict):
    date_created = episode.get("date_created", None)
    if date_created:
        episode["date_created"] = date_created.strftime(TIME_FORMAT)
    return episode


def get_s3_resource(account_id: str, key: str, secret: str):
    return boto3.resource(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        region_name="auto",
    )
