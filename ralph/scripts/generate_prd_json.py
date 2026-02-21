#!/usr/bin/env python3
"""Generate ralph/docs/prd.json from a PRD markdown file.

Data-driven parser that extracts project metadata from YAML frontmatter,
features with sub-features, and story breakdown mappings from any PRD.md.
Supports incremental updates with content hashing.

CRITICAL SAFETY RULES:
1. NEVER modify stories marked as passed (status: "passed")
2. Only append new stories that don't already exist
3. Only update incomplete stories (status != "passed") if fields are missing
4. Preserve all existing story metadata (completed_at, content_hash, etc.)
"""

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict


class Story(TypedDict):
    """A single work item extracted from the PRD."""

    id: str
    title: str
    description: str
    acceptance: list[str]
    files: list[str]
    status: str  # "pending" | "in_progress" | "passed" | "failed"
    wave: int  # 1-indexed BFS level in dependency graph (0 = uncomputed)
    completed_at: str | None
    content_hash: str
    depends_on: list[str]


class SubFeature(TypedDict):
    """A sub-feature section (e.g. 5.1, 6.2) parsed from the PRD."""

    number: str
    acceptance: list[str]
    files: list[str]


class StorySpec(TypedDict):
    """A story specification extracted from the breakdown section."""

    id: str
    title: str
    feature_id: str
    label: str
    depends_on: list[str]


class Feature(TypedDict):
    """A feature section parsed from the PRD."""

    number: str
    name: str
    description: str
    acceptance: list[str]
    files: list[str]


def compute_hash(title: str, description: str, acceptance: list[str]) -> str:
    """Compute SHA-256 hash of story content for change detection."""
    content = f"{title}|{description}|{json.dumps(acceptance, sort_keys=True)}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def story_sort_key(story_id: str) -> tuple[int, str]:
    """Sort key for story IDs that handles alphanumeric suffixes.

    Args:
        story_id: Full story ID like "STORY-010b" or "STORY-003".

    Returns:
        Tuple of (numeric_part, alpha_suffix) for stable ordering.
    """
    suffix = story_id.split("-")[1]
    num_match = re.match(r"\d+", suffix)
    num = int(num_match.group()) if num_match else 0
    alpha = re.search(r"[a-z]+$", suffix)
    return (num, alpha.group() if alpha else "")


def parse_frontmatter(prd_content: str) -> dict[str, str]:
    """Extract YAML frontmatter key-value pairs from PRD content.

    Args:
        prd_content: Raw PRD markdown content.

    Returns:
        Dict of frontmatter fields (e.g. title, description, version).
    """
    match = re.match(r"^---\s*\n(.*?)\n---", prd_content, re.DOTALL)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).split("\n"):
        kv = line.split(":", 1)
        if len(kv) == 2:
            result[kv[0].strip()] = kv[1].strip()
    return result


def extract_project_name(frontmatter: dict[str, str]) -> str:
    """Extract project name from frontmatter title field.

    Tries several patterns: bold **Name**, "for Name" suffix,
    then falls back to the raw title value.

    Args:
        frontmatter: Parsed frontmatter dict.

    Returns:
        Project name string.
    """
    title = frontmatter.get("title", "")
    # Reason: PRD titles use different conventions for the project name
    bold_match = re.search(r"\*\*([^*]+)\*\*", title)
    if bold_match:
        return bold_match.group(1)
    for_match = re.search(r"\bfor\s+(.+)$", title)
    if for_match:
        return for_match.group(1).strip()
    if title:
        return title
    return "Unknown Project"


def _extract_acceptance(content: str) -> list[str]:
    """Extract acceptance criteria from a markdown section.

    Args:
        content: Markdown content containing acceptance criteria.

    Returns:
        List of acceptance criterion strings.
    """
    acceptance: list[str] = []
    # Reason: PRD uses varying indentation (0 or 2 spaces) before "- [ ]"
    # \n? tolerates optional blank line between header and first item (markdownlint)
    acceptance_match = re.search(
        r"\*\*Acceptance Criteria\*\*:\s*\n\n?((?:\s*- \[[x ]\][^\n]+\n)+)",
        content,
        re.DOTALL,
    )
    if acceptance_match:
        for line in acceptance_match.group(1).split("\n"):
            if line.strip().startswith("- ["):
                criterion = re.sub(r"^- \[[x ]\]\s*", "", line.strip())
                if criterion:
                    acceptance.append(criterion)
    return acceptance


