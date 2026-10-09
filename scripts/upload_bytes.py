#!/usr/bin/env python3
"""Upload one local file using a FlowUs pre-signed transaction from stdin."""

from __future__ import annotations

import argparse
import getpass
import json
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="Local file whose bytes will be uploaded")
    args = parser.parse_args()
    source = Path(args.file).expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"Local upload file does not exist: {source}")

    raw_transaction = getpass.getpass("") if sys.stdin.isatty() else sys.stdin.readline()
    transaction = json.loads(raw_transaction)
    method = str(transaction["method"]).upper()
    url = str(transaction["upload_url"])
    headers = {str(key): str(value) for key, value in transaction.get("headers", {}).items()}
    if method not in {"PUT", "POST"}:
        raise SystemExit(f"Refusing unsupported upload method: {method}")
    if urlparse(url).scheme != "https":
        raise SystemExit("Refusing non-HTTPS upload URL")

    request = urllib.request.Request(url, data=source.read_bytes(), headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=120) as response:
        status = response.status
    if not 200 <= status < 300:
        raise SystemExit(f"Upload failed with HTTP {status}")
    print(json.dumps({"ok": True, "status": status, "bytes": source.stat().st_size}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
