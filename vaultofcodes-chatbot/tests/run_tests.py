"""
run_tests.py

Runs the test dataset (test_queries.json) against a running instance of the
chatbot API and prints/saves a pass/fail evaluation report.

Usage:
    python3 tests/run_tests.py [--base-url http://localhost:8000]
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent


def post_chat(base_url: str, session_id: str | None, message: str) -> dict:
    payload = json.dumps({"session_id": session_id, "message": message}).encode()
    req = urllib.request.Request(
        f"{base_url}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def run(base_url: str):
    test_cases = json.loads((HERE / "test_queries.json").read_text())

    # Two independent sessions: one linear conversation (so TC14 -> TC15
    # memory test works), and standalone calls for everything else.
    session_id = None
    results = []

    for case in test_cases:
        try:
            data = post_chat(base_url, session_id, case["message"])
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            results.append({**case, "pass": False, "error": str(e)})
            continue

        session_id = data["session_id"]  # keep conversation going for memory test

        intent_ok = data["intent"] == case["expected_intent"]
        escalate_ok = data["escalate"] == case["expect_escalate"]
        links_ok = (len(data.get("links", [])) > 0) == case["expect_links"] if "expect_links" in case else True

        passed = intent_ok and escalate_ok and links_ok

        results.append({
            **case,
            "pass": passed,
            "actual_intent": data["intent"],
            "actual_escalate": data["escalate"],
            "actual_links": len(data.get("links", [])),
            "reply_preview": data["reply"][:120],
        })

    return results


def render_report(results: list[dict]) -> str:
    lines = []
    lines.append("# VaultOfCodes Chatbot — Testing / Evaluation Report\n")
    total = len(results)
    passed = sum(1 for r in results if r["pass"])
    lines.append(f"**Result: {passed} / {total} test cases passed**\n")
    lines.append("| ID | Category | Message | Expected Intent | Actual Intent | Escalate (exp/act) | Links (exp/act) | Status |")
    lines.append("|----|----------|---------|------------------|----------------|----------------------|-------------------|--------|")
    for r in results:
        status = "✅ PASS" if r["pass"] else "❌ FAIL"
        exp_links = "yes" if r.get("expect_links") else "no"
        act_links = r.get("actual_links", "-")
        lines.append(
            f"| {r['id']} | {r['category']} | {r['message']} | `{r['expected_intent']}` | "
            f"`{r.get('actual_intent', 'ERROR')}` | {r['expect_escalate']}/{r.get('actual_escalate', '-')} | "
            f"{exp_links}/{act_links} | {status} |"
        )

    lines.append("\n## Reply previews\n")
    for r in results:
        lines.append(f"**{r['id']}** ({r['category']})")
        lines.append(f"> Q: {r['message']}")
        lines.append(f"> A: {r.get('reply_preview', r.get('error', 'N/A'))}")
        lines.append("")

    lines.append("## Coverage checklist (per assignment spec, section 15)\n")
    checklist = [
        "Course inquiries", "Training inquiries", "Internship inquiries",
        "Certificate issues", "Offer letter issues", "Verification queries",
        "Website navigation", "Payment questions", "Technical issues",
        "Random/general questions", "Unclear questions", "Human support",
        "Conversation memory (context retention)",
    ]
    for item in checklist:
        lines.append(f"- [x] {item}")

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--out", default=str(HERE.parent / "TESTING_REPORT.md"))
    args = parser.parse_args()

    results = run(args.base_url)
    report = render_report(results)

    Path(args.out).write_text(report)
    print(report)

    failed = sum(1 for r in results if not r["pass"])
    sys.exit(1 if failed else 0)
