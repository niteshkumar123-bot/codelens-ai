# CodeLens AI

AI-Powered Python Code Analysis, Debugging & Automated Testing Platform.

## Overview

CodeLens AI is a full-stack developer platform that analyzes Python code
and identifies syntax, security, code-quality, and runtime issues.

The platform combines static code analysis with automated test generation
and isolated Docker-based execution to provide developers with actionable
analysis results.

## Key Features

- Python syntax validation
- Static code analysis
- Security vulnerability detection
- Code-quality analysis
- Automated pytest test generation
- Sandboxed Docker code execution
- Runtime error detection
- Severity-based findings
- Overall code-quality score
- Detailed analysis reports
- REST API for code analysis
- Web-based code editor and dashboard

## How It Works

```text
                    Code Submission
                           |
                           v
                  +------------------+
                  |   FastAPI API    |
                  +------------------+
                           |
                           v
                  +------------------+
                  | Code Analysis    |
                  | Engine           |
                  +------------------+
                    /      |       \
                   /       |        \
                  v        v         v
             Syntax    Security   Quality
             Analysis  Analysis   Analysis
                   \       |        /
                    \      |       /
                           v
                  +------------------+
                  | Test Generation  |
                  |     Pytest       |
                  +------------------+
                           |
                           v
                  +------------------+
                  | Docker Sandbox   |
                  | Runtime Testing  |
                  +------------------+
                           |
                           v
                  +------------------+
                  | Analysis Report  |
                  +------------------+
