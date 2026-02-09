#!/usr/bin/env python3
"""
Generate ralph/docs/prd.json from docs/PRD.md or docs/GreenAgent-PRD.md

Generalized parser that extracts features and story breakdown mapping from PRD.md.
Supports incremental updates with content hashing.

CRITICAL SAFETY RULES:
1. NEVER modify stories marked as passed (passes: true)
2. Only append new stories that don't already exist
3. Only update incomplete stories (passes: false) if fields are missing
4. Preserve all existing story metadata (completed_at, content_hash, etc.)
"""

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict


class Story(TypedDict):
    id: str
    title: str
    description: str
    acceptance: list[str]
    files: list[str]
    passes: bool
    completed_at: str | None
    content_hash: str
    depends_on: list[str]  # Story IDs that must complete first


class Feature(TypedDict):
    number: int
    name: str
    description: str
    acceptance: list[str]
    files: list[str]


def compute_hash(title: str, description: str, acceptance: list[str]) -> str:
    """Compute SHA-256 hash of story content for change detection"""
    content = f"{title}|{description}|{json.dumps(acceptance, sort_keys=True)}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def parse_features(prd_content: str) -> dict[int, Feature]:
    """Parse all Feature sections from PRD.md"""
    features = {}

    # Split by feature headings (capture everything until next #### or end)
    feature_pattern = r"#### Feature (\d+):(.*?)(?=#### Feature |\Z)"

    for match in re.finditer(feature_pattern, prd_content, re.DOTALL):
        feature_num = int(match.group(1))
        feature_content = match.group(2)

        # Extract name (first line after "Feature N:")
        name_match = re.search(r"^([^\n]+)", feature_content.strip())
        name = name_match.group(1).strip() if name_match else f"Feature {feature_num}"

        # Extract description
        desc_match = re.search(
            r"\*\*Description\*\*:\s*(.+?)(?:\n\n|\*\*)", feature_content, re.DOTALL
        )
        description = desc_match.group(1).strip() if desc_match else ""

        # Extract acceptance criteria
        acceptance = []
        acceptance_match = re.search(
            r"\*\*Acceptance Criteria\*\*:\s*\n((?:- \[[x ]\][^\n]+\n)+)",
            feature_content,
            re.DOTALL,
        )
        if acceptance_match:
            for line in acceptance_match.group(1).split("\n"):
                if line.strip().startswith("- ["):
                    criterion = re.sub(r"^- \[[x ]\]\s*", "", line.strip())
                    if criterion:
                        acceptance.append(criterion)

        # Also extract Technical Requirements and merge into acceptance criteria
        tech_req_match = re.search(
            r"\*\*Technical Requirements\*\*:\s*\n((?:- [^\n]+\n)+)", feature_content, re.DOTALL
        )
        if tech_req_match:
            for line in tech_req_match.group(1).split("\n"):
                if line.strip().startswith("- "):
                    requirement = line.strip()[2:].strip()  # Remove "- " prefix
                    if requirement and requirement not in acceptance:
                        acceptance.append(requirement)

        # Extract files
        files = []
        files_match = re.search(
            r"\*\*Files(?:\s+Implemented)?\*\*:\s*\n((?:- `[^`]+`\n?)+)", feature_content, re.DOTALL
        )
        if files_match:
            for line in files_match.group(1).split("\n"):
                file_match = re.search(r"`([^`]+)`", line)
                if file_match:
                    # Remove comments after " - "
                    file_path = file_match.group(1).split(" - ")[0].strip()
                    files.append(file_path)

        features[feature_num] = {
            "number": feature_num,
            "name": name,
            "description": description,
            "acceptance": acceptance,
            "files": files,
        }

        # Parse sub-features for features with ##### headings (dynamic detection)
        if re.search(r'##### \d+\.\d+', feature_content):
            sub_features = parse_subfeatures(feature_content)
            if sub_features:
                features[feature_num]["sub_features"] = sub_features

    return features


