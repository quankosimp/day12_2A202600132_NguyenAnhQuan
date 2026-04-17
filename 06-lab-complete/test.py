from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from langchain_core.messages import AIMessage, ToolMessage

from agent import run_agent

BASE_DIR = Path(__file__).resolve().parent
USERCASES_PATH = BASE_DIR / "usercases.md"
RESULTS_PATH = BASE_DIR / "test_results.md"
CASE_TIMEOUT_SECONDS = 45


@dataclass
class TestCase:
    title: str
    prompt: str
    expected: str


def parse_usercases(markdown_text: str) -> list[TestCase]:
    pattern = re.compile(
        r"##\s+(?P<title>.+?)\n\n"
        r"\*\*User:\*\*\s*\n"
        r'"(?P<prompt>.+?)"\n\n'
        r"\*\*Kỳ vọng:\*\*\s*\n"
        r"(?P<expected>.*?)(?=\n---\n|\Z)",
        re.DOTALL,
    )
    matches = pattern.finditer(markdown_text)

    cases = []
    for match in matches:
        title = match.group("title").strip()
        prompt = match.group("prompt").strip()
        expected = match.group("expected").strip()
        cases.append(TestCase(title=title, prompt=prompt, expected=expected))

    if not cases:
        raise ValueError("Không parse được test case nào từ usercases.md.")

    return cases


def extract_trace(messages: list) -> tuple[list[dict], list[dict], str]:
    tool_calls = []
    tool_outputs = []

    for message in messages:
        if isinstance(message, AIMessage) and getattr(message, "tool_calls", None):
            for call in message.tool_calls:
                tool_calls.append(
                    {
                        "name": call.get("name", "unknown"),
                        "args": call.get("args", {}),
                    }
                )
        elif isinstance(message, ToolMessage):
            tool_outputs.append(
                {
                    "name": getattr(message, "name", "tool"),
                    "content": str(message.content).strip(),
                }
            )

    final_answer = str(messages[-1].content).strip() if messages else ""
    return tool_calls, tool_outputs, final_answer


def format_tool_calls(tool_calls: list[dict]) -> str:
    if not tool_calls:
        return "- Không có tool call"

    lines = []
    for call in tool_calls:
        lines.append(f"- `{call['name']}` với args: `{call['args']}`")
    return "\n".join(lines)


def format_tool_outputs(tool_outputs: list[dict]) -> str:
    if not tool_outputs:
        return "- Không có tool output"

    blocks = []
    for output in tool_outputs:
        blocks.append(
            "\n".join(
                [
                    f"- `{output['name']}`",
                    "```text",
                    output["content"] or "(rỗng)",
                    "```",
                ]
            )
        )
    return "\n".join(blocks)


def build_results_markdown(results: list[dict]) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sections = [
        "# Test Results - TravelBuddy Agent",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Total cases: `{len(results)}`",
        "",
    ]

    for index, result in enumerate(results, start=1):
        sections.extend(
            [
                f"## Test {index} - {result['title']}",
                "",
                f"- Trace ID: `{result['trace_id']}`",
                "",
                "**Prompt:**",
                "",
                f"> {result['prompt']}",
                "",
                "**Kỳ vọng:**",
                "",
                result["expected"],
                "",
                "**Tool calls:**",
                "",
                result["tool_calls_md"],
                "",
                "**Tool outputs:**",
                "",
                result["tool_outputs_md"],
                "",
                "**Agent response:**",
                "",
                "```text",
                result["response"] or "(rỗng)",
                "```",
                "",
            ]
        )
        if result.get("error"):
            sections.extend(
                [
                    "**Error:**",
                    "",
                    "```text",
                    result["error"],
                    "```",
                    "",
                ]
            )

    return "\n".join(sections).rstrip() + "\n"


def run_tests() -> list[dict]:
    markdown_text = USERCASES_PATH.read_text(encoding="utf-8")
    cases = parse_usercases(markdown_text)
    results = []

    for case in cases:
        print(f"Running: {case.title}")
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_agent, case.prompt)
                result = future.result(timeout=CASE_TIMEOUT_SECONDS)
            tool_calls, tool_outputs, final_answer = extract_trace(result["messages"])
            results.append(
                {
                    "title": case.title,
                    "trace_id": result.get("trace_id", "-"),
                    "prompt": case.prompt,
                    "expected": case.expected,
                    "tool_calls_md": format_tool_calls(tool_calls),
                    "tool_outputs_md": format_tool_outputs(tool_outputs),
                    "response": final_answer,
                    "error": "",
                }
            )
        except FutureTimeoutError:
            results.append(
                {
                    "title": case.title,
                    "trace_id": "-",
                    "prompt": case.prompt,
                    "expected": case.expected,
                    "tool_calls_md": "- Không có tool call",
                    "tool_outputs_md": "- Không có tool output",
                    "response": "",
                    "error": f"Timeout sau {CASE_TIMEOUT_SECONDS} giây.",
                }
            )
        except Exception as exc:
            results.append(
                {
                    "title": case.title,
                    "trace_id": "-",
                    "prompt": case.prompt,
                    "expected": case.expected,
                    "tool_calls_md": "- Không có tool call",
                    "tool_outputs_md": "- Không có tool output",
                    "response": "",
                    "error": str(exc),
                }
            )

    return results


def main() -> None:
    results = run_tests()
    RESULTS_PATH.write_text(build_results_markdown(results), encoding="utf-8")
    print(f"Đã lưu kết quả vào: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