def _extract_files(content: str) -> list[str]:
    """Extract file paths from a markdown section.

    Args:
        content: Markdown content containing file listings.

    Returns:
        List of file path strings.
    """
    files: list[str] = []
    # Reason: PRD uses varying indentation (0 or 2 spaces) before "- `path`"
    # \n? tolerates optional blank line between header and first item (markdownlint)
    files_match = re.search(
        r"\*\*Files(?:\s+Implemented)?\*\*:\s*\n\n?((?:\s*- `[^`]+`[^\n]*\n?)+)",
        content,
        re.DOTALL,
    )
    if not files_match:
        return files
    for line in files_match.group(1).split("\n"):
        file_match = re.search(r"`([^`]+)`", line)
        if file_match:
            file_path = file_match.group(1).split(" - ")[0].strip()
            file_path = re.sub(r"\s*\([^)]+\)\s*$", "", file_path)
            files.append(file_path)
    return files


def _extract_tech_requirements(content: str) -> list[str]:
    """Extract Technical Requirements items from a feature section.

    Stops at code fences (```) to avoid truncating items that precede
    fenced blocks (e.g. ``- Update table:\\n```markdown``).

    Args:
        content: Markdown content of a feature section.

    Returns:
        List of requirement strings.
    """
    requirements: list[str] = []
    # Reason: Match consecutive "- " lines, stopping at code fences or non-list lines
    # \n? tolerates optional blank line between header and first item (markdownlint)
    match = re.search(
        r"\*\*Technical Requirements\*\*:\s*\n\n?((?:- [^\n]+\n)+)",
        content,
        re.DOTALL,
    )
    if not match:
        return requirements
    for line in match.group(1).split("\n"):
        # Reason: Stop before code fences that break the list pattern
        if line.strip().startswith("```"):
            break
        if line.strip().startswith("- "):
            req = line.strip()[2:].strip()
            # Reason: Skip items ending with ":" that introduce a code block —
            # the content is in the fence, not the list item
            if req and not req.endswith(":"):
                requirements.append(req)
    return requirements


def parse_subfeatures(feature_content: str) -> dict[str, SubFeature]:
    """Parse sub-features from feature content (e.g. 5.1, 6.2).

    Args:
        feature_content: Raw markdown content of a single feature section.

    Returns:
        Dict mapping sub-feature name to SubFeature data.
    """
    sub_features: dict[str, SubFeature] = {}
    sub_feature_pattern = r"##### (\d+[a-z]?\.\d+) ([^\n]+)\s*\n(.*?)(?=\n#####|\Z)"

    for match in re.finditer(sub_feature_pattern, feature_content, re.DOTALL):
        sub_name = match.group(2).strip()
        sub_features[sub_name] = {
            "number": match.group(1),
            "acceptance": _extract_acceptance(match.group(3)),
            "files": _extract_files(match.group(3)),
        }
    return sub_features


def _parse_single_feature(feature_id: str, feature_content: str) -> Feature:
    """Parse a single feature section into a Feature dict.

    Args:
        feature_id: The feature identifier (e.g. "5", "9b").
        feature_content: Raw markdown content after the feature heading.

    Returns:
        Feature dict with name, description, acceptance, and files.
    """
    name_match = re.search(r"^([^\n]+)", feature_content.strip())
    name = name_match.group(1).strip() if name_match else f"Feature {feature_id}"

    # Reason: Lookahead prevents capturing \n- prefix of the next list item
    desc_match = re.search(
        r"\*\*Description\*\*:\s*(.+?)(?=\n\n|\n\s*-\s*\*\*|\*\*)",
        feature_content,
        re.DOTALL,
    )
    description = desc_match.group(1).strip() if desc_match else ""

    acceptance = _extract_acceptance(feature_content)
    for req in _extract_tech_requirements(feature_content):
        if req not in acceptance:
            acceptance.append(req)

    return {
        "number": feature_id,
        "name": name,
        "description": description,
        "acceptance": acceptance,
        "files": _extract_files(feature_content),
    }


