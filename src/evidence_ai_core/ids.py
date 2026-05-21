from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import re

_SLUG_SAFE = re.compile(r"[^a-zA-Z0-9]+")

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def slugify(value: str, fallback: str = "packet") -> str:
    slug = _SLUG_SAFE.sub("-", value.strip().lower()).strip("-")
    return slug[:48] or fallback

def make_packet_id(request_text: str, created_at: str | None = None) -> str:
    created_at = created_at or utc_now_iso()
    digest = hashlib.sha256(f"{created_at}\n{request_text}".encode("utf-8")).hexdigest()[:8]
    timestamp = created_at.replace("-", "").replace(":", "").split("+")[0].replace("T", "_")
    return f"{timestamp}_{slugify(request_text)}_{digest}"