def parse_subfeatures(feature_content: str) -> dict[str, dict]:
    """
    Parse sub-features from feature content (e.g., 5.1, 5.2, 10.1, 10.2).

    Returns dict mapping sub-feature name → {number, acceptance, files}
    """
    sub_features = {}

    # Pattern for ##### N.N Sub-feature Name
    sub_feature_pattern = r"##### (\d+\.\d+) ([^\n]+)\s*\n(.*?)(?=\n#####|\Z)"

    for match in re.finditer(sub_feature_pattern, feature_content, re.DOTALL):
        sub_num = match.group(1)
        sub_name = match.group(2).strip()
        sub_content = match.group(3)

        # Extract acceptance criteria
        acceptance = []
        acceptance_match = re.search(
            r"\*\*Acceptance Criteria\*\*:\s*\n((?:- \[[x ]\][^\n]+\n)+)", sub_content, re.DOTALL
        )
        if acceptance_match:
            for line in acceptance_match.group(1).split("\n"):
                if line.strip().startswith("- ["):
                    criterion = re.sub(r"^- \[[x ]\]\s*", "", line.strip())
                    if criterion:
                        acceptance.append(criterion)

        # Extract files
        files = []
        files_match = re.search(r"\*\*Files\*\*:\s*\n((?:- `[^`]+`[^\n]*\n)+)", sub_content)
        if files_match:
            for line in files_match.group(1).split("\n"):
                file_match = re.search(r"`([^`]+)`", line)
                if file_match:
                    file_path = file_match.group(1).split(" - ")[0].strip()
                    # Remove suffixes like "(extend)", "(verify/extend)", "(CREATE)"
                    file_path = re.sub(r"\s*\([^)]+\)\s*$", "", file_path)
                    files.append(file_path)

        sub_features[sub_name] = {"number": sub_num, "acceptance": acceptance, "files": files}

    return sub_features


# Keyword mappings for matching story titles to sub-features
SUBFEATURE_KEYWORDS: dict[int, list[tuple[list[str], str]]] = {
    # Feature 5: (story_keywords, sub_feature_keyword)
    5: [
        (["trivial"], "trivial"),
        (["statistical"], "statistical"),
        (["held-out", "test set"], "contamination"),
        (["limitations"], "flaw"),
    ],
    # Feature 10: (story_keywords, sub_feature_keyword)
    10: [
        (["a2a", "task"], "a2a"),
        (["docker", "parameter"], "docker"),
        (["task isolation"], "isolation"),
    ],
}


def match_story_to_subfeature(
    story_title: str, sub_features: dict[str, dict], feature_num: int
) -> dict | None:
    """Match a story title to its corresponding sub-feature using keyword mapping."""
    if feature_num not in SUBFEATURE_KEYWORDS:
        return None

    title_lower = story_title.lower()

    for sub_name, sub_data in sub_features.items():
        sub_name_lower = sub_name.lower()

        for story_keywords, sub_keyword in SUBFEATURE_KEYWORDS[feature_num]:
            # Check if all story keywords match title AND sub_keyword matches sub_name
            if all(kw in title_lower for kw in story_keywords) and sub_keyword in sub_name_lower:
                return sub_data

    return None


