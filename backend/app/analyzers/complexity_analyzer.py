import radon.complexity as cc
import radon.raw as raw
from typing import Dict, Any

class ComplexityAnalyzer:
    @staticmethod
    def analyze(code: str) -> Dict[str, Any]:
        try:
            blocks = cc.cc_visit(code)
            avg_complexity = sum(b.complexity for b in blocks) / len(blocks) if blocks else 1.0
            raw_metrics = raw.analyze(code)
            
            # Big-O estimation heuristic based on nested loops in AST
            import ast
            tree = ast.parse(code)
            loop_depth = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.For, ast.While)):
                    # Check for nested loops
                    depth = 1
                    for sub in ast.walk(node):
                        if isinstance(sub, (ast.For, ast.While)) and sub != node:
                            depth += 1
                    if depth > loop_depth:
                        loop_depth = depth

            time_complexity = "O(1)"
            if loop_depth == 1:
                time_complexity = "O(n)"
            elif loop_depth >= 2:
                time_complexity = f"O(n^{loop_depth})"

            return {
                "cyclomatic_complexity_average": round(avg_complexity, 2),
                "loc": raw_metrics.loc,
                "lloc": raw_metrics.lloc,
                "estimated_time_complexity": time_complexity,
                "estimated_space_complexity": "O(n)" if loop_depth > 0 else "O(1)",
                "confidence": 0.82,
                "reasoning": f"Static analysis detected maximum loop nesting depth of {loop_depth}."
            }
        except Exception:
            return {
                "cyclomatic_complexity_average": 1.0,
                "loc": len(code.splitlines()),
                "lloc": len(code.splitlines()),
                "estimated_time_complexity": "O(n)",
                "estimated_space_complexity": "O(1)",
                "confidence": 0.50,
                "reasoning": "Fallback complexity estimation due to parse error."
            }
