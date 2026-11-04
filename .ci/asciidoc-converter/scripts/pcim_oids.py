"""PCIM review OIDs from the deliberately restricted entity table in AsciiDoc.

This is not a general AsciiDoc parser. Entity cells must be plain values with
the documented anchor/xref forms; attributes, nested tables and includes are
rejected rather than interpreted differently from the renderer.
"""

import re

HEADER = ["type", "local_id", "oid", "allocation_status", "definition", "authority_or_decision"]
TYPES = {"profile", "actor", "transaction", "profile_actor_option", "use_case"}
SCOPE_TYPES = {"actors": "actor", "transactions": "transaction",
               "options": "profile_actor_option", "useCases": "use_case"}


def valid_oid(oid):
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*))+", oid):
        return False
    parts = [int(part) for part in oid.split(".")]
    return parts[0] in (0, 1, 2) and (parts[0] == 2 or parts[1] <= 39)


def read_entities(path):
    text = path.read_text(encoding="utf-8")
    pieces = text.split("|===")
    if len(pieces) != 3 or "role=pcim_oid_registry" not in pieces[0] or pieces[2].strip():
        raise ValueError("OID registry must contain exactly one pcim_oid_registry table")
    cells = [cell.strip() for cell in pieces[1].split("|")[1:]]
    if cells[:6] != HEADER or len(cells) % 6:
        raise ValueError("OID registry must have the six documented columns")
    entities = []
    for i in range(6, len(cells), 6):
        kind, local, oid, status, definition, authority = cells[i:i + 6]
        local_match = re.fullmatch(r"\[\[(pcim-oid-[a-z0-9-]+)\]\]([A-Za-z0-9_-]+)", local)
        ref_match = re.fullmatch(r"<<([a-z0-9-]+),([^<>\n]+)>>", definition)
        if (kind not in TYPES or not local_match or not ref_match or not valid_oid(oid)
                or status not in {"existing", "reserved-root", "proposed"}
                or not authority or any(c in authority for c in "{}[]<>")):
            raise ValueError(f"Invalid OID registry entry: {local}")
        entities.append({"type": kind, "id": local_match[2], "oid": oid,
                         "uri": "urn:oid:" + oid, "allocationStatus": status,
                         "registryAnchor": local_match[1], "anchor": ref_match[1],
                         "label": ref_match[2], "authorityOrDecision": authority})
    return entities


def apply_oids(requirements, entities, source_text):
    ids, oids, anchors = set(), set(), set()
    roots = [e for e in entities if e["type"] == "profile" and e["id"] == "PCIM"]
    if len(roots) != 1:
        raise ValueError("Exactly one PCIM profile root is required")
    root = roots[0]["oid"]
    known = {}
    for entity in entities:
        key = (entity["type"], entity["id"])
        if key in ids or entity["oid"] in oids or entity["registryAnchor"] in anchors:
            raise ValueError(f"Duplicate entity identity: {entity['id']}")
        if f"[[{entity['anchor']}]]" not in source_text:
            raise ValueError(f"Unknown entity definition: {entity['anchor']}")
        ids.add(key)
        oids.add(entity["oid"])
        anchors.add(entity["registryAnchor"])
        known[key] = entity
    for requirement in requirements:
        match = re.fullmatch(r"PCIMR([0-9]{4})", requirement["id"])
        if not match or int(match[1]) == 0:
            raise ValueError(f"Invalid requirement ID: {requirement['id']}")
        oid = f"{root}.10.{int(match[1])}"
        if oid in oids:
            raise ValueError(f"Duplicate OID: {oid}")
        oids.add(oid)
        requirement.update(oid=oid, uri="urn:oid:" + oid, allocationStatus="proposed")
        refs = {}
        for scope, kind in SCOPE_TYPES.items():
            refs[scope] = []
            for local_id in requirement["scope"][scope]:
                entity = known.get((kind, local_id))
                if entity is None:
                    raise ValueError(f"{requirement['id']}: unknown {kind} {local_id}")
                refs[scope].append({k: entity[k] for k in ("id", "oid", "uri", "allocationStatus")})
        requirement["scopeReferences"] = refs
    return root


def render_attributes(requirements, entities):
    lines = ["// Generated for review; edit entity registry or requirement blocks, not this file."]
    lines += [f":{e['registryAnchor']}: {e['oid']}" for e in entities]
    lines += [f":pcim-oid-{r['anchor']}: {r['oid']}" for r in requirements]
    return "\n".join(lines) + "\n"


def render_requirement_table(requirements):
    lines = ['// Generated from the requirements model.',
             '[#pcim-requirement-oid-table,cols="1,3,1,2",options="header"]',
             '|===', '|Requirement |Proposed OID |Level |Type']
    for req in requirements:
        lines.append(f"|<<{req['anchor']},{req['id']}>> |{req['oid']} |{req['level']} |{req['type']}")
    return "\n".join(lines + ['|===', ''])