def parse_story_breakdown(prd_content: str) -> dict[int, list[dict]]:
    """
    Parse story breakdown mapping from PRD.md "Notes for Ralph Loop" section.

    Returns mapping of feature_num → list of story specs:
    {
        3: [
            {'id': 'STORY-022', 'title': '...', 'acceptance_filter': [...], 'files': [...]},
            ...
        ]
    }
    """
    # Find ALL "Story Breakdown" sections (Phase 1, Phase 2, etc.)
    # Updated regex to handle "stories total)" or "stories)" patterns
    # Made colon optional since PRD.md may not have it
    breakdown_matches = list(
        re.finditer(
            r"Story Breakdown[^\n]*\((\d+) stories[^\n]*?\):?\s*\n(.*?)(?=###|##|\Z)",
            prd_content,
            re.DOTALL,
        )
    )

    if not breakdown_matches:
        print("Warning: Could not find 'Story Breakdown' section")
        return {}

    print(f"Found {len(breakdown_matches)} Story Breakdown section(s)")

    # Parse each breakdown section and merge mappings
    mapping = {}

    for breakdown_match in breakdown_matches:
        breakdown_text = breakdown_match.group(2)

        # Parse each feature mapping: "- **Feature N (...) → STORY-X, STORY-Y, ..."
        # Pattern: Feature N (Name) → STORY-XXX: Description, STORY-YYY: Description
        feature_pattern = r"\*\*Feature (\d+)[^→]+→\s*(.+?)(?=\n\s*-\s*\*\*|\Z)"

        for match in re.finditer(feature_pattern, breakdown_text, re.DOTALL):
            feature_num = int(match.group(1))
            stories_text = match.group(2).strip()

            # Parse individual stories: STORY-XXX: Title (depends: STORY-YYY, STORY-ZZZ)
            # Pattern captures: story_num, title, optional depends clause
            # Updated to handle titles with parentheses (only stop at "(depends:" not just "(")
            story_pattern = (
                r"STORY-(\d+):\s*(.+?)(?:\s*\(depends:\s*([^)]+)\))?(?=\s*,\s*STORY-|\n|\Z)"
            )

            story_specs = []
            for story_match in re.finditer(story_pattern, stories_text):
                story_num = story_match.group(1)
                story_title = story_match.group(2).strip()
                depends_str = story_match.group(3)

                # Parse depends_on list
                depends_on = []
                if depends_str:
                    # Extract STORY-XXX patterns from depends string
                    for dep_match in re.finditer(r"STORY-\d+", depends_str):
                        depends_on.append(dep_match.group(0))

                story_specs.append(
                    {
                        "id": f"STORY-{story_num}",
                        "title": story_title,
                        "acceptance_filter": [],  # Will filter from feature acceptance
                        "files": [],  # Will use feature files or empty
                        "depends_on": depends_on,
                    }
                )

            # Merge into mapping (later sections can override earlier ones)
            if feature_num not in mapping:
                mapping[feature_num] = []
            mapping[feature_num].extend(story_specs)

    return mapping


def apply_story_breakdown(
    features: dict[int, Feature], breakdown: dict[int, list[dict]]
) -> list[Story]:
    """
    Apply story breakdown mapping to features to generate atomic stories.

    For features without explicit breakdown, create one story per feature.
    """
    stories = []

    for feature_num in sorted(features.keys()):
        feature = features[feature_num]

        if feature_num in breakdown:
            # Use explicit breakdown
            for spec in breakdown[feature_num]:
                # Try to match story to sub-feature if available
                sub_feature = None
                if "sub_features" in feature:
                    sub_feature = match_story_to_subfeature(
                        spec["title"], feature["sub_features"], feature_num
                    )

                if sub_feature:
                    acceptance = sub_feature["acceptance"]
                    files = sub_feature["files"]
                else:
                    # Fallback to feature-level acceptance/files
                    acceptance = feature["acceptance"]
                    files = spec.get("files", []) or feature["files"]

                content_hash = compute_hash(spec["title"], feature["description"], acceptance)

                story: Story = {
                    "id": spec["id"],
                    "title": spec["title"],
                    "description": f"{feature['description']} - {spec['title']}",
                    "acceptance": acceptance,
                    "files": files,
                    "passes": False,
                    "completed_at": None,
                    "content_hash": content_hash,
                    "depends_on": spec.get("depends_on", []),
                }
                stories.append(story)
        else:
            # No explicit breakdown - create one story per feature
            # Determine story ID based on feature number (Phase 1 features)
            if feature_num <= 2:
                # Phase 1 features were already broken down manually
                continue

            story_id = f"STORY-{feature_num:03d}"
            content_hash = compute_hash(
                feature["name"], feature["description"], feature["acceptance"]
            )

            story: Story = {
                "id": story_id,
                "title": feature["name"],
                "description": feature["description"],
                "acceptance": feature["acceptance"],
                "files": feature["files"],
                "passes": False,
                "completed_at": None,
                "content_hash": content_hash,
                "depends_on": [],
            }
            stories.append(story)

    return stories


