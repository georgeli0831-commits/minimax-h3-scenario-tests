#!/usr/bin/env python3
"""Export the supplied H3 text-to-video workflow to ComfyUI's API format.

The bundled workflow uses a ComfyUI frontend subgraph.  The prompt API only
accepts executable node classes, so this exporter expands that subgraph without
changing any workflow setting.  The result keeps the source's 0.4 MP, 5 s and
20-step defaults unless an explicitly allowed test override is supplied.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import urllib.request
import uuid


def widget_values(node: dict) -> dict[str, object]:
    """Map a LiteGraph node's widget values to their input names."""
    values = iter(node.get("widgets_values", []))
    result: dict[str, object] = {}
    for input_def in node.get("inputs", []):
        if "widget" in input_def:
            try:
                result[input_def["name"]] = next(values)
            except StopIteration as exc:
                raise ValueError(
                    f"node {node['id']} has fewer widgets_values than widget inputs"
                ) from exc
    return result


def links_by_id(links: list[dict]) -> dict[int, dict]:
    normalized: dict[int, dict] = {}
    for link in links:
        # ComfyUI serializes ordinary graph links as positional arrays, while
        # links inside a frontend subgraph are named objects.
        if isinstance(link, list):
            link = {
                "id": link[0],
                "origin_id": link[1],
                "origin_slot": link[2],
                "target_id": link[3],
                "target_slot": link[4],
            }
        normalized[link["id"]] = link
    return normalized


def external_value(input_def: dict, ui_values: dict[str, object], link_map: dict[int, dict]):
    """Return a literal or an API link for an outer subgraph input."""
    link_id = input_def.get("link")
    if link_id is not None:
        link = link_map[link_id]
        return [str(link["origin_id"]), link["origin_slot"]]
    return ui_values.get(input_def["name"])


def api_inputs(
    node: dict,
    link_map: dict[int, dict],
    origin_rewrite,
) -> dict[str, object]:
    """Convert one serialized UI node's inputs to API inputs."""
    values = widget_values(node)
    converted: dict[str, object] = {}
    for input_def in node.get("inputs", []):
        name = input_def["name"]
        link_id = input_def.get("link")
        if link_id is not None:
            link = link_map[link_id]
            replacement = origin_rewrite(link["origin_id"], link["origin_slot"])
            if replacement is not None:
                converted[name] = replacement
        elif name in values:
            converted[name] = values[name]
    return converted


def export(workflow: dict, overrides: dict[str, object]) -> dict[str, dict]:
    subgraphs = {item["id"]: item for item in workflow.get("definitions", {}).get("subgraphs", [])}
    outer_nodes = {node["id"]: node for node in workflow["nodes"]}
    outer_link_map = links_by_id(workflow["links"])

    macro_nodes = [node for node in workflow["nodes"] if node["type"] in subgraphs]
    if len(macro_nodes) != 1:
        raise ValueError(f"expected exactly one frontend subgraph, got {len(macro_nodes)}")
    macro = macro_nodes[0]
    subgraph = subgraphs[macro["type"]]
    input_node_id = subgraph["inputNode"]["id"]
    output_node_id = subgraph["outputNode"]["id"]
    outer_values = widget_values(macro)
    for key, value in overrides.items():
        outer_values[key] = value

    macro_inputs = macro["inputs"]
    macro_slot_values = {
        slot: external_value(input_def, outer_values, outer_link_map)
        for slot, input_def in enumerate(macro_inputs)
    }

    inner_links = links_by_id(subgraph["links"])
    output_rewrites: dict[int, list[object]] = {}
    for link in inner_links.values():
        if link["target_id"] == output_node_id:
            output_rewrites[link["target_slot"]] = [str(link["origin_id"]), link["origin_slot"]]

    api: dict[str, dict] = {}

    def rewrite_inner_origin(origin_id: int, origin_slot: int):
        if origin_id == input_node_id:
            return macro_slot_values.get(origin_slot)
        return [str(origin_id), origin_slot]

    for node in subgraph["nodes"]:
        api[str(node["id"])] = {
            "class_type": node["type"],
            "inputs": api_inputs(node, inner_links, rewrite_inner_origin),
        }

    def rewrite_outer_origin(origin_id: int, origin_slot: int):
        if origin_id == macro["id"]:
            return output_rewrites.get(origin_slot)
        return [str(origin_id), origin_slot]

    for node in workflow["nodes"]:
        if node["id"] == macro["id"] or node["type"] == "MarkdownNote":
            continue
        api[str(node["id"])] = {
            "class_type": node["type"],
            "inputs": api_inputs(node, outer_link_map, rewrite_outer_origin),
        }

    return api


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--prompt")
    parser.add_argument("--duration", type=float)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--megapixels", type=float)
    parser.add_argument("--validate-url", help="ComfyUI /object_info URL")
    args = parser.parse_args()

    source = json.loads(args.workflow.read_text(encoding="utf-8-sig"))
    overrides: dict[str, object] = {}
    if args.prompt is not None:
        overrides["prompt"] = args.prompt
    if args.duration is not None:
        overrides["value_1"] = args.duration
    if args.seed is not None:
        overrides["noise_seed"] = args.seed
    if args.megapixels is not None:
        for node in source["nodes"]:
            if node["type"] == "ResolutionSelector":
                widgets = widget_values(node)
                widgets["megapixels"] = args.megapixels
                # Reconstruct ordered widget values without touching graph topology.
                node["widgets_values"] = [
                    widgets[input_def["name"]]
                    for input_def in node["inputs"]
                    if "widget" in input_def
                ]
                break

    prompt = export(source, overrides)
    if args.validate_url:
        with urllib.request.urlopen(args.validate_url, timeout=30) as response:
            registered = set(json.load(response))
        missing = sorted({entry["class_type"] for entry in prompt.values()} - registered)
        if missing:
            raise SystemExit(f"missing executable API types: {', '.join(missing)}")
    payload = {"prompt": prompt, "client_id": str(uuid.uuid4())}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"exported {len(prompt)} executable nodes to {args.output}")


if __name__ == "__main__":
    main()
