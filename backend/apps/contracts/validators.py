"""Secure validation for uploaded contract files."""
from __future__ import annotations

import hashlib
import os
from typing import IO

from django.conf import settings
from rest_framework.exceptions import ValidationError

try:
    import magic  # python-magic (libmagic). Optional fallback below.
    HAS_MAGIC = True
except Exception:  # pragma: no cover
    HAS_MAGIC = False


def validate_upload(uploaded_file) -> dict:
    """Validate size, extension, and (when available) MIME via libmagic.

    Returns a dict with `mime_type`, `extension`, `size_bytes`, `sha256`.
    Raises rest_framework.ValidationError on failure.
    """
    name = uploaded_file.name or ""
    ext = os.path.splitext(name)[1].lower()

    if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        raise ValidationError(f"Unsupported file extension '{ext}'.")

    size = getattr(uploaded_file, "size", 0)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size <= 0:
        raise ValidationError("Uploaded file is empty.")
    if size > max_bytes:
        raise ValidationError(f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit.")

    # Read content into memory for hashing + sniffing (size already bounded).
    head = uploaded_file.read(2048)
    sha = hashlib.sha256()
    sha.update(head)
    for chunk in iter(lambda: uploaded_file.read(8192), b""):
        sha.update(chunk)
    uploaded_file.seek(0)

    if HAS_MAGIC:
        mime_type = magic.from_buffer(head, mime=True)
        # libmagic sometimes reports text/plain variants (e.g. "text/x-c")
        # for plain text. Normalize when extension is .txt.
        if ext == ".txt" and mime_type.startswith("text/"):
            mime_type = "text/plain"
    else:
        # Best-effort fallback by extension
        mime_type = {".txt": "text/plain"}.get(ext, "application/octet-stream")

    if mime_type not in settings.ALLOWED_UPLOAD_MIMETYPES:
        raise ValidationError(f"Unsupported MIME type '{mime_type}'.")

    return {
        "mime_type": mime_type,
        "extension": ext,
        "size_bytes": size,
        "sha256": sha.hexdigest(),
    }