def parse_features(prd_content: str) -> dict[str, Feature]:
    """Parse all Feature sections from PRD markdown.

    Supports both numeric (Feature 5) and alphanumeric (Feature 9b) IDs.

    Args:
        prd_content: Raw PRD markdown content.

    Returns:
        Dict mapping feature ID string to Feature data.
    """
    features: dict[str, Feature] = {}
    feature_pattern = r"#### Feature (\d+[a-z]?):(.*?)(?=#### Feature |\Z)"

    for match in re.finditer(feature_pattern, prd_content, re.DOTALL):
        feature_id = match.group(1)
        feature_content = match.group(2)
        features[feature_id] = _parse_single_feature(feature_id, feature_content)

        if re.search(r"##### \d+[a-z]?\.\d+", feature_content):
            sub_features = parse_subfeatures(feature_content)
            if sub_features:
                features[feature_id]["sub_features"] = sub_features  # type: ignore[typeddict-unknown-key]

    return features


def _parse_depends(depends_str: str | None) -> list[str]:
    """Parse dependency references from a depends string.

    Args:
        depends_str: Raw depends string like "STORY-001, STORY-002" or None.

    Returns:
        List of dependency story IDs.
    """
    if not depends_str:
        return []
    return [m.group(0) for m in re.finditer(r"STORY-\d+[a-z]?", depends_str)]


def _parse_feature_stories(feature_id: str, label: str, stories_text: str) -> list[StorySpec]:
    """Parse story specs from a single feature's breakdown text.

    Args:
        feature_id: Feature ID this breakdown line belongs to.
        label: Parenthetical label (e.g. "Judge Settings") or empty string.
        stories_text: Raw text after the arrow containing STORY-XXX entries.

    Returns:
        List of StorySpec dicts.
    """
    specs: list[StorySpec] = []
    story_pattern = (
        r"STORY-(\d+[a-z]?):\s*(.+?)"
        r"(?:\s*\(depends:\s*([^)]+)\))?"
        r"(?=\s*,\s*STORY-|\n|\Z)"
    )
    for story_match in re.finditer(story_pattern, stories_text):
        specs.append(
            {
                "id": f"STORY-{story_match.group(1)}",
                "title": story_match.group(2).strip(),
                "feature_id": feature_id,
                "label": label,
                "depends_on": _parse_depends(story_match.group(3)),
            }
        )
    return specs


def parse_story_breakdown(prd_content: str) -> list[StorySpec]:
    """Parse story breakdown from the "Notes for Ralph Loop" section.

    Extracts feature-to-story mappings including parenthetical labels
    (e.g. "Judge Settings") for sub-feature matching and dependency info.

    Args:
        prd_content: Raw PRD markdown content.

    Returns:
        List of StorySpec dicts.
    """
    breakdown_matches = list(
        re.finditer(
            r"Story Breakdown[^\n]*\((\d+) stories[^\n]*?\):?\s*\n(.*?)(?=###|##|\Z)",
            prd_content,
            re.DOTALL,
        )
    )
    if not breakdown_matches:
        print("Warning: Could not find 'Story Breakdown' section")
        return []

    print(f"Found {len(breakdown_matches)} Story Breakdown section(s)")

    all_specs: list[StorySpec] = []
    # Reason: Dotted IDs like "11.1", "12.2" require (?:\.\d+)? extension
    feature_pattern = (
        r"\*\*Feature (\d+[a-z]?(?:\.\d+)?)"
        r"(?:\s*\(([^)]+)\))?"
        r"\*\*\s*"
        r"[^\S\n]*\u2192\s*"
        r"(.+?)(?=\n\s*-\s*\*\*|\Z)"
    )

    for breakdown_match in breakdown_matches:
        for match in re.finditer(feature_pattern, breakdown_match.group(2), re.DOTALL):
            label = match.group(2).strip() if match.group(2) else ""
            all_specs.extend(_parse_feature_stories(match.group(1), label, match.group(3).strip()))

    return all_specs


def _match_label_to_subfeature(
    label: str, sub_features: dict[str, SubFeature]
) -> SubFeature | None:
    """Match a breakdown label to a sub-feature by name substring.

    Args:
        label: Parenthetical label from the breakdown (e.g. "Judge Settings").
        sub_features: Dict of sub-feature name -> SubFeature data.

    Returns:
        Matched SubFeature, or None.
    """
    if not label:
        return None
    label_lower = label.lower()
    label_words = set(label_lower.split())
    for sub_name, sub_data in sub_features.items():
        sub_lower = sub_name.lower()
        # Reason: Labels are abbreviated forms of sub-feature names;
        # check both contiguous substring and word-level containment
        if label_lower in sub_lower or sub_lower in label_lower:
            return sub_data
        if label_words and label_words <= set(sub_lower.split()):
            return sub_data
    return None


