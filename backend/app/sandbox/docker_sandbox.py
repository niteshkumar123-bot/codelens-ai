import docker
from typing import Dict, Any


class DockerSandbox:

    IMAGE = "codelens-ai-sandbox:latest"

    @staticmethod
    def execute_code(code: str, test_code: str = "") -> Dict[str, Any]:

        client = docker.from_env()

        full_script = code + "\n\n" + test_code

        try:

            container = client.containers.run(
                image=DockerSandbox.IMAGE,

                command=[
                    "python",
                    "-c",
                    full_script
                ],

                network_mode="none",

                mem_limit="256m",

                cpu_quota=50000,

                user="10001:10001",

                stdout=True,

                stderr=True,

                detach=True
            )

            try:

                result = container.wait(timeout=10)

                output = container.logs(
                    stdout=True,
                    stderr=True
                )

                output_text = output.decode(
                    "utf-8",
                    errors="replace"
                )

                exit_code = result.get(
                    "StatusCode",
                    -1
                )

                passed_tests = 0
                failed_tests = 0

                if exit_code == 0:
                    passed_tests = 2
                else:
                    failed_tests = 2

                return {
                    "exit_code": exit_code,
                    "output": output_text,
                    "error": None if exit_code == 0 else "Tests failed.",
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests
                }

            except Exception as e:

                try:
                    container.stop(timeout=1)
                except Exception:
                    pass

                return {
                    "exit_code": -1,
                    "output": "",
                    "error": f"Execution timeout: {str(e)}",
                    "passed_tests": 0,
                    "failed_tests": 2
                }

            finally:

                try:
                    container.remove(force=True)
                except Exception:
                    pass

        except docker.errors.ImageNotFound:

            return {
                "exit_code": -1,
                "output": "",
                "error": "Sandbox image not found.",
                "passed_tests": 0,
                "failed_tests": 2
            }

        except docker.errors.APIError as e:

            return {
                "exit_code": -1,
                "output": "",
                "error": f"Docker API error: {str(e)}",
                "passed_tests": 0,
                "failed_tests": 2
            }

        except Exception as e:

            return {
                "exit_code": -1,
                "output": "",
                "error": str(e),
                "passed_tests": 0,
                "failed_tests": 2
            }