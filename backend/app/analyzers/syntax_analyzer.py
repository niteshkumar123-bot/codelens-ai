import ast
import py_compile
import tempfile
import os
from typing import Dict, Any

class SyntaxAnalyzer:
    @staticmethod
    def analyze(code: str) -> Dict[str, Any]:
        try:
            ast.parse(code)
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {
                "valid": False,
                "error": {
                    "type": "SyntaxError",
                    "message": str(e),
                    "line": e.lineno,
                    "column": e.offset,
                    "evidence": e.text.strip() if e.text else "",
                    "suggestion": "Check for unclosed brackets, missing colons, or indentation mismatches."
                }
            }
        except IndentationError as e:
            return {
                "valid": False,
                "error": {
                    "type": "IndentationError",
                    "message": str(e),
                    "line": e.lineno,
                    "column": e.offset,
                    "evidence": e.text.strip() if e.text else "",
                    "suggestion": "Ensure consistent use of spaces or tabs for indentation."
                }
            }