def _merge_subfeature_data(
    feature: Feature, sub_features: dict[str, SubFeature]
) -> tuple[list[str], list[str]]:
    """Merge feature-level and all sub-feature acceptance/files.

    Args:
        feature: Parent feature data.
        sub_features: Dict of sub-feature name -> SubFeature data.

    Returns:
        Tuple of (merged_acceptance, merged_files).
    """
    acceptance = list(feature["acceptance"])
    files = list(feature["files"])
    for sf_data in sub_features.values():
        for ac in sf_data["acceptance"]:
            if ac not in acceptance:
                acceptance.append(ac)
        for fp in sf_data["files"]:
            if fp not in files:
                files.append(fp)
    return acceptance, files


def _resolve_acceptance_and_files(
    spec: StorySpec,
    feature: Feature,
    specs: list[StorySpec],
) -> tuple[list[str], list[str]]:
    """Resolve acceptance criteria and files for a single story.

    Args:
        spec: The story spec being resolved.
        feature: The parent feature.
        specs: All story specs (to count siblings for merge logic).

    Returns:
        Tuple of (acceptance, files).
    """
    sub_features: dict[str, SubFeature] | None = feature.get("sub_features")  # type: ignore[typeddict-item]

    if sub_features:
        same_feature_count = sum(1 for s in specs if s["feature_id"] == spec["feature_id"])
        # Reason: Single story covering a multi-sub-feature parent must merge all;
        # label matching only makes sense when multiple stories split sub-features
        if same_feature_count == 1:
            return _merge_subfeature_data(feature, sub_features)
        if spec["label"]:
            matched = _match_label_to_subfeature(spec["label"], sub_features)
            if matched:
                return matched["acceptance"], matched["files"]

    # Fallback to feature-level data
    return feature["acceptance"], feature["files"]


def resolve_stories(specs: list[StorySpec], features: dict[str, Feature]) -> list[Story]:
    """Resolve story specs into complete Story objects using feature data.

    Args:
        specs: Story specs from parse_story_breakdown().
        features: Parsed features dict from parse_features().

    Returns:
        List of fully resolved Story objects.
    """
    stories: list[Story] = []

    for spec in specs:
        feature = features.get(spec["feature_id"])
        # Reason: Dotted IDs like "11.1" reference sub-features under parent "11"
        sub_number: str | None = None
        if not feature and "." in spec["feature_id"]:
            parent_id, _ = spec["feature_id"].split(".", 1)
            feature = features.get(parent_id)
            sub_number = spec["feature_id"]
        if not feature:
            print(f"Warning: Feature {spec['feature_id']} not found for {spec['id']}")
            continue

        # Reason: When breakdown uses dotted ID, match the specific sub-feature
        # by number instead of relying on label-based fuzzy matching
        if sub_number:
            sub_features: dict[str, SubFeature] | None = feature.get("sub_features")  # type: ignore[typeddict-item]
            if sub_features:
                for _, sf_data in sub_features.items():
                    if sf_data["number"] == sub_number:
                        acceptance, files = sf_data["acceptance"], sf_data["files"]
                        break
                else:
                    acceptance, files = _resolve_acceptance_and_files(spec, feature, specs)
            else:
                acceptance, files = _resolve_acceptance_and_files(spec, feature, specs)
        else:
            acceptance, files = _resolve_acceptance_and_files(spec, feature, specs)
        description = feature["description"]

        stories.append(
            {
                "id": spec["id"],
                "title": spec["title"],
                "description": description,
                "acceptance": acceptance,
                "files": files,
                "status": "pending",
                "wave": 0,
                "completed_at": None,
                "content_hash": compute_hash(spec["title"], description, acceptance),
                "depends_on": spec["depends_on"],
            }
        )

    return stories


