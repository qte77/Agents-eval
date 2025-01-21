"""
https://github.com/technovangelist/omar
"""

import os
import json
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass
from typing import List
from pathlib import Path

import pytz


# MARK: Data Structures


@dataclass
class ModelLayer:
    media_type: str
    digest: str
    size: int


@dataclass
class ModelManifest:
    layers: List[ModelLayer]


@dataclass
class ModelUsage:
    name: str
    last_used: datetime
    usage_count: int
    size: int


# region Utility Functions


def get_model_dir():
    custom_path = os.environ.get("OLLAMA_MODELS")
    if custom_path:
        return Path(custom_path)

    if os.name == "posix":
        return Path.home() / ".ollama" / "models"
    elif os.name == "nt":
        return Path.home() / ".ollama"
    else:
        return Path("/usr/share/ollama")


def get_log_paths():
    if os.name == "posix":
        log_dir = Path.home() / ".ollama" / "logs"
        paths = sorted(log_dir.glob("server*.log"), reverse=True)
        return paths
    elif os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return [Path(local_app_data) / "Ollama"]
    return []


def parse_manifest_path(path):
    components = path.parts
    if len(components) >= 4:
        user = components[-3]
        model = components[-2]
        tag = os.path.basename(path)

        prefix = "" if user == "library" else f"{user}/"
        return f"{prefix}{model}:{tag}"
    return None

    # endregion Utility Functions
    # region Model Manifest Processing


def find_model_manifests():
    hash_to_name_size = defaultdict(lambda: ("", 0))
    model_dir = get_model_dir()
    manifest_dir = model_dir / "manifests"

    for path in manifest_dir.rglob("*"):
        if path.is_file():
            try:
                with path.open("r") as f:
                    manifest = json.load(f)
                    for layer in manifest.get("layers", []):
                        if (
                            layer.get("mediaType")
                            == "application/vnd.ollama.image.model"
                        ):
                            hash = layer["digest"].replace("sha256:", "")
                            if model_name := parse_manifest_path(path):
                                current_name, current_size = hash_to_name_size[hash]
                                new_name = (
                                    f"{current_name}, {model_name}"
                                    if current_name
                                    else model_name
                                )
                                hash_to_name_size[hash] = (new_name, layer["size"])
            except json.JSONDecodeError:
                continue

    return dict(hash_to_name_size)


# region Model Manifest Processing
# region logparsing


def parse_logs(hash_to_name_size):
    model_usage = {}
    log_paths = get_log_paths()
    seen_hashes = set()

    for log_path in log_paths:
        file_time = datetime.fromtimestamp(os.path.getmtime(log_path))
        last_timestamp = None

        with open(log_path, "r") as file:
            for line in file:
                if line.startswith("time="):
                    try:
                        last_timestamp = datetime.fromisoformat(line[5:].strip())
                    except ValueError:
                        pass
                elif len(line) > 19 and line[4] == "/" and line[7] == "/":
                    try:
                        last_timestamp = datetime.strptime(
                            line[:19], "%Y/%m/%d %H:%M:%S"
                        )
                    except ValueError:
                        pass
                elif "llama_model_loader: loaded meta data" in line:
                    hash_start = line.find("sha256-")
                    if hash_start != -1:
                        hash = line[hash_start + 7 : hash_start + 71]
                        seen_hashes.add(hash)

                        model_name, size = hash_to_name_size.get(
                            hash, (f"{hash[:8]}...-deleted", 0)
                        )

                        if model_name not in model_usage:
                            model_usage[model_name] = ModelUsage(
                                name=model_name,
                                last_used=last_timestamp or file_time,
                                usage_count=0,
                                size=size,
                            )

                        model_usage[model_name].usage_count += 1
                        if (
                            last_timestamp
                            and last_timestamp > model_usage[model_name].last_used
                        ):
                            model_usage[model_name].last_used = last_timestamp

    return model_usage


# endregion logparsing
# region Output Formatting


def format_size(size):
    gb = size / (1024**3)
    if gb >= 1.0:
        return f"{gb:.1f} GB"
    mb = size / (1024**2)
    return f"{mb:.1f} MB"


def print_table(models, title):
    if not models:
        return

    is_deleted = any(m.name.endswith("-deleted") for m in models)
    is_unlogged = all(
        m.usage_count == 0 and m.last_used == datetime.now(pytz.UTC) for m in models
    )

    model_width = max(len("Model"), max(len(m.name) for m in models))
    last_used_width = max(len("Last Used"), 10) if not is_unlogged else 0
    usage_count_width = (
        max(len("Usage Count"), max(len(str(m.usage_count)) for m in models))
        if not is_unlogged
        else 0
    )
    show_size = not is_deleted
    size_width = (
        max(len("Size"), max(len(format_size(m.size)) for m in models))
        if show_size
        else 0
    )

    print(f"\n{title}")
    if is_unlogged:
        print(f"{'Model':<{model_width}}  {'Size':>{size_width}}")
        print(f"{'-' * model_width}  {'-' * size_width}")
        for usage in models:
            print(
                f"{usage.name:<{model_width}}  {format_size(usage.size):>{size_width}}"
            )
    elif show_size:
        print(
            f"{'Model':<{model_width}}  {'Last Used':<{last_used_width}}  {'Usage Count':>{usage_count_width}}  {'Size':>{size_width}}"
        )
        print(
            f"{'-' * model_width}  {'-' * last_used_width}  {'-' * usage_count_width}  {'-' * size_width}"
        )
        for usage in models:
            print(
                f"{usage.name:<{model_width}}  {usage.last_used.strftime('%Y-%m-%d'):<{last_used_width}}  {usage.usage_count:>{usage_count_width}}  {format_size(usage.size):>{size_width}}"
            )
    else:
        print(
            f"{'Model':<{model_width}}  {'Last Used':<{last_used_width}}  {'Usage Count':>{usage_count_width}}"
        )
        print(
            f"{'-' * model_width}  {'-' * last_used_width}  {'-' * usage_count_width}"
        )
        for usage in models:
            print(
                f"{usage.name:<{model_width}}  {usage.last_used.strftime('%Y-%m-%d'):<{last_used_width}}  {usage.usage_count:>{usage_count_width}}"
            )


# endregion Output Formatting
# region Main Function


def parse_ollama_logs():

    print("Starting to parse...")

    hash_to_name_size = find_model_manifests()
    model_usage = parse_logs(hash_to_name_size)

    active_models = [m for m in model_usage.values() if not m.name.endswith("-deleted")]
    deleted_models = [m for m in model_usage.values() if m.name.endswith("-deleted")]

    for models in [active_models, deleted_models]:
        models.sort(key=lambda m: (m.last_used, m.usage_count), reverse=True)

    unlogged_models = [
        (name, size)
        for names, size in hash_to_name_size.values()
        for name in names.split(", ")
        if not any(name in m.name.split(", ") for m in model_usage.values())
    ]
    unlogged_models.sort(key=lambda x: x[0])

    print_table(active_models, "Active Models:")

    if unlogged_models:
        print("\nUnlogged Models:")
        print("---------------")
        model_width = max(len("Model"), max(len(name) for name, _ in unlogged_models))
        size_width = max(
            len("Size"), max(len(format_size(size)) for _, size in unlogged_models)
        )
        print(f"{'Model':<{model_width}}  {'Size':>{size_width}}")
        print(f"{'-' * model_width}  {'-' * size_width}")
        for name, size in unlogged_models:
            print(f"{name:<{model_width}}  {format_size(size):>{size_width}}")

    print_table(deleted_models, "Deleted Models:")
    print()


# endregion Main Function
