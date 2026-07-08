# -*- coding: utf-8 -*-
"""routing.yaml 轻量解析（无 PyYAML 依赖）。"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Task:
    id: str
    labels: dict[str, str] = field(default_factory=dict)
    trigger_examples: list[str] = field(default_factory=list)
    required_reads: list[str] = field(default_factory=list)
    route: str = ""
    workflow: str = ""
    script: str = ""


@dataclass
class Manifest:
    always_read: list[str]
    first_use: list[str]
    tasks: list[Task]
    common_task_ids: list[str]
    fuzzy_workflow: str = ""


def _clean(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _parse_inline_list(value: str) -> list[str]:
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        return []
    inner = value[1:-1].strip()
    if not inner:
        return []
    return [_clean(part.strip()) for part in inner.split(",") if part.strip()]


def _parse_inline_map(value: str) -> dict[str, str]:
    value = value.strip()
    if not (value.startswith("{") and value.endswith("}")):
        return {}
    inner = value[1:-1].strip()
    result: dict[str, str] = {}
    for part in inner.split(","):
        if ":" not in part:
            continue
        key, item = part.split(":", 1)
        result[_clean(key).strip()] = _clean(item)
    return result


def parse_manifest(text: str) -> Manifest:
    always_read: list[str] = []
    first_use: list[str] = []
    common_task_ids: list[str] = []
    tasks: list[Task] = []
    current: Task | None = None
    section: str | None = None
    top_section: str | None = None
    fuzzy_workflow = ""

    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        stripped = raw.strip()

        if stripped == "always_read:":
            top_section = "always_read"
            current = None
            section = None
            continue
        if stripped == "first_use:":
            top_section = "first_use"
            current = None
            section = None
            continue
        if stripped == "tasks:":
            top_section = "tasks"
            section = None
            continue
        if stripped == "skill_sync:":
            top_section = "skill_sync"
            current = None
            section = None
            continue

        if top_section == "always_read" and raw.startswith("  - "):
            always_read.append(_clean(stripped[2:]))
            continue
        if top_section == "first_use" and raw.startswith("  - "):
            first_use.append(_clean(stripped[2:]))
            continue
        if top_section == "skill_sync" and stripped == "common_tasks:":
            section = "common_tasks"
            continue
        if section == "common_tasks" and raw.startswith("    - "):
            common_task_ids.append(_clean(stripped[2:]))
            continue

        if raw.startswith("  - id:"):
            current = Task(id=_clean(raw.split(":", 1)[1]))
            tasks.append(current)
            section = None
            continue
        if current is None:
            if stripped.startswith("workflow:") and "fuzzy" in text.split(stripped)[0][-200:]:
                pass
            if "fuzzy_intent:" in text and stripped.startswith("workflow:"):
                # handled below via regex after loop
                pass
            continue

        if raw.startswith("    labels:"):
            section = "labels"
            _, value = stripped.split(":", 1)
            current.labels.update(_parse_inline_map(value))
            if value.strip().startswith("{"):
                section = None
            continue
        if raw.startswith("    required_reads:"):
            section = "required_reads"
            _, value = stripped.split(":", 1)
            current.required_reads.extend(_parse_inline_list(value))
            if value.strip().startswith("["):
                section = None
            continue
        if raw.startswith("    trigger_examples:"):
            section = "trigger_examples"
            _, value = stripped.split(":", 1)
            current.trigger_examples.extend(_parse_inline_list(value))
            if value.strip().startswith("["):
                section = None
            continue
        if section == "labels" and raw.startswith("      ") and ":" in stripped:
            key, value = stripped.split(":", 1)
            current.labels[key.strip()] = _clean(value)
            continue
        if section == "required_reads" and raw.startswith("      - "):
            current.required_reads.append(_clean(stripped[2:]))
            continue
        if section == "trigger_examples" and raw.startswith("      - "):
            current.trigger_examples.append(_clean(stripped[2:]))
            continue
        if raw.startswith("    ") and ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = _clean(value)
            if key == "route":
                current.route = value
            elif key == "workflow":
                current.workflow = value
            elif key == "script":
                current.script = value
            section = None

    m = re.search(
        r"fuzzy_intent:\s*\n(?:.*\n)*?\s+workflow:\s*(\S+)",
        text,
    )
    if m:
        fuzzy_workflow = m.group(1)

    return Manifest(
        always_read=always_read,
        first_use=first_use,
        tasks=tasks,
        common_task_ids=common_task_ids,
        fuzzy_workflow=fuzzy_workflow,
    )


def load_manifest(root: Path) -> Manifest:
    text = (root / "routing.yaml").read_text(encoding="utf-8")
    return parse_manifest(text)


def task_by_id(manifest: Manifest, task_id: str) -> Task | None:
    for task in manifest.tasks:
        if task.id == task_id:
            return task
    return None