def enhance_stories_with_manual_details(stories: list[Story]) -> list[Story]:
    """
    Enhance stories with detailed titles, descriptions, and file mappings.

    This fills in details that aren't easily parsed from PRD.md structure.
    Uses knowledge of the Phase 2 implementation plan.
    """
    enhancements = {
        "STORY-022": {
            "description": (
                "Create messenger.py with A2A client utilities "
                "(create_message, send_message, Messenger class) for green agent "
                "to call purple agents via A2A protocol"
            ),
            "acceptance": [
                "messenger.py exposes create_message() function for A2A message construction",
                "messenger.py exposes send_message() function for HTTP POST to purple agents",
                "Messenger class provides high-level API for agent-to-agent communication",
                "Handles A2A protocol errors and timeouts gracefully",
                "Unit tests verify message format and sending logic",
            ],
            "files": ["src/bulletproof_green/messenger.py", "tests/test_messenger.py"],
        },
        "STORY-023": {
            "description": (
                "Create arena_executor.py with multi-turn orchestration: "
                "green agent iteratively calls purple agent, evaluates response, "
                "provides critique, until risk_score < target or max_iterations reached"
            ),
            "acceptance": [
                "Supports configurable max_iterations (default: 5)",
                "Supports configurable target_risk_score (default: 20)",
                "Returns structured ArenaResult with iteration history",
                "Each iteration includes: narrative, evaluation, critique",
                "Terminates when risk_score < target OR max_iterations reached",
                "Critique feedback derived from redline issues to guide purple agent refinement",
            ],
            "files": ["src/bulletproof_green/arena_executor.py", "tests/test_arena_executor.py"],
        },
        "STORY-024": {
            "description": (
                "Extend green agent server to handle arena mode requests "
                "via mode=arena parameter, routing to ArenaExecutor "
                "instead of single-shot evaluation"
            ),
            "files": ["src/bulletproof_green/server.py", "tests/integration/test_arena_mode.py"],
        },
        # Feature 5 - Benchmark rigor sub-features (027-030)
        "STORY-027": {
            "description": (
                "Test benchmark with trivial agents (empty response, random text) "
                "to establish baseline scores and ensure they score >80 "
                "(high risk = failing)"
            )
        },
        "STORY-028": {
            "description": (
                "Add statistical rigor: report 95% confidence intervals, "
                "run benchmark multiple times for reproducibility, "
                "calculate inter-rater reliability (Cohen's κ)"
            )
        },
        "STORY-029": {
            "description": (
                "Implement data contamination prevention: maintain held-out "
                "test set not in public ground truth, version tracking for "
                "all narratives, document data provenance"
            )
        },
        "STORY-030": {
            "description": (
                "Document known benchmark limitations, quantify impact of "
                "keyword-based evaluation gaps, provide guidance on result "
                "interpretation"
            )
        },
        # Feature 4 - Split between create (025) and integrate (026)
        "STORY-025": {
            "description": (
                "Create llm_judge.py with LLM-as-Judge implementation "
                "using GPT-4 to score narratives based on IRS criteria"
            ),
            "acceptance": [
                "llm_judge.py implements LLMJudge class with score() method",
                "Uses OpenAI API (GPT-4) for scoring",
                "Returns structured scores with reasoning",
                "Handles API errors gracefully",
                "Add openai to pyproject.toml dependencies",
            ],
            "files": [
                "src/bulletproof_green/llm_judge.py",
                "tests/test_llm_judge.py",
                "pyproject.toml",
            ],
        },
        "STORY-026": {
            "description": (
                "Integrate LLM judge with rule-based scoring to create hybrid evaluation system"
            ),
            "acceptance": [
                "Evaluator uses both rule-based and LLM scoring",
                "Scorer combines rule-based and LLM scores",
                "Weighted combination or fallback strategy implemented",
                "Integration tests verify hybrid approach",
            ],
            "files": [
                "src/bulletproof_green/evaluator.py",
                "src/bulletproof_green/scorer.py",
                "tests/test_hybrid_evaluation.py",
            ],
        },
        # Feature 6 - Add missing files
        "STORY-031": {
            "files": [
                "src/bulletproof_green/rules/business_risk_detector.py",
                "src/bulletproof_green/evaluator.py",
                "src/bulletproof_green/scorer.py",
                "tests/test_business_risk_detector.py",
            ]
        },
        # Feature 7 - Split between create (032) and integrate (033)
        "STORY-032": {
            "files": [
                "src/bulletproof_green/rules/specificity_detector.py",
                "tests/test_specificity_detector.py",
            ]
        },
        "STORY-033": {
            "description": (
                "Wire business_risk_detector and specificity_detector into evaluator pipeline"
            ),
            "acceptance": [
                "Evaluator imports and uses business_risk_detector",
                "Evaluator imports and uses specificity_detector",
                "Both detectors integrated into evaluation flow",
                "Integration tests verify detectors are called",
            ],
            "files": ["src/bulletproof_green/evaluator.py", "tests/test_evaluator_integration.py"],
        },
        # Feature 8 - Split between tag (034) and report (035)
        "STORY-034": {
            "acceptance": [
                "Add difficulty tags (EASY, MEDIUM, HARD) to ground_truth.json",
                "Tag at least 10 test cases per difficulty level",
                "Tags based on IRS complexity and edge case handling",
            ],
            "files": ["data/ground_truth.json"],
        },
        "STORY-035": {
            "description": "Extend validate_benchmark.py to report accuracy by difficulty level",
            "acceptance": [
                "Report accuracy breakdown by difficulty level (EASY, MEDIUM, HARD)",
                "Show pass/fail counts per difficulty",
                "Include difficulty distribution in output",
            ],
            "files": ["src/validate_benchmark.py", "tests/test_benchmark_validation.py"],
        },
        # Feature 9 - Split between test data (036) and LLM tests (037)
        "STORY-036": {
            "acceptance": [
                "Create adversarial_narratives.json with gaming attempts",
                "Test rule-based anti-gaming detection",
                "Include keyword stuffing, overgeneralization, irrelevance tests",
                "Verify rule-based detectors catch gaming attempts",
            ],
            "files": ["data/adversarial_narratives.json", "tests/test_anti_gaming.py"],
        },
        "STORY-037": {
            "acceptance": [
                "Test LLM reward hacking scenarios",
                "Document known LLM judge limitations",
                "Test cases for prompt injection, context manipulation",
                "Add limitations to BENCHMARK_LIMITATIONS.md",
            ],
            "files": ["tests/test_anti_gaming.py", "docs/AgentBeats/BENCHMARK_LIMITATIONS.md"],
        },
        # Feature 11 - Split between schema (041), server (042), tests (043)
        "STORY-041": {
            "acceptance": [
                "Update evaluator.py to return nested output structure",
                "Update scorer.py to return nested scores",
                "Ensure backward compatibility or migration path",
                "Schema matches Green-Agent-Metrics-Specification.md",
            ],
            "files": [
                "src/bulletproof_green/evaluator.py",
                "src/bulletproof_green/scorer.py",
                "tests/test_output_structure.py",
            ],
        },
        "STORY-042": {
            "acceptance": [
                "Wire server.py to use GreenAgentExecutor (currently hardcoded placeholder!)",
                "Remove mock response from lines 52-56",
                "Server creates executor instance on startup or per-request",
                "Task execution delegates to executor.execute()",
                "Server returns executor output as task result",
            ],
            "files": ["src/bulletproof_green/server.py"],
        },
        "STORY-043": {
            "acceptance": [
                "Update all tests for new output structure",
                "Verify test_green_agent_evaluator.py uses new schema",
                "Verify test_green_agent_executor.py uses new schema",
                "Verify test_green_agent_server.py uses new schema",
            ],
            "files": [
                "tests/test_green_agent_evaluator.py",
                "tests/test_green_agent_executor.py",
                "tests/test_green_agent_server.py",
            ],
        },
    }

    # Apply enhancements
    for story in stories:
        if story["id"] in enhancements:
            for key, value in enhancements[story["id"]].items():
                if value:  # Only override if enhancement value is not empty
                    story[key] = value

    return stories


