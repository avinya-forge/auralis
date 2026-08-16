import subprocess
import os
import re
import hashlib
import json
import urllib.request


def run_command(command):
    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False
        )
        return result.stdout
    except Exception as e:
        return str(e)


def parse_flake8(output):
    issues = []
    for line in output.split("\n"):
        if line.strip():
            match = re.match(r"^(.*?):(\d+):\d+: (.*)$", line)
            if match:
                file_path = match.group(1)
                msg = match.group(3)
                if not file_path.startswith("src") and not file_path.startswith("tests"):
                    continue
                issues.append({"file": file_path, "tool": "flake8", "msg": msg})
    return issues


def parse_bandit(output):
    issues = []
    for line in output.split("\n"):
        if line.startswith(">> Issue: "):
            msg = (
                line.split(">> Issue: ")[1].split(" \n")[0]
                if " \n" in line
                else line.split(">> Issue: ")[1]
            )
        elif line.startswith("   Location: "):
            parts = line.split("   Location: ")[1].split(":")
            if len(parts) >= 2:
                file_path = parts[0]
                issues.append(
                    {"file": file_path, "tool": "bandit", "msg": msg, "severity": "critical"}
                )
    return issues


def parse_mypy(output):
    issues = []
    for line in output.split("\n"):
        if "error:" in line:
            match = re.match(r"^(.*?):\d+:(?:.*? )?error: (.*)$", line)
            if match:
                file_path = match.group(1)
                msg = match.group(2)
                issues.append({"file": file_path, "tool": "mypy", "msg": msg})
    return issues


def send_notification(issues):
    webhook_url = os.environ.get("WEBHOOK_URL")
    if not webhook_url:
        print("WEBHOOK_URL not set, skipping notifications.")
        return

    critical_issues = [i for i in issues if i.get("severity") == "critical"]
    if not critical_issues:
        print("No critical issues found, skipping notifications.")
        return

    message = f"🚨 Critical Security/Logic Failures Detected ({len(critical_issues)} issues):\n"
    for i in critical_issues[:5]:
        message += f"- {i['tool']} in {i['file']}: {i['msg']}\n"
    if len(critical_issues) > 5:
        message += f"... and {len(critical_issues) - 5} more."

    data = json.dumps({"text": message, "content": message}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req)
        print("Notification sent successfully.")
    except Exception as e:
        print(f"Failed to send notification: {e}")


def inject_tasks(issues):
    if not issues:
        print("No issues found.")
        return

    backlog_path = "docs/backlog.md"
    with open(backlog_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check what's already there
    existing_tasks = re.findall(r"- \*\*\[ \] TASK:\*\* auto-audit-(.*?) \|", content)

    tasks_to_add = []
    for issue in issues:
        file = issue["file"]
        tool = issue["tool"]
        msg = issue["msg"].replace("|", "").replace("\n", " ").strip()

        # generate a unique short hash
        hash_input = f"{file}-{tool}-{msg}".encode("utf-8")
        task_hash = hashlib.sha256(hash_input).hexdigest()[:8]

        if task_hash in existing_tasks or task_hash in content:
            continue

        task_str = (
            f"- **[ ] TASK:** auto-audit-{task_hash} | [DEBT] | **Loc:** {file} "
            f"| **Spec:** Fix {tool} error: {msg} | **Deps:** None | **LOC Estimate:** 10\n"
        )
        tasks_to_add.append(task_str)

    if not tasks_to_add:
        print("No new issues to inject.")
        return

    tasks_text = "".join(tasks_to_add)

    # Inject directly under "## 🐛 Identified Discrepancies (Hunters)"
    target_header = "## 🐛 Identified Discrepancies (Hunters)"
    if target_header in content:
        parts = content.split(target_header)
        new_content = parts[0] + target_header + "\n" + tasks_text + parts[1].lstrip("\n")
        with open(backlog_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Injected {len(tasks_to_add)} tasks into docs/backlog.md")
    else:
        print(f"Could not find '{target_header}' in docs/backlog.md")


if __name__ == "__main__":
    print("Running flake8...")
    flake8_out = run_command(["python", "-m", "flake8", "src/", "tests/"])
    flake8_issues = parse_flake8(flake8_out)

    print("Running bandit...")
    bandit_out = run_command(["python", "-m", "bandit", "-r", "src/", "tests/"])
    bandit_issues = parse_bandit(bandit_out)

    print("Running mypy...")
    mypy_out = run_command(["python", "-m", "mypy", "src/", "tests/"])
    mypy_issues = parse_mypy(mypy_out)

    all_issues = flake8_issues + bandit_issues + mypy_issues
    inject_tasks(all_issues)
    send_notification(all_issues)
