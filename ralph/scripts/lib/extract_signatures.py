#!/usr/bin/env python3
"""Extract Python class and function signatures using the ast module.

Invoked per-file by snapshot.sh to replace grep-based signature extraction.
Outputs line-number-prefixed signatures matching the format consumed by sed
in snapshot.sh (e.g. "17:class AgentFactory:").

Includes decorators and preserves original source formatting. Falls back to
grep-style extraction if the file has syntax errors.

Usage:
    python3 extract_signatures.py <filepath>
"""

import ast
import re
import sys


def _read_source_lines(filepath: str) -> list[str]:
    """Read source file lines for original formatting preservation.

    Args:
        filepath: Path to the Python source file.

    Returns:
        List of source lines (1-indexed access requires offset).
    """
    with open(filepath, encoding="utf-8", errors="replace") as f:
        return f.readlines()


def extract_with_ast(filepath: str, source_lines: list[str]) -> list[str]:
    """Extract signatures using ast.parse and source line lookup.

    Args:
        filepath: Path to the Python source file.
        source_lines: Pre-read source lines for formatting preservation.

    Returns:
        List of formatted signature strings (lineno:source_line).
    """
    with open(filepath, encoding="utf-8", errors="replace") as f:
        tree = ast.parse(f.read(), filename=filepath)

    results: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        # Emit decorator lines
        for decorator in node.decorator_list:
            deco_line = decorator.lineno
            results.append(f"{deco_line}:{source_lines[deco_line - 1].rstrip()}")

        # Emit the def/class line with original formatting
        lineno = node.lineno
        line = source_lines[lineno - 1].rstrip()

        # Reason: Multi-line signatures may truncate the return type on the
        # first line; append it if present in the AST but missing from source
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns:
            if "->" not in line:
                return_annotation = ast.unparse(node.returns)
                line = f"{line} -> {return_annotation}"

        results.append(f"{lineno}:{line}")

    # Sort by line number for stable output
    results.sort(key=lambda s: int(s.split(":", 1)[0]))
    return results


def extract_with_grep(filepath: str, source_lines: list[str]) -> list[str]:
    """Fallback extraction using regex when ast.parse fails.

    Args:
        filepath: Path to the Python source file.
        source_lines: Pre-read source lines.

    Returns:
        List of formatted signature strings (lineno:source_line).
    """
    pattern = re.compile(r"^(class |def |    def |async def )")
    results: list[str] = []
    for i, line in enumerate(source_lines, start=1):
        if pattern.match(line):
            results.append(f"{i}:{line.rstrip()}")
    return results


def main() -> int:
    """Extract signatures from a Python file and print to stdout.

    Returns:
        Exit code (0 for success, 1 for usage error).
    """
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <filepath>", file=sys.stderr)
        return 1

    filepath = sys.argv[1]
    source_lines = _read_source_lines(filepath)

    try:
        results = extract_with_ast(filepath, source_lines)
    except SyntaxError:
        results = extract_with_grep(filepath, source_lines)

    for line in results:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
