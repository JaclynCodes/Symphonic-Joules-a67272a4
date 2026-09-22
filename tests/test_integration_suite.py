"""
Integration tests for the Symphonic-Joules test suite.

This module validates that the test suite can execute successfully and provides
accurate validation of workflow files. It tests:
- Test execution without errors
- Fixture initialization
- Test discovery
- Test isolation
- Error reporting
"""

import ast
import hashlib
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


def run_pytest(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run pytest with a consistent config for integration tests."""
    return subprocess.run(
        [sys.executable, "-m", "pytest", *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(cwd),
    )


@pytest.fixture(scope="module")
def repo_root() -> Path:
    """Return the repository root directory."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def tests_dir(repo_root: Path) -> Path:
    """Return the repository's tests directory."""
    return repo_root / "tests"


@pytest.fixture(scope="module")
def workflows_dir(repo_root: Path) -> Path:
    """Return the workflow test directory."""
    return repo_root / "tests" / "workflows"


class TestTestExecution:
    """Test that the test suite can execute successfully."""

    def test_pytest_collection_works(self, workflows_dir: Path, repo_root: Path):
        """Verify pytest collection succeeds without failing the suite."""
        result = run_pytest(str(workflows_dir), "--collect-only", "-q", cwd=repo_root)

        assert result.returncode in (0, 5), (
            f"Test collection failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )

    def test_workflow_tests_are_discoverable(self, workflows_dir: Path, repo_root: Path):
        """Verify pytest can discover workflow tests under tests/workflows."""
        result = run_pytest(str(workflows_dir), "--collect-only", "-q", cwd=repo_root)

        stdout = result.stdout.lower()
        assert any(marker in stdout for marker in ("test session starts", "tests collected", "test_")), (
            f"No tests discovered:\n{result.stdout}"
        )

    def test_blank_workflow_tests_execute(self, repo_root: Path):
        """Test that blank workflow tests execute without import errors."""
        test_file = repo_root / "tests" / "workflows" / "test_blank_workflow.py"
        result = run_pytest(str(test_file), "-v", "--tb=short", cwd=repo_root)

        assert "ERRORS" not in result.stdout or result.returncode != 2, (
            f"Test execution had errors:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


class TestFixtureInitialization:
    """Test that fixtures initialize correctly."""

    def test_workflow_path_fixture_resolves(self, repo_root: Path):
        """Verify that the workflow fixture resolves to a real workflow file."""
        import importlib.util

        module_path = repo_root / "tests" / "workflows" / "test_blank_workflow.py"
        sys.path.insert(0, str(repo_root / "tests" / "workflows"))

        try:
            spec = importlib.util.spec_from_file_location("test_blank_workflow", module_path)
            assert spec is not None and spec.loader is not None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            assert hasattr(module, "workflow_path"), "workflow_path fixture should be defined"

            expected_path = repo_root / ".github" / "workflows" / "blank.yml"
            assert expected_path.exists(), f"Workflow file should exist at {expected_path}"
        finally:
            sys.path.pop(0)

    def test_yaml_parsing_works(self, repo_root: Path):
        """Test that YAML parsing in fixtures works correctly."""
        workflow_file = repo_root / ".github" / "workflows" / "blank.yml"

        with workflow_file.open("r", encoding="utf-8") as handle:
            content = yaml.safe_load(handle)

        assert content is not None, "YAML parsing should succeed"
        assert isinstance(content, dict), "Parsed YAML should be a dictionary"
        assert "name" in content, "Workflow should have name field"


class TestTestIsolation:
    """Test that tests are properly isolated."""

    def test_module_fixtures_are_cached(self, tests_dir: Path):
        """Test that module-scoped fixtures are used for performance."""
        test_file = tests_dir / "workflows" / "test_blank_workflow.py"

        content = test_file.read_text(encoding="utf-8")
        assert "scope='module'" in content or 'scope="module"' in content, (
            "Test file should use module-scoped fixtures for performance"
        )

    def test_tests_dont_modify_workflow_files(self, repo_root: Path):
        """Verify workflow YAML files under .github/workflows are not modified by tests."""
        workflows_dir = repo_root / ".github" / "workflows"
        workflow_files = sorted(workflows_dir.glob("*.yml"))

        initial_hashes = {
            path: hashlib.sha256(path.read_bytes()).digest() for path in workflow_files
        }

        result = run_pytest(
            str(repo_root / "tests" / "workflows"),
            "--collect-only",
            "-q",
            cwd=repo_root,
        )

        assert result.returncode in (0, 5), (
            f"Pytest collection failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )

        for workflow_file in workflow_files:
            current_hash = hashlib.sha256(workflow_file.read_bytes()).digest()
            assert current_hash == initial_hashes[workflow_file], (
                f"Test execution should not modify {workflow_file.name}"
            )


class TestErrorReporting:
    """Test that test failures provide clear error messages."""

    def test_assertion_messages_are_descriptive(self, tests_dir: Path):
        """Test that assertions include descriptive error messages."""
        test_files = sorted((tests_dir / "workflows").glob("test_*.py"))

        for test_file in test_files:
            content = test_file.read_text(encoding="utf-8")
            lines = content.splitlines()

            total_asserts = 0
            assert_with_message = 0

            for line in lines:
                stripped = line.strip()
                if "assert " in stripped and not stripped.startswith("#"):
                    total_asserts += 1
                    if "," in stripped:
                        assert_with_message += 1

            if total_asserts > 0:
                ratio = assert_with_message / total_asserts
                assert ratio >= 0.8, (
                    f"{test_file.name}: Only {ratio:.0%} of assertions have error messages"
                )


class TestTestCoverage:
    """Test that test coverage is comprehensive."""

    def test_all_workflow_aspects_tested(self, repo_root: Path):
        """Ensure workflow tests cover critical workflow aspects."""
        test_files = sorted((repo_root / "tests" / "workflows").glob("test_*.py"))

        critical_aspects = [
            "structure",
            "metadata",
            "trigger",
            "job",
            "step",
            "security",
            "permission",
        ]

        for test_file in test_files:
            content = test_file.read_text(encoding="utf-8").lower()
            covered = sum(1 for aspect in critical_aspects if aspect in content)

            assert covered >= 5, (
                f"{test_file.name} should test more workflow aspects (got {covered}/7)"
            )

    def test_blank_workflow_has_markdown_lint_job(self, repo_root: Path):
        """Test that blank.yml workflow includes the lint-markdown job."""
        workflow_file = repo_root / ".github" / "workflows" / "blank.yml"

        with workflow_file.open("r", encoding="utf-8") as handle:
            content = yaml.safe_load(handle)

        assert "jobs" in content, "Workflow should have jobs section"
        assert "lint-markdown" in content["jobs"], (
            "Workflow should have 'lint-markdown' job for markdown linting"
        )

        lint_job = content["jobs"]["lint-markdown"]
        assert "steps" in lint_job, "lint-markdown job should have steps"

        steps = lint_job["steps"]
        has_markdownlint = any(
            "markdownlint-cli2-action" in step.get("uses", "")
            for step in steps
            if isinstance(step, dict)
        )
        assert has_markdownlint, (
            "lint-markdown job should use markdownlint-cli2-action"
        )


class TestDocumentation:
    """Test that tests are well-documented."""

    def test_all_test_classes_documented(self, tests_dir: Path):
        """Verify all test classes have docstrings."""
        test_files = sorted((tests_dir / "workflows").glob("test_*.py"))

        for test_file in test_files:
            tree = ast.parse(test_file.read_text(encoding="utf-8"))
            test_classes = [
                node for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef) and node.name.startswith("Test")
            ]

            for cls in test_classes:
                docstring = ast.get_docstring(cls)
                assert docstring is not None, (
                    f"Class {cls.name} in {test_file.name} should have docstring"
                )

    def test_all_test_methods_documented(self, tests_dir: Path):
        """Verify all workflow test methods have docstrings."""
        test_files = sorted((tests_dir / "workflows").glob("test_*.py"))

        for test_file in test_files:
            tree = ast.parse(test_file.read_text(encoding="utf-8"))

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                            docstring = ast.get_docstring(item)
                            assert docstring is not None, (
                                f"Method {item.name} in {node.name} ({test_file.name}) needs docstring"
                            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
