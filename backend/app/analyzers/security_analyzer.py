import ast
import subprocess
import tempfile
import os
import json
from typing import List, Dict, Any

class SecurityAnalyzer:
    @staticmethod
    def analyze(code: str) -> List[Dict[str, Any]]:
        findings = []
        # Custom AST Security Scanner for dangerous calls (eval, exec, pickle, os.system, etc.)
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in ["eval", "exec"]:
                        findings.append({
                            "category": "security",
                            "severity": "critical",
                            "confidence": 0.99,
                            "rule_id": "SEC-DANGEROUS-EVAL",
                            "title": "Dangerous Dynamic Code Execution",
                            "description": f"Use of built-in function '{node.func.id}' allows arbitrary code execution and injection vulnerabilities.",
                            "line": node.lineno,
                            "column": node.col_offset,
                            "evidence": f"{node.func.id}(...)",
                            "recommendation": "Avoid eval() and exec(). Use safe parsers like ast.literal_eval for data structures."
                        })
                elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                    if node.value.id == "os" and node.attr in ["system", "popen", "spawn"]:
                        findings.append({
                            "category": "security",
                            "severity": "critical",
                            "confidence": 0.95,
                            "rule_id": "SEC-OS-SYSTEM",
                            "title": "Unsafe Operating System Call",
                            "description": f"Direct execution of 'os.{node.attr}' can lead to command injection.",
                            "line": node.lineno,
                            "column": node.col_offset,
                            "evidence": f"os.{node.attr}(...)",
                            "recommendation": "Use the 'subprocess' module with shell=False and argument lists."
                        })
        except Exception:
            pass

        # Integration with Bandit via temporary file execution
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tf:
            tf.write(code)
            tf_path = tf.name

        try:
            result = subprocess.run(
                ["bandit", "-f", "json", tf_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stdout:
                data = json.loads(result.stdout)
                for res in data.get("results", []):
                    findings.append({
                        "category": "security",
                        "severity": res.get("issue_severity", "MEDIUM").lower(),
                        "confidence": 0.90,
                        "rule_id": res.get("test_id", "BANDIT-SEC"),
                        "title": res.get("issue_text", "Security Issue Detected"),
                        "description": res.get("issue_text"),
                        "line": res.get("line_number"),
                        "column": None,
                        "evidence": res.get("code", "").strip(),
                        "recommendation": "Review secure coding guidelines for Python vulnerability mitigation."
                    })
        except Exception:
            pass
        finally:
            if os.path.exists(tf_path):
                os.unlink(tf_path)

        return findings
