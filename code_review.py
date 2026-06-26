import subprocess
import os

def review_changes():
    print("Initiating documentation and code audit review...")
    files_to_check = ["docs/vision.md", "docs/backlog.md", "docs/release-notes.md", "README.md", "src/services/ai/instrument_classifier.py"]
    for f in files_to_check:
        if os.path.exists(f):
            print(f"VERIFIED: {f} exists.")
        else:
            print(f"ERROR: {f} is missing!")

    # Check backlog schema adherence
    with open("docs/backlog.md", "r") as f:
        content = f.read()
        if "TASK:" in content and "Loc:" in content and "Spec:" in content:
             print("SUCCESS: Backlog follows mandatory schema.")
        else:
             print("FAILURE: Backlog schema mismatch.")

review_changes()
