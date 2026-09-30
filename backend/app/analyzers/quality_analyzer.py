import subprocess
import tempfile
import os
import json
from typing import List, Dict, Any

class QualityAnalyzer:
    @staticmethod
    def analyze(code: str) -> List[Dict[str, Any]]:
        findings = []
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tf:
            tf.write(code)
            tf_path = tf.name

        try:
            result = subprocess.run(
                ["ruff", "check", "--format=json", tf_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stdout:
                data = json.loads(result.stdout)
                for item in data:
                    findings.append({
                        "category": "quality",
                        "severity": "medium",
                        "confidence": 0.95,
                        "rule_id": item.get("code", "RUFF-LINT"),
                        "title": item.get("message", "Code Quality Lint Issue"),
                        "description": item.get("message"),
                        "line": item.get("location", {}).get("row"),
                        "column": item.get("location", {}).get("column"),
                        "evidence": "",
                        "recommendation": item.get("fix", {}).get("message", "Refactor according to PEP 8 standards.")
                    })
        except Exception:
            pass
        finally:
            if os.path.exists(tf_path):
                os.unlink(tf_path)

        return findings
