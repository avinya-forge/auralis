with open("src/modules/neu/ai_batch_processor.py", "r") as f:
    lines = f.readlines()

# Remove typing.Optional
with open("src/modules/neu/ai_batch_processor.py", "w") as f:
    for line in lines:
        if "from typing import Any, Dict, List, Optional" in line:
            f.write("from typing import Any, Dict, List\n")
        else:
            f.write(line)

with open("tests/test_ai_batch_processor.py", "r") as f:
    lines = f.readlines()

with open("tests/test_ai_batch_processor.py", "w") as f:
    for line in lines:
        if "import pytest" in line:
            continue
        if "task_id1 = processor.enqueue_track" in line:
            f.write(line.replace("task_id1 = ", ""))
            continue
        if "task_id2 = processor.enqueue_track" in line:
            f.write(line.replace("task_id2 = ", ""))
            continue
        if "task_id = processor.enqueue_track" in line:
            f.write(line.replace("task_id = ", ""))
            continue
        f.write(line)

with open("tests/test_threshold_filter.py", "r") as f:
    lines = f.readlines()

with open("tests/test_threshold_filter.py", "w") as f:
    for line in lines:
        if "import pytest" in line:
            continue
        f.write(line)
