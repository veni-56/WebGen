"""
storage/s3.py — S3-compatible storage backend.

Works with AWS S3, MinIO, Cloudflare R2, Backblaze B2.
Requires boto3: pip install boto3
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from storage.filesystem import StorageBackend


class S3Backend(StorageBackend):
    def __init__(self, bucket: str, prefix: str = "",
                 endpoint_url: str | None = None,
                 region: str = "us-east-1"):
        self._bucket       = bucket
        self._prefix       = prefix.rstrip("/")
        self._endpoint_url = endpoint_url or os.environ.get("S3_ENDPOINT_URL")
        self._region       = region
        self._client       = None

    def _s3(self):
        if self._client is None:
            try:
                import boto3
                kwargs = {"region_name": self._region}
                if self._endpoint_url:
                    kwargs["endpoint_url"] = self._endpoint_url
                self._client = boto3.client("s3", **kwargs)
            except ImportError:
                raise RuntimeError("boto3 not installed: pip install boto3")
        return self._client

    def _full_key(self, key: str) -> str:
        return f"{self._prefix}/{key}" if self._prefix else key

    def put(self, key: str, data: bytes,
            content_type: str = "application/octet-stream") -> str:
        fk = self._full_key(key)
        self._s3().put_object(
            Bucket=self._bucket, Key=fk, Body=data,
            ContentType=content_type,
            # Immutable: set long cache
            CacheControl="public, max-age=31536000, immutable",
        )
        return key

    def get(self, key: str) -> bytes | None:
        try:
            resp = self._s3().get_object(Bucket=self._bucket, Key=self._full_key(key))
            return resp["Body"].read()
        except Exception:
            return None

    def exists(self, key: str) -> bool:
        try:
            self._s3().head_object(Bucket=self._bucket, Key=self._full_key(key))
            return True
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        try:
            self._s3().delete_object(Bucket=self._bucket, Key=self._full_key(key))
            return True
        except Exception:
            return False

    def list_prefix(self, prefix: str) -> list[str]:
        full = self._full_key(prefix)
        try:
            paginator = self._s3().get_paginator("list_objects_v2")
            keys = []
            for page in paginator.paginate(Bucket=self._bucket, Prefix=full):
                for obj in page.get("Contents", []):
                    k = obj["Key"]
                    if self._prefix:
                        k = k[len(self._prefix)+1:]
                    keys.append(k)
            return keys
        except Exception:
            return []

    def signed_url(self, key: str, expires_in: int = 3600) -> str:
        return self._s3().generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": self._full_key(key)},
            ExpiresIn=expires_in,
        )
