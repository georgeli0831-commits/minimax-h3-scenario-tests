#!/usr/bin/env python3
"""Export a supplied non-subgraph ComfyUI workflow to `/prompt` API JSON.

The script keeps graph topology unchanged.  `--set` applies a permitted test
input override only in the exported API payload, leaving the source workflow
JSON untouched.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import uuid
import urllib.request


def widget_values(node: dict) -> dict[str, object]:
    raw_values = node.get("widgets_values", [])
    if isinstance(raw_values, dict):
        return raw_values
    values = iter(raw_values)
    mapped: dict[str, object] = {}
    for input_def in node.get("inputs", []):
        if "widget" in input_def:
            try:
                mapped[input_def["name"]] = next(values)
            except StopIteration as exc:
                raise ValueError(
                    f"node {node['id']} has fewer widgets_values than widget inputs"
                ) from exc
    return mapped


def normalize_links(raw_links: list) -> dict[int, dict]:
    links: dict[int, dict] = {}
    for link in raw_links:
        if isinstance(link, list):
            link = {
                "id": link[0],
                "origin_id": link[1],
                "origin_slot": link[2],
                "target_id": link[3],
                "target_slot": link[4],
            }
        links[link["id"]] = link
    return links


def parse_override(raw: str) -> tuple[str, str, object]:
    try:
        address, value = raw.split("=", 1)
        node_id, input_name = address.split(".", 1)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--set uses NODE_ID.INPUT_NAME=VALUE") from exc
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = value
    return node_id, input_name, parsed


def export(workflow: dict, overrides: list[tuple[str, str, object]]) -> dict[str, dict]:
    links = normalize_links(workflow["links"])
    api: dict[str, dict] = {}
    for node in workflow["nodes"]:
        if node["type"] == "MarkdownNote":
            continue
        values = widget_values(node)
        inputs: dict[str, object] = {}
        for input_def in node.get("inputs", []):
            name = input_def["name"]
            # Browser-only controls are not valid workflow API inputs.
            input_type = str(input_def.get("type", ""))
            if input_type.endswith("UPLOAD") or input_type.endswith("_UI"):
                continue
            link_id = input_def.get("link")
            if link_id is not None:
                link = links[link_id]
                inputs[name] = [str(link["origin_id"]), link["origin_slot"]]
            elif name in values:
                inputs[name] = values[name]
        api[str(node["id"])] = {"class_type": node["type"], "inputs": inputs}

    for node_id, input_name, value in overrides:
        try:
            api[node_id]["inputs"][input_name] = value
        except KeyError as exc:
            raise ValueError(f"override target does not exist: {node_id}.{input_name}") from exc
    return api


def validate(prompt: dict[str, dict], object_info: dict) -> None:
    missing_types = sorted({node["class_type"] for node in prompt.values()} - set(object_info))
    if missing_types:
        raise ValueError("missing executable API types: " + ", ".join(missing_types))

    unknown_inputs: list[str] = []
    for node_id, node in prompt.items():
        spec = object_info[node["class_type"]].get("input", {})
        allowed = set(spec.get("required", {})) | set(spec.get("optional", {})) | set(spec.get("hidden", {}))

        def is_dynamic_input(name: str) -> bool:
            for collection_name, collection_spec in {**spec.get("required", {}), **spec.get("optional", {})}.items():
                if not collection_spec or collection_spec[0] != "COMFY_AUTOGROW_V3":
                    continue
                template = collection_spec[1].get("template", {})
                dynamic = template.get("input", {}).get("required", {})
                prefix = template.get("prefix")
                if prefix and name.startswith(f"{collection_name}.{prefix}"):
                    return True
                names = template.get("names", [])
                if name.startswith(f"{collection_name}.") and name.split(".", 1)[1] in names:
                    return True
            return False

        for name in node["inputs"]:
            if name not in allowed and not is_dynamic_input(name):
                unknown_inputs.append(f"{node_id}.{name}")
    if unknown_inputs:
        raise ValueError("unknown API inputs: " + ", ".join(sorted(unknown_inputs)))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--set", action="append", default=[], type=parse_override)
    parser.add_argument("--validate-url", help="ComfyUI /object_info URL")
    args = parser.parse_args()

    workflow = json.loads(args.workflow.read_text(encoding="utf-8-sig"))
    prompt = export(workflow, args.set)
    if args.validate_url:
        with urllib.request.urlopen(args.validate_url, timeout=30) as response:
            validate(prompt, json.load(response))
    payload = {"prompt": prompt, "client_id": str(uuid.uuid4())}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"exported {len(prompt)} executable nodes to {args.output}")


if __name__ == "__main__":
    main()