def main():
    import sys

    # Paths (relative to project root)
    project_root = Path(__file__).parent.parent.parent

    # Check for command-line argument or use default
    if len(sys.argv) > 1:
        prd_filename = sys.argv[1]
        prd_path = project_root / prd_filename
    else:
        # Try GreenAgent-PRD.md first, then PRD.md
        prd_path = project_root / "docs" / "GreenAgent-PRD.md"
        if not prd_path.exists():
            prd_path = project_root / "docs" / "PRD.md"

    existing_prd_json_path = project_root / "ralph" / "docs" / "prd.json"
    output_path = project_root / "ralph" / "docs" / "prd.json"

    # Check PRD.md exists
    if not prd_path.exists():
        print(f"ERROR: PRD file not found at {prd_path}")
        return 1

    # Read PRD.md
    print("Reading PRD.md...")
    with open(prd_path) as f:
        prd_content = f.read()

    # Parse features
    print("Parsing features from PRD.md...")
    features = parse_features(prd_content)
    print(f"Found {len(features)} features: {sorted(features.keys())}")

    # Parse story breakdown mapping
    print("Parsing story breakdown mapping...")
    breakdown = parse_story_breakdown(prd_content)
    print(f"Found breakdown mappings for features: {sorted(breakdown.keys())}")

    # Generate Phase 2 stories from features + breakdown
    print("Generating Phase 2 stories...")
    phase2_stories = apply_story_breakdown(features, breakdown)

    # Enhance with manual details (temporary until PRD.md structure improves)
    phase2_stories = enhance_stories_with_manual_details(phase2_stories)

    print(f"Generated {len(phase2_stories)} Phase 2 stories")

    # Load existing stories
    existing_stories = []
    if existing_prd_json_path.exists():
        with open(existing_prd_json_path) as f:
            existing_data = json.load(f)
            existing_stories = existing_data.get("stories", [])
            print(f"Loaded {len(existing_stories)} existing stories from prd.json")

    # Get existing story IDs to avoid duplicates
    existing_story_ids = {s["id"] for s in existing_stories}

    # Add content_hash and depends_on to existing stories if missing
    # CRITICAL: Never modify stories marked as passed (passes: true)
    passed_count = 0
    updated_count = 0
    for story in existing_stories:
        # Skip passed stories - they are immutable
        if story.get("passes", False):
            passed_count += 1
            continue

        # Only modify incomplete stories
        modified = False
        if "content_hash" not in story:
            story["content_hash"] = compute_hash(
                story["title"], story["description"], story["acceptance"]
            )
            modified = True
        if "depends_on" not in story:
            story["depends_on"] = []
            modified = True

        if modified:
            updated_count += 1

    if passed_count > 0:
        print(f"Protected {passed_count} passed stories from modification")
    if updated_count > 0:
        print(f"Updated {updated_count} incomplete stories with missing fields")

    # Filter out new stories that already exist (avoid duplicates)
    new_stories = [s for s in phase2_stories if s["id"] not in existing_story_ids]
    skipped_count = len(phase2_stories) - len(new_stories)
    print(f"Filtered to {len(new_stories)} new stories (skipped {skipped_count} duplicates)")

    # Combine existing + new stories
    all_stories = existing_stories + new_stories

    # Sort by ID
    all_stories.sort(key=lambda s: int(s["id"].split("-")[1]))

    # Create final prd.json structure
    # Auto-detect project and description from PRD file
    prd_filename = prd_path.name
    if "GreenAgent" in prd_filename:
        project_name = "RDI-AgentBeats-GraphJudge"
        description = (
            "Graph-Based Coordination Benchmark - Green Agent (Assessor) for evaluating "
            "multi-agent coordination quality through runtime graph analysis, LLM assessment, "
            "and latency metrics."
        )
    else:
        project_name = "RDI-AgentBeats-TheBulletproofProtocol"
        description = (
            "Legal Domain Agent Benchmark for AgentBeats competition - "
            "IRS Section 41 R&D tax credit evaluator. "
            "Purple agent (reference implementation) generates test narratives, "
            "Green agent (benchmark) evaluates them for IRS compliance."
        )

    prd_data = {
        "project": project_name,
        "description": description,
        "source": prd_filename,
        "generated": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
        "stories": all_stories,
    }

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(prd_data, f, indent=2)

    print(f"\n✅ Generated {output_path}")
    print(f"Total stories: {len(all_stories)}")
    print(f"  - Existing (preserved): {len(existing_stories)} stories")
    print(f"  - New (appended): {len(new_stories)} stories")

    # Summary
    completed = sum(1 for s in all_stories if s["passes"])
    pending = len(all_stories) - completed
    print(f"\nStatus: {completed} completed, {pending} pending")

    return 0


if __name__ == "__main__":
    exit(main())
