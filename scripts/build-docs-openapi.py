#!/usr/bin/env python3
"""
Build the curated OpenAPI spec that Mintlify renders for the public API reference.

Reads the full upstream spec (api-reference/openapi.source.json) and writes a
curated copy (api-reference/openapi.json) with operational / vendor-webhook /
internal endpoints removed and a few rendering fixes applied.

To refresh after an API update:
  1. Overwrite api-reference/openapi.source.json with the new upstream spec.
  2. Run:  python3 scripts/build-docs-openapi.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "api-reference", "openapi.source.json")
OUT = os.path.join(ROOT, "api-reference", "openapi.json")

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}

# Whole tags that are operational / internal and never invoked by API consumers.
HIDE_TAGS = {
    "warm-transfer",        # Twilio voice webhooks (vendor -> us)
    "benchmarking-internal",  # internal benchmarking sweeps
    "voice-admin",          # /v1/internal/voice admin upserts
}

# Individual operations to hide, keyed by (METHOD, path).
HIDE_OPERATIONS = {
    ("POST", "/sms/inbound"),            # inbound SMS webhook (vendor -> us)
    ("POST", "/sms/status/{turn_id}"),   # SMS delivery-status callback (vendor -> us)
    ("GET", "/sms/healthz"),             # health probe
    ("GET", "/health"),                  # health probe
    ("GET", "/ready"),                   # readiness probe
}

# Any path containing one of these fragments is operational/internal infra.
HIDE_PATH_FRAGMENTS = ("/_internal/", "/internal/", "/twilio/")


def should_hide(method: str, path: str, op: dict) -> bool:
    tags = op.get("tags") or []
    if any(t in HIDE_TAGS for t in tags):
        return True
    if (method.upper(), path) in HIDE_OPERATIONS:
        return True
    if any(frag in path for frag in HIDE_PATH_FRAGMENTS):
        return True
    return False


def enforce_apikey_auth(op: dict) -> None:
    """Customers authenticate with an API key only (x-api-key header). Drop the
    HTTPBearer alternative so the generated playground advertises API-key auth
    exclusively."""
    sec = op.get("security")
    if not sec:
        return
    sec = [req for req in sec if "HTTPBearer" not in req]
    op["security"] = sec or [{"APIKeyHeader": []}]


def fix_descriptions(op: dict) -> None:
    """Wrap raw `{...}` JSON examples in fenced code blocks so Mintlify's MDX
    renderer doesn't try to evaluate them as JSX expressions."""
    if op.get("operationId") == "bulkIngest":
        op["description"] = (
            "Unified document ingestion endpoint.\n\n"
            "Accepts a multipart form with:\n"
            "- `manifest` (required): JSON array describing each item\n"
            "- `files` (optional): one or more file uploads, referenced by "
            "`file_index` in the manifest\n\n"
            "Manifest format (JSON array):\n\n"
            "```json\n"
            "[\n"
            '  {"type": "file", "file_index": 0, "title": "Report"},\n'
            '  {"type": "text", "title": "FAQ", "content": "What is..."},\n'
            '  {"type": "file", "file_index": 1, "title": "Old Report", "document_id": "uuid"}\n'
            "]\n"
            "```"
        )


def main() -> int:
    with open(SRC) as f:
        spec = json.load(f)

    # Brand the spec title (upstream ships "CX Platform API").
    spec.setdefault("info", {})["title"] = "Feather API"

    paths = spec.get("paths", {})
    kept = 0
    hidden = 0
    used_tags = set()

    for path in list(paths.keys()):
        item = paths[path]
        for method in list(item.keys()):
            if method.lower() not in HTTP_METHODS:
                continue
            op = item[method]
            if should_hide(method, path, op):
                del item[method]
                hidden += 1
                continue
            fix_descriptions(op)
            enforce_apikey_auth(op)
            for t in (op.get("tags") or []):
                used_tags.add(t)
            kept += 1
        # Drop path entries that no longer have any operations.
        if not any(m.lower() in HTTP_METHODS for m in item):
            del paths[path]

    # Trim the top-level tag list to only tags still in use.
    if "tags" in spec:
        spec["tags"] = [t for t in spec["tags"] if t.get("name") in used_tags]

    # Customers use the API key only; drop the other auth schemes entirely.
    schemes = spec.get("components", {}).get("securitySchemes")
    if schemes:
        spec["components"]["securitySchemes"] = {
            k: v for k, v in schemes.items() if k == "APIKeyHeader"
        }

    with open(OUT, "w") as f:
        json.dump(spec, f, indent=2)
        f.write("\n")

    print(f"kept {kept} operations, hid {hidden}")
    print(f"output: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
