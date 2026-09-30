import ast
from typing import List, Dict, Any

class CustomASTVisitor(ast.NodeVisitor):
    def __init__(self, code_lines: List[str]):
        self.code_lines = code_lines
        self.findings: List[Dict[str, Any]] = []
        self.variables_declared = set()
        self.variables_used = set()
        self.imports = set()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Check for mutable default arguments
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.findings.append({
                    "category": "ast",
                    "severity": "high",
                    "confidence": 0.95,
                    "rule_id": "AST-MUTABLE-DEFAULT",
                    "title": "Mutable Default Argument",
                    "description": f"Function '{node.name}' uses a mutable default argument ({type(default).__name__}), which retains state across calls.",
                    "line": node.lineno,
                    "column": node.col_offset,
                    "evidence": self._get_line(node.lineno),
                    "recommendation": "Use None as the default value and initialize the mutable object inside the function body."
                })
        
        # Check for excessive arguments
        if len(node.args.args) > 5:
            self.findings.append({
                "category": "quality",
                "severity": "medium",
                "confidence": 0.90,
                "rule_id": "AST-EXCESSIVE-ARGS",
                "title": "Excessive Function Arguments",
                "description": f"Function '{node.name}' has {len(node.args.args)} arguments (>5).",
                "line": node.lineno,
                "column": node.col_offset,
                "evidence": self._get_line(node.lineno),
                "recommendation": "Consider refactoring parameters into a configuration object or data class."
            })

        # Check for recursion without base case indicator (simple heuristic)
        has_recursion = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == node.name for n in ast.walk(node))
        has_return = any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(node))
        if has_recursion and not has_return:
            self.findings.append({
                "category": "logic",
                "severity": "critical",
                "confidence": 0.85,
                "rule_id": "AST-RECURSION-NO-BASE",
                "title": "Possible Missing Recursion Base Case",
                "description": f"Recursive function '{node.name}' may lack a definitive return condition or base case.",
                "line": node.lineno,
                "column": node.col_offset,
                "evidence": self._get_line(node.lineno),
                "recommendation": "Ensure proper termination checks are placed at the beginning of the recursive function."
            })

        self.generic_visit(node)

    def visit_Try(self, node: ast.Try):
        for handler in node.handlers:
            if handler.type is None:
                self.findings.append({
                    "category": "quality",
                    "severity": "high",
                    "confidence": 0.99,
                    "rule_id": "AST-BARE-EXCEPT",
                    "title": "Bare Except Clause",
                    "description": "Using a bare 'except:' catches all exceptions including SystemExit and KeyboardInterrupt.",
                    "line": handler.lineno,
                    "column": handler.col_offset,
                    "evidence": self._get_line(handler.lineno),
                    "recommendation": "Catch specific exceptions like Exception, ValueError, or KeyError."
                })
        self.generic_visit(node)

    def _get_line(self, lineno: int) -> str:
        if 0 < lineno <= len(self.code_lines):
            return self.code_lines[lineno - 1].strip()
        return ""

class ASTAnalyzer:
    @staticmethod
    def analyze(code: str) -> List[Dict[str, Any]]:
        lines = code.splitlines()
        try:
            tree = ast.parse(code)
            visitor = CustomASTVisitor(lines)
            visitor.visit(tree)
            return visitor.findings
        except Exception:
            return []
