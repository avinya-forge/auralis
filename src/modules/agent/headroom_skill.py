import ast
import copy
import hashlib
import logging
import os
from typing import Dict, List

logger = logging.getLogger(__name__)


class CodeHeadroom:
    """
    Skill to proactively identify areas of code that can be optimized or reduced for better performance and maintainability.
    """

    def __init__(self, llm_bridge):
        self.llm_bridge = llm_bridge

    def _strip_docstrings_and_names(self, node: ast.AST) -> ast.AST:
        """
        Strips docstrings and replaces variable/function names to create a structural fingerprint.
        """

        class NodeTransformer(ast.NodeTransformer):
            def visit_FunctionDef(self, n: ast.FunctionDef) -> ast.AST:
                n.name = "function"
                if ast.get_docstring(n):
                    n.body = n.body[1:]
                self.generic_visit(n)
                return n

            def visit_Name(self, n: ast.Name) -> ast.AST:
                n.id = "var"
                self.generic_visit(n)
                return n

            def visit_arg(self, n: ast.arg) -> ast.AST:
                n.arg = "arg"
                self.generic_visit(n)
                return n

        return NodeTransformer().visit(node)

    def analyze_file(self, filepath: str) -> List[Dict]:
        """
        Analyzes a single file for optimization opportunities.
        """
        try:
            with open(filepath, "r") as f:
                source = f.read()

            tree = ast.parse(source)

            opportunities = []

            # Subtask 1: Detect redundant functions and duplicate logic blocks
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            seen_fingerprints: Dict[str, ast.FunctionDef] = {}

            for func in functions:
                # Need a copy to avoid mutating the original tree if we need it
                func_copy = copy.deepcopy(func)
                structural_node = self._strip_docstrings_and_names(func_copy)
                fingerprint = ast.dump(structural_node)

                if fingerprint in seen_fingerprints:
                    original_func = seen_fingerprints[fingerprint]
                    opportunities.append(
                        {
                            "type": "duplicate_logic",
                            "description": f"Duplicate function logic detected between "
                            f"'{func.name}' (line {func.lineno}) and "
                            f"'{original_func.name}' (line {original_func.lineno}).",
                            "file": filepath,
                            "line": func.lineno,
                        }
                    )
                else:
                    seen_fingerprints[fingerprint] = func

            return opportunities
        except Exception as e:
            logger.error(f"Error analyzing {filepath}: {e}")
            return []

    def generate_refactoring_suggestions(self, opportunities: List[Dict]) -> List[Dict]:
        """
        Subtask 2: Generate refactoring suggestions automatically via LLM orchestration.
        """
        suggestions = []
        for opp in opportunities:
            prompt = (
                f"Given the following code optimization opportunity: "
                f"'{opp['description']}' in file {opp['file']}, "
                f"provide a concise refactoring suggestion."
            )
            try:
                response = self.llm_bridge.generate_response(prompt)
                opp["suggestion"] = response
                suggestions.append(opp)
            except Exception as e:
                logger.error(f"Failed to generate suggestion: {e}")
        return suggestions

    def inject_to_backlog(
        self, suggestions: List[Dict], backlog_path: str = "docs/backlog.md"
    ) -> None:
        """
        Subtask 3: Inject proposed optimizations into a new 'Tech Debt' backlog queue.
        """
        if not suggestions:
            return

        try:
            if not os.path.exists(backlog_path):
                logger.error(f"Backlog not found at {backlog_path}")
                return

            with open(backlog_path, "r") as f:
                content = f.read()

            # Check if Tech Debt section exists, if not add it
            if "## 🛠️ Tech Debt" not in content:
                content += "\n## 🛠️ Tech Debt\n"

            new_tasks = ""
            for sugg in suggestions:
                task_id = f"debt-{hashlib.md5(sugg['description'].encode(), usedforsecurity=False).hexdigest()[:8]}"
                # Avoid duplicates
                if task_id not in content:
                    task = (
                        f"- **[ ] TASK:** {task_id} | "
                        f"**Loc:** {sugg['file']} | "
                        f"**Spec:** {sugg['description']} "
                        f"Suggestion: {sugg.get('suggestion', 'None')}\n"
                    )
                    new_tasks += task

            if new_tasks:
                # Append to the end or under Tech Debt
                # For simplicity, append to the end of the file, assuming Tech Debt is the last section if we just added it,
                # or insert after the header if it exists.
                if "## 🛠️ Tech Debt" in content:
                    parts = content.split("## 🛠️ Tech Debt")
                    new_content = parts[0] + "## 🛠️ Tech Debt\n" + new_tasks + parts[1]
                else:
                    new_content = content + "\n## 🛠️ Tech Debt\n" + new_tasks

                with open(backlog_path, "w") as f:
                    f.write(new_content)

        except Exception as e:
            logger.error(f"Error injecting into backlog: {e}")
