#!/usr/bin/env python3
"""Extract PCIM semantic requirement blocks from AsciiDoc into JSON."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


TITLE_RE = re.compile(r"^\.(PCIMR\d{4})\s*$")
ATTR_RE = re.compile(r"^\[pcim_requirement#(pcimr\d{4})(?P<attrs>.*)\]\s*$")
SECTION_RE = re.compile(r"^(=+)\s+(.+?)\s*$")
CONTENT_TAG_RE = re.compile(
    r"^\[(NORMATIVE|VERIFICATION|NOTE|RATIONALE|RELATED|EXAMPLE)\]\s*$"
)

LIST_METADATA = {
    "pcim_actor",
    "pcim_transaction",
    "pcim_option",
    "pcim_use_case",
    "pcim_message",
    "pcim_segment",
}


def git_value(args, cwd):
    try:
        return subprocess.check_output(
            ["git", *args], cwd=cwd, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def split_attrs(attr_text):
    if attr_text.startswith(","):
        attr_text = attr_text[1:]

    parts = []
    current = []
    quote = None
    escape = False

    for char in attr_text:
        if escape:
            current.append(char)
            escape = False
            continue
        if char == "\\":
            current.append(char)
            escape = True
            continue
        if quote:
            current.append(char)
            if char == quote:
                quote = None
            continue
        if char in ("'", '"'):
            current.append(char)
            quote = char
            continue
        if char == ",":
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
            continue
        current.append(char)

    part = "".join(current).strip()
    if part:
        parts.append(part)

    attrs = {}
    for part in parts:
        if "=" not in part:
            attrs[part] = True
            continue
        key, value = part.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        attrs[key.strip()] = value
    return attrs


def as_list(metadata, key):
    value = metadata.get(key)
    if value is None or value is True:
        return []
    return [item.strip() for item in str(value).split(",") if item.strip()]


def normalize_text(lines):
    return "\n".join(line.rstrip() for line in lines).strip()


def parse_content_blocks(lines, start, end, errors):
    blocks = {}
    i = start
    while i < end:
        tag_match = CONTENT_TAG_RE.match(lines[i])
        if not tag_match:
            i += 1
            continue

        tag = tag_match.group(1).lower()
        fence_line = i + 1
        if fence_line >= end or lines[fence_line].strip() != "====":
            errors.append(f"line {i + 1}: [{tag.upper()}] must be followed by ====")
            i += 1
            continue

        content_start = fence_line + 1
        content_end = content_start
        while content_end < end and lines[content_end].strip() != "====":
            content_end += 1

        if content_end >= end:
            errors.append(f"line {i + 1}: [{tag.upper()}] block is not closed")
            break

        blocks.setdefault(tag, []).append(normalize_text(lines[content_start:content_end]))
        i = content_end + 1
    return blocks


def parse_requirements(source_path, repo_root):
    lines = source_path.read_text(encoding="utf-8").splitlines()
    requirements = []
    errors = []
    section_stack = []
    seen = {}
    i = 0

    while i < len(lines):
        section_match = SECTION_RE.match(lines[i])
        if section_match:
            level = len(section_match.group(1))
            title = section_match.group(2).strip()
            section_stack = section_stack[: level - 1]
            section_stack.append({"level": level, "title": title, "line": i + 1})

        title_match = TITLE_RE.match(lines[i])
        if not title_match:
            i += 1
            continue

        req_id = title_match.group(1)
        attr_line = i + 1
        if attr_line >= len(lines):
            errors.append(f"line {i + 1}: requirement title has no attribute line")
            i += 1
            continue

        attr_match = ATTR_RE.match(lines[attr_line])
        if not attr_match:
            errors.append(f"line {i + 1}: requirement title is not followed by pcim_requirement block")
            i += 1
            continue

        anchor = attr_match.group(1)
        expected_anchor = req_id.lower()
        if anchor != expected_anchor:
            errors.append(
                f"line {attr_line + 1}: anchor {anchor} does not match {expected_anchor}"
            )

        metadata = split_attrs(attr_match.group("attrs"))
        level = metadata.get("pcim_req_level")
        req_type = metadata.get("pcim_req_type")
        if level not in {"shall", "should", "may"}:
            errors.append(f"line {attr_line + 1}: pcim_req_level is required")
        if not req_type:
            errors.append(f"line {attr_line + 1}: pcim_req_type is required")

        block_start = attr_line + 1
        while block_start < len(lines) and not lines[block_start].strip():
            block_start += 1
        if block_start >= len(lines) or lines[block_start].strip() != "****":
            errors.append(f"line {attr_line + 1}: pcim_requirement block must start with ****")
            i += 1
            continue

        block_end = block_start + 1
        while block_end < len(lines) and lines[block_end].strip() != "****":
            block_end += 1
        if block_end >= len(lines):
            errors.append(f"line {block_start + 1}: pcim_requirement block is not closed")
            i += 1
            continue

        content = parse_content_blocks(lines, block_start + 1, block_end, errors)
        normative = content.get("normative", [])
        if len(normative) != 1:
            errors.append(f"line {i + 1}: requirement must contain exactly one [NORMATIVE] block")

        if req_id in seen:
            errors.append(f"line {i + 1}: duplicate requirement id {req_id}")
        seen[req_id] = i + 1

        rel_source = str(source_path.relative_to(repo_root))
        requirement = {
            "id": req_id,
            "anchor": anchor,
            "level": level,
            "type": req_type,
            "status": metadata.get("pcim_req_status", "active"),
            "source": {
                "repository": "IHE/DEV.PCIM",
                "file": rel_source,
                "line": i + 1,
                "sectionPath": [section["title"] for section in section_stack],
            },
            "scope": {
                "actors": as_list(metadata, "pcim_actor"),
                "transactions": as_list(metadata, "pcim_transaction"),
                "options": as_list(metadata, "pcim_option"),
                "useCases": as_list(metadata, "pcim_use_case"),
                "messages": as_list(metadata, "pcim_message"),
                "segments": as_list(metadata, "pcim_segment"),
            },
            "metadata": metadata,
            "normativeText": normative[0] if normative else "",
            "verification": {
                "method": metadata.get("pcim_verification_method"),
                "level": metadata.get("pcim_verification_level"),
                "text": "\n\n".join(content.get("verification", [])),
            },
            "notes": content.get("note", []),
            "rationale": content.get("rationale", []),
            "related": content.get("related", []),
            "examples": content.get("example", []),
        }
        requirements.append(requirement)
        i = block_end + 1

    return requirements, errors


def read_doc_attrs(source_path):
    attrs = {}
    for line in source_path.read_text(encoding="utf-8").splitlines():
        if line.startswith(":revnumber:"):
            attrs["revnumber"] = line.split(":", 2)[2].strip()
        elif line.startswith("Date:"):
            attrs["date"] = line.split(":", 1)[1].strip()
    return attrs


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output")
    parser.add_argument("--trace-output")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate requirement blocks without writing JSON artifacts.",
    )
    parser.add_argument(
        "--omit-commit",
        action="store_true",
        help="Write null for the source commit to keep generated review fixtures stable.",
    )
    args = parser.parse_args()

    if not args.check_only and not args.output:
        parser.error("--output is required unless --check-only is used")

    repo_root = Path.cwd().resolve()
    source_path = (repo_root / args.source).resolve()
    output_path = (repo_root / args.output).resolve() if args.output else None
    trace_path = (repo_root / args.trace_output).resolve() if args.trace_output else None

    requirements, errors = parse_requirements(source_path, repo_root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    requirements.sort(key=lambda requirement: requirement["id"])

    if args.check_only:
        print(f"Validated {len(requirements)} PCIM requirement identifiers")
        return 0

    doc_attrs = read_doc_attrs(source_path)
    commit = None if args.omit_commit else git_value(["rev-parse", "HEAD"], repo_root)

    artifact = {
        "$schema": "https://profiles.ihe.net/DEV/PCIM/schemas/pcim-requirements.schema.json",
        "artifactType": "pcim-requirements",
        "profile": "PCIM",
        "source": {
            "repository": "IHE/DEV.PCIM",
            "file": str(source_path.relative_to(repo_root)),
            "commit": commit,
            "revision": doc_attrs.get("revnumber"),
            "publicationDate": doc_attrs.get("date"),
        },
        "count": len(requirements),
        "requirements": requirements,
    }
    write_json(output_path, artifact)

    if trace_path:
        trace = {
            "$schema": "https://profiles.ihe.net/DEV/PCIM/schemas/pcim-requirement-trace.schema.json",
            "artifactType": "pcim-requirement-trace",
            "profile": "PCIM",
            "source": artifact["source"],
            "count": len(requirements),
            "requirements": [
                {
                    "id": requirement["id"],
                    "level": requirement["level"],
                    "type": requirement["type"],
                    "source": requirement["source"],
                    "scope": requirement["scope"],
                    "verification": requirement["verification"],
                }
                for requirement in requirements
            ],
        }
        write_json(trace_path, trace)

    print(f"Extracted {len(requirements)} PCIM requirements to {output_path}")
    if trace_path:
        print(f"Wrote PCIM requirement trace to {trace_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