def _backfill_existing_stories(existing_stories: list[Story]) -> tuple[int, int]:
    """Backfill missing fields and migrate legacy schema on existing stories.

    Handles migration from legacy ``passes: bool`` to ``status: str`` enum,
    and adds ``wave: int`` field when missing.

    Args:
        existing_stories: List of existing story dicts (mutated in place).

    Returns:
        Tuple of (passed_count, updated_count).
    """
    passed_count = 0
    updated_count = 0
    for story in existing_stories:
        modified = False

        # Reason: Migrate legacy `passes: bool` → `status: str`
        if "passes" in story and "status" not in story:
            story["status"] = "passed" if story["passes"] else "pending"  # type: ignore[typeddict-item]
            del story["passes"]  # type: ignore[typeddict-item]
            modified = True

        if "wave" not in story:
            story["wave"] = 0
            modified = True

        if story.get("status") == "passed":
            passed_count += 1
            if modified:
                updated_count += 1
            continue

        if "content_hash" not in story:
            story["content_hash"] = compute_hash(
                story["title"], story["description"], story["acceptance"]
            )
            modified = True
        if "depends_on" not in story:
            story["depends_on"] = []
            modified = True
        if "status" not in story:
            story["status"] = "pending"
            modified = True
        if modified:
            updated_count += 1
    return passed_count, updated_count


def compute_waves(stories: list[Story]) -> None:
    """Assign BFS wave numbers to stories based on dependency graph.

    Wave 1 = stories with no dependencies (or all deps already passed).
    Wave N+1 = stories whose deps are all in waves 1..N.
    Mutates stories in place.

    Args:
        stories: List of Story dicts (mutated in place to set ``wave``).
    """
    story_map = {s["id"]: s for s in stories}
    placed: set[str] = set()
    wave_num = 0

    # Reason: Stories already passed are pre-placed (wave 0 = already done)
    for s in stories:
        if s["status"] == "passed":
            placed.add(s["id"])
            s["wave"] = 0

    remaining: list[Story] = [s for s in stories if s["status"] != "passed"]

    while remaining:
        wave_num += 1
        frontier: list[Story] = [
            s for s in remaining if all(d in placed or d not in story_map for d in s["depends_on"])
        ]
        if not frontier:
            # Circular dependency or unresolvable — assign wave 0
            for s in remaining:
                s["wave"] = 0
            break
        for s in frontier:
            s["wave"] = wave_num
            placed.add(s["id"])
        remaining = [s for s in remaining if s["id"] not in placed]


def _parse_args(argv: list[str]) -> tuple[Path, bool]:
    """Parse CLI arguments for PRD path and dry-run flag.

    Args:
        argv: Command-line arguments (sys.argv).

    Returns:
        Tuple of (prd_path, dry_run).
    """
    project_root = Path(__file__).parent.parent.parent
    dry_run = "--dry-run" in argv
    # Reason: Filter out flags before resolving positional PRD path arg
    positional = [a for a in argv[1:] if not a.startswith("--")]
    if positional:
        prd_path = project_root / positional[0]
    else:
        prd_path = project_root / "docs" / "PRD.md"
        if not prd_path.exists():
            sprint_prds = sorted((project_root / "docs").glob("PRD-Sprint*.md"), reverse=True)
            if sprint_prds:
                prd_path = sprint_prds[0]
    return prd_path, dry_run


def _print_dry_run_waves(stories: list[Story]) -> None:
    """Print per-wave story summary for dry-run validation."""
    wave_groups: dict[int, list[Story]] = {}
    for story in stories:
        wave_groups.setdefault(story["wave"], []).append(story)
    for wn in sorted(wave_groups):
        label = f"Wave {wn}" if wn > 0 else "Pre-completed"
        print(f"  {label}:")
        for story in wave_groups[wn]:
            ac_count = len(story["acceptance"])
            files_count = len(story["files"])
            sid, stitle = story["id"], story["title"][:60]
            print(f"    {sid}: {stitle} (AC: {ac_count}, files: {files_count})")


def _merge_and_write_stories(
    output_path: Path,
    new_parsed_stories: list[Story],
    project_name: str,
    description: str,
    source_name: str,
) -> list[Story]:
    """Load existing prd.json, merge with new stories, and write output.

    Args:
        output_path: Path to write prd.json.
        new_parsed_stories: Freshly parsed stories from PRD markdown.
        project_name: Project name from frontmatter.
        description: Project description from frontmatter.
        source_name: Source PRD filename.

    Returns:
        Merged and sorted story list.
    """
    existing_stories: list[Story] = []
    if output_path.exists():
        with open(output_path) as f:
            existing_data: dict[str, list[Story]] = json.load(f)
            existing_stories = existing_data.get("stories", [])
            print(f"Loaded {len(existing_stories)} existing stories from prd.json")

    passed_count, updated_count = _backfill_existing_stories(existing_stories)
    if passed_count > 0:
        print(f"Protected {passed_count} passed stories from modification")
    if updated_count > 0:
        print(f"Updated {updated_count} incomplete stories with missing fields")

    existing_ids = {s["id"] for s in existing_stories}
    new_stories = [s for s in new_parsed_stories if s["id"] not in existing_ids]
    print(
        f"Filtered to {len(new_stories)} new stories "
        f"(skipped {len(new_parsed_stories) - len(new_stories)} duplicates)"
    )

    all_stories: list[Story] = existing_stories + new_stories
    all_stories.sort(key=lambda s: story_sort_key(s["id"]))
    compute_waves(all_stories)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(
            {
                "project": project_name,
                "description": description,
                "source": source_name,
                "generated": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                "stories": all_stories,
            },
            f,
            indent=2,
        )
    return all_stories


def _print_wave_summary(all_stories: list[Story]) -> None:
    """Print per-wave grouping for visibility into execution plan."""
    completed = sum(1 for s in all_stories if s.get("status") == "passed")
    print(
        f"Total stories: {len(all_stories)} ({completed} completed, "
        f"{len(all_stories) - completed} pending)"
    )

    waves: dict[int, list[str]] = {}
    for s in all_stories:
        waves.setdefault(s["wave"], []).append(s["id"])
    for wave_num in sorted(waves):
        if wave_num == 0:
            ids = [
                sid
                for sid in waves[0]
                if any(st["id"] == sid and st.get("status") == "passed" for st in all_stories)
            ]
            if ids:
                print(f"  Completed: {', '.join(ids)}")
        else:
            print(f"  Wave {wave_num}: {', '.join(waves[wave_num])}")


def main() -> int:
    """Parse PRD markdown and generate ralph/docs/prd.json.

    Supports ``--dry-run`` flag for parse-only validation (no file write).

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    import sys

    prd_path, dry_run = _parse_args(sys.argv)
    project_root = Path(__file__).parent.parent.parent
    output_path = project_root / "ralph" / "docs" / "prd.json"

    if dry_run:
        print("DRY RUN — parse only, no file write")

    if not prd_path.exists():
        print(f"ERROR: PRD file not found at {prd_path}")
        return 1

    print(f"Reading {prd_path.name}...")
    with open(prd_path) as f:
        prd_content = f.read()

    frontmatter = parse_frontmatter(prd_content)
    project_name = extract_project_name(frontmatter)
    description = frontmatter.get("description", "")
    print(f"Project: {project_name}")

    print("Parsing features...")
    features = parse_features(prd_content)
    print(f"Found {len(features)} features: {sorted(features.keys())}")

    print("Parsing story breakdown...")
    specs = parse_story_breakdown(prd_content)
    print(f"Found {len(specs)} story specs")

    # Reason: Cross-check declared story count against parsed count
    declared_match = re.search(r"Story Breakdown[^\n]*\((\d+) stories", prd_content)
    if declared_match:
        declared = int(declared_match.group(1))
        if declared != len(specs):
            print(f"WARNING: PRD declares {declared} stories but parser found {len(specs)}")

    print("Resolving stories...")
    new_parsed_stories = resolve_stories(specs, features)
    print(f"Resolved {len(new_parsed_stories)} stories")

    compute_waves(new_parsed_stories)

    if dry_run:
        _print_dry_run_waves(new_parsed_stories)
        return 0

    all_stories = _merge_and_write_stories(
        output_path,
        new_parsed_stories,
        project_name,
        description,
        prd_path.name,
    )

    print(f"\nGenerated {output_path}")
    _print_wave_summary(all_stories)

    # Reason: Show per-wave grouping for visibility into execution plan
    waves: dict[int, list[str]] = {}
    for s in all_stories:
        waves.setdefault(s["wave"], []).append(s["id"])
    for wave_num in sorted(waves):
        if wave_num == 0:
            ids = [
                sid
                for sid in waves[0]
                if any(st["id"] == sid and st.get("status") == "passed" for st in all_stories)
            ]
            if ids:
                print(f"  Completed: {', '.join(ids)}")
        else:
            print(f"  Wave {wave_num}: {', '.join(waves[wave_num])}")

    return 0


if __name__ == "__main__":
    exit(main())
