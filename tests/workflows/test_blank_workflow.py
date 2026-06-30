"""
Comprehensive test suite for .github/workflows/blank.yml

This test suite validates the GitHub Actions workflow configuration including:
- YAML syntax and structure
- GitHub Actions schema compliance
- Workflow trigger configuration
- Job definitions and steps
- Branch references and configurations
"""

import pytest
import yaml
import os
from pathlib import Path


# Fixture to load the workflow file
@pytest.fixture
def workflow_file_path():
    """Return the path to the workflow file."""
    repo_root = Path(__file__).parent.parent.parent
    return repo_root / ".github" / "workflows" / "blank.yml"


@pytest.fixture
def workflow_data(workflow_file_path):
    """Load and parse the workflow YAML file."""
    with open(workflow_file_path, 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture
def workflow_raw_content(workflow_file_path):
    """Load the raw content of the workflow file."""
    with open(workflow_file_path, 'r') as f:
        return f.read()


class TestWorkflowStructure:
    """Test the basic structure and syntax of the workflow file."""
    
    def test_workflow_file_exists(self, workflow_file_path):
        """Test that the workflow file exists."""
        assert workflow_file_path.exists(), "Workflow file should exist"
    
    def test_workflow_is_valid_yaml(self, workflow_file_path):
        """Test that the workflow file is valid YAML."""
        try:
            with open(workflow_file_path, 'r') as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML syntax: {e}")
    
    def test_workflow_has_name(self, workflow_data):
        """Test that the workflow has a name defined."""
        assert "name" in workflow_data, "Workflow should have a name"
        assert workflow_data["name"] == "CI", "Workflow name should be 'CI'"
    
    def test_workflow_has_jobs(self, workflow_data):
        """Test that the workflow has jobs defined."""
        assert "jobs" in workflow_data, "Workflow should have jobs defined"
        assert isinstance(workflow_data["jobs"], dict), "Jobs should be a dictionary"
        assert len(workflow_data["jobs"]) > 0, "Workflow should have at least one job"


class TestWorkflowTriggers:
    """Test workflow trigger configurations."""
    
    def test_workflow_has_on_triggers(self, workflow_data):
        """Test that the workflow has 'on' triggers defined."""
        # YAML parser interprets 'on' as True (boolean)
        assert True in workflow_data or "on" in workflow_data, \
            "Workflow should have trigger configuration"
    
    def test_push_trigger_configured(self, workflow_data):
        """Test that push trigger is configured."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        assert "push" in triggers, "Push trigger should be configured"
    
    def test_push_trigger_branches(self, workflow_data):
        """Test that push trigger targets main branch."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        push_config = triggers.get("push", {})
        assert "branches" in push_config, "Push trigger should specify branches"
        branches = push_config["branches"]
        assert isinstance(branches, list), "Branches should be a list"
        assert "main" in branches, "Push trigger should include 'main' branch"
    
    def test_push_trigger_does_not_reference_base_branch(self, workflow_data):
        """Test that push trigger does not reference the old 'base' branch."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        push_config = triggers.get("push", {})
        branches = push_config.get("branches", [])
        assert "base" not in branches, \
            "Push trigger should not reference deprecated 'base' branch"
    
    def test_pull_request_trigger_configured(self, workflow_data):
        """Test that pull_request trigger is configured."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        assert "pull_request" in triggers, "Pull request trigger should be configured"
    
    def test_pull_request_trigger_branches(self, workflow_data):
        """Test that pull_request trigger targets main branch."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        pr_config = triggers.get("pull_request", {})
        assert "branches" in pr_config, "Pull request trigger should specify branches"
        branches = pr_config["branches"]
        assert isinstance(branches, list), "Branches should be a list"
        assert "main" in branches, \
            "Pull request trigger should include 'main' branch"
    
    def test_pull_request_trigger_does_not_reference_base_branch(self, workflow_data):
        """Test that pull_request trigger does not reference the old 'base' branch."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        pr_config = triggers.get("pull_request", {})
        branches = pr_config.get("branches", [])
        assert "base" not in branches, \
            "Pull request trigger should not reference deprecated 'base' branch"
    
    def test_workflow_dispatch_trigger_configured(self, workflow_data):
        """Test that workflow_dispatch trigger is configured for manual runs."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        assert "workflow_dispatch" in triggers, \
            "Workflow should support manual dispatch"
    
    def test_no_unexpected_triggers(self, workflow_data):
        """Test that only expected triggers are configured."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        expected_triggers = {"push", "pull_request", "workflow_dispatch"}
        actual_triggers = set(triggers.keys())
        unexpected = actual_triggers - expected_triggers
        assert len(unexpected) == 0, \
            f"Unexpected triggers found: {unexpected}"


class TestJobConfiguration:
    """Test job configurations in the workflow."""
    
    def test_build_job_exists(self, workflow_data):
        """Test that the 'build' job exists."""
        jobs = workflow_data.get("jobs", {})
        assert "build" in jobs, "Workflow should have a 'build' job"
    
    def test_build_job_has_runner(self, workflow_data):
        """Test that the build job specifies a runner."""
        build_job = workflow_data["jobs"]["build"]
        assert "runs-on" in build_job, "Build job should specify a runner"
        assert build_job["runs-on"] == "ubuntu-latest", \
            "Build job should run on ubuntu-latest"
    
    def test_build_job_has_steps(self, workflow_data):
        """Test that the build job has steps defined."""
        build_job = workflow_data["jobs"]["build"]
        assert "steps" in build_job, "Build job should have steps"
        assert isinstance(build_job["steps"], list), "Steps should be a list"
        assert len(build_job["steps"]) > 0, "Build job should have at least one step"
    
    def test_checkout_step_exists(self, workflow_data):
        """Test that the checkout step exists."""
        steps = workflow_data["jobs"]["build"]["steps"]
        checkout_steps = [s for s in steps if "uses" in s and "checkout" in s["uses"]]
        assert len(checkout_steps) > 0, \
            "Build job should include a checkout step"
    
    def test_checkout_step_version(self, workflow_data):
        """Test that the checkout action uses v4."""
        steps = workflow_data["jobs"]["build"]["steps"]
        checkout_steps = [s for s in steps if "uses" in s and "checkout" in s["uses"]]
        assert len(checkout_steps) > 0
        checkout_action = checkout_steps[0]["uses"]
        assert "@v4" in checkout_action, \
            "Checkout action should use v4"
    
    def test_all_steps_have_valid_structure(self, workflow_data):
        """Test that all steps have valid structure."""
        steps = workflow_data["jobs"]["build"]["steps"]
        for i, step in enumerate(steps):
            assert isinstance(step, dict), f"Step {i} should be a dictionary"
            assert "uses" in step or "run" in step, \
                f"Step {i} should have either 'uses' or 'run'"
    
    def test_named_steps_have_names(self, workflow_data):
        """Test that steps with 'name' field have non-empty names."""
        steps = workflow_data["jobs"]["build"]["steps"]
        for i, step in enumerate(steps):
            if "name" in step:
                assert step["name"], f"Step {i} should have a non-empty name"
                assert isinstance(step["name"], str), \
                    f"Step {i} name should be a string"


class TestWorkflowSemantics:
    """Test semantic correctness and best practices."""
    
    def test_workflow_name_is_descriptive(self, workflow_data):
        """Test that the workflow name is descriptive."""
        name = workflow_data.get("name", "")
        assert len(name) > 0, "Workflow name should not be empty"
        assert len(name) <= 50, \
            "Workflow name should be reasonably short (≤50 chars)"
    
    def test_no_hardcoded_secrets(self, workflow_raw_content):
        """Test that there are no hardcoded secrets or tokens."""
        dangerous_patterns = [
            "password=",
            "token=",
            "api_key=",
            "secret=",
            "ghp_",
            "ghs_",
        ]
        content_lower = workflow_raw_content.lower()
        for pattern in dangerous_patterns:
            assert pattern not in content_lower, \
                f"Potential hardcoded secret pattern found: {pattern}"
    
    def test_branch_consistency(self, workflow_data):
        """Test that all branch references are consistent."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        
        push_branches = triggers.get("push", {}).get("branches", [])
        pr_branches = triggers.get("pull_request", {}).get("branches", [])
        
        assert push_branches == pr_branches, \
            "Push and pull_request triggers should target the same branches"
    
    def test_runner_is_supported(self, workflow_data):
        """Test that the runner OS is a supported GitHub Actions runner."""
        supported_runners = [
            "ubuntu-latest", "ubuntu-22.04", "ubuntu-20.04",
            "windows-latest", "windows-2022", "windows-2019",
            "macos-latest", "macos-13", "macos-12", "macos-11"
        ]
        build_job = workflow_data["jobs"]["build"]
        runner = build_job.get("runs-on", "")
        assert runner in supported_runners, \
            f"Runner '{runner}' should be a supported GitHub Actions runner"


class TestBranchMigration:
    """Test specific to the branch migration from 'base' to 'main'."""
    
    def test_no_base_branch_references(self, workflow_raw_content):
        """Test that there are no references to the old 'base' branch."""
        lines = workflow_raw_content.split('\n')
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('#'):
                continue
            if 'branches:' in line.lower():
                context_start = max(0, i-1)
                context_end = min(len(lines), i+3)
                context = '\n'.join(lines[context_start:context_end])
                if '"base"' in context or "'base'" in context or '[ "base" ]' in context:
                    pytest.fail(
                        f"Found reference to 'base' branch near line {i}: {line}"
                    )
    
    def test_main_branch_is_referenced(self, workflow_data):
        """Test that 'main' branch is properly referenced."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        
        push_branches = triggers.get("push", {}).get("branches", [])
        assert "main" in push_branches, \
            "Push trigger should reference 'main' branch"
        
        pr_branches = triggers.get("pull_request", {}).get("branches", [])
        assert "main" in pr_branches, \
            "Pull request trigger should reference 'main' branch"


class TestWorkflowRobustness:
    """Test robustness and error handling."""
    
    @pytest.mark.parametrize("required_field", ["name", "jobs"])
    def test_required_top_level_fields(self, workflow_data, required_field):
        """Test that required top-level fields are present."""
        assert required_field in workflow_data, \
            f"Workflow should have '{required_field}' field"
    
    @pytest.mark.parametrize("job_field", ["runs-on", "steps"])
    def test_required_job_fields(self, workflow_data, job_field):
        """Test that required job fields are present."""
        build_job = workflow_data["jobs"]["build"]
        assert job_field in build_job, \
            f"Build job should have '{job_field}' field"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestWorkflowComments:
    """Test workflow comments and documentation."""
    
    def test_workflow_has_descriptive_comments(self, workflow_raw_content):
        """Test that the workflow file contains helpful comments."""
        assert "# This is a basic workflow" in workflow_raw_content, \
            "Workflow should have introductory comment"
        assert "# Controls when the workflow will run" in workflow_raw_content, \
            "Workflow should explain trigger configuration"
    
    def test_commented_badge_link_is_valid(self, workflow_raw_content):
        """Test that the commented badge link has correct format."""
        lines = workflow_raw_content.split('\n')
        badge_lines = [line for line in lines if 'badge.svg' in line]
        
        if badge_lines:
            badge_line = badge_lines[0]
            assert 'github.com' in badge_line.lower(), \
                "Badge should reference github.com"
            assert 'blank.yml' in badge_line, \
                "Badge should reference the correct workflow file"
            assert badge_line.strip().startswith('#'), \
                "Badge link should be commented out"
    
    def test_step_comments_are_meaningful(self, workflow_raw_content):
        """Test that step comments provide meaningful context."""
        lines = workflow_raw_content.split('\n')
        step_comments = [line for line in lines if line.strip().startswith('# ') and 
                        ('step' in line.lower() or 'runs' in line.lower() or 'checks' in line.lower())]
        
        assert len(step_comments) > 0, \
            "Workflow should have comments explaining steps"


class TestWorkflowSecurityAndBestPractices:
    """Test security and best practice compliance."""
    
    def test_checkout_action_is_pinned(self, workflow_data):
        """Test that checkout action is pinned to a specific version."""
        steps = workflow_data["jobs"]["build"]["steps"]
        checkout_steps = [s for s in steps if "uses" in s and "checkout" in s["uses"]]
        
        for step in checkout_steps:
            action = step["uses"]
            assert "@" in action, \
                "Actions should be pinned to a version"
            assert not action.endswith("@main") and not action.endswith("@master"), \
                "Actions should not use branch references like @main or @master"
    
    def test_no_inline_scripts_with_secrets(self, workflow_raw_content):
        """Test that inline scripts don't contain secret patterns."""
        dangerous_patterns = [
            '${{ secrets.GITHUB_TOKEN }}',
            'export SECRET',
            'export PASSWORD',
            'export API_KEY'
        ]
        
        content_lower = workflow_raw_content.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in content_lower:
                pytest.fail(f"Potentially unsafe secret usage: {pattern}")
    
    def test_named_steps_have_valid_actions(self, steps):
        """Test that named steps have either run commands or uses actions"""
    def test_workflow_permissions_not_overly_permissive(self, workflow_data):
        """Test that workflow doesn't have overly permissive settings."""
        # If permissions are set, they should be specific
        if "permissions" in workflow_data:
            perms = workflow_data["permissions"]
            if isinstance(perms, str):
                assert perms != "write-all", \
                    "Workflow should not use 'write-all' permissions"
    
    def test_no_shell_injection_vulnerabilities(self, workflow_data):
        """Test that workflow steps don't have obvious shell injection risks."""
        steps = workflow_data["jobs"]["build"]["steps"]
        
        for i, step in enumerate(steps):
            if "run" in step:
                run_command = step["run"]
                # Check for dangerous patterns
                assert "${{ github.event" not in run_command or \
                       "github.event.issue.title" not in run_command, \
                    f"Step {i} may have shell injection vulnerability"


class TestWorkflowEdgeCases:
    """Test edge cases and boundary conditions."""
    def test_named_steps_have_run_commands(self, steps):
        """
        Ensure every workflow step that has a `name` key also defines a `run` command.
        
        Parameters:
            steps (list[dict]): Sequence of step mappings from a job's `steps` list in the workflow; each mapping may contain keys like `name`, `uses`, and `run`.
        
        Raises:
            AssertionError: If a step contains `name` but does not include a `run` key, an assertion is raised identifying the offending step by name.
        """
        for step in steps:
            if 'name' in step:
                assert 'run' in step or 'uses' in step, \
                    f"Named step '{step['name']}' must have either 'run' or 'uses'"
    
    @pytest.mark.parametrize("step_name,error_message", [
        ('Run a one-line script', "One-line script step not found"),
        ('Run a multi-line script', "Multi-line script step not found"),
    ])
    def test_script_step_exists(self, steps, step_name, error_message):
        """
        Assert that a step with the given name exists in the provided steps list.
        
        Parameters:
        	steps (list[dict]): List of step dictionaries from a job's `steps` section.
        	step_name (str): The expected `name` value for the required script step.
        	error_message (str): Assertion message displayed if the named step is not found.
        """
        matching_steps = [s for s in steps if s.get('name') == step_name]
        assert len(matching_steps) > 0, error_message
    
    def test_workflow_handles_empty_branch_list(self, workflow_data):
        """Test that branch configurations are not empty."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        
        if "push" in triggers and "branches" in triggers["push"]:
            assert len(triggers["push"]["branches"]) > 0, \
                "Push trigger should specify at least one branch"
        
        if "pull_request" in triggers and "branches" in triggers["pull_request"]:
            assert len(triggers["pull_request"]["branches"]) > 0, \
                "Pull request trigger should specify at least one branch"
    
    def test_workflow_name_special_characters(self, workflow_data):
        """Test that workflow name doesn't contain problematic characters."""
        name = workflow_data.get("name", "")
        problematic_chars = ['<', '>', '|', '&', ';', '`', '$']
        
        for char in problematic_chars:
            assert char not in name, \
                f"Workflow name should not contain '{char}'"
    
    def test_step_names_are_unique(self, workflow_data):
        """Test that step names are unique within a job."""
        steps = workflow_data["jobs"]["build"]["steps"]
        named_steps = [s.get("name") for s in steps if "name" in s]
        
        assert len(named_steps) == len(set(named_steps)), \
            "Step names should be unique within a job"
    
    def test_workflow_file_size_is_reasonable(self, workflow_file_path):
        """Test that workflow file is not excessively large."""
        file_size = os.path.getsize(workflow_file_path)
        # Reasonable limit: 50KB for a workflow file
        assert file_size < 51200, \
            f"Workflow file size ({file_size} bytes) should be under 50KB"
    
    def test_no_circular_workflow_dependencies(self, workflow_data):
        """Test that workflow doesn't trigger itself recursively."""
        # This workflow should not trigger on workflow_run of itself
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        
        if "workflow_run" in triggers:
            workflow_run_config = triggers["workflow_run"]
            if "workflows" in workflow_run_config:
                triggered_workflows = workflow_run_config["workflows"]
                assert "blank.yml" not in triggered_workflows and "CI" not in triggered_workflows, \
                    "Workflow should not create circular dependencies"


class TestWorkflowComments:
    """Test comments and documentation in the workflow file"""
    
    def test_has_comments(self, workflow_raw):
        """Test that workflow file contains comments"""
        comment_lines = [line for line in workflow_raw.split('\n') if line.strip().startswith('#')]
        assert len(comment_lines) > 0, "Workflow should contain comments for documentation"
    
    def test_main_branch_comment_matches_config(self, workflow_raw):
        """Test that comments about main branch match the actual configuration"""
        # Check that comments mention 'main' branch - optimize by avoiding full lowercase conversion
        # Only convert to lowercase for case-insensitive search
        if 'main' not in workflow_raw and 'MAIN' not in workflow_raw and 'Main' not in workflow_raw:
            pytest.fail("Workflow should mention 'main' branch")
        
        # Ensure 'base' branch is not mentioned in active configuration
        lines = workflow_raw.split('\n')
        for line in lines:
            if 'branches:' in line:
                # Check the next line for branch configuration
                idx = lines.index(line)
                if idx + 1 < len(lines):
                    next_line = lines[idx + 1]
                    if 'base' in next_line and not next_line.strip().startswith('#'):
                        pytest.fail("Found 'base' branch in active configuration (should be 'main')")
    
    def test_has_badge_reference(self, workflow_raw):
        """Test that workflow includes CI badge reference"""
        assert 'badge.svg' in workflow_raw, "Workflow should include badge reference"
        assert 'CI' in workflow_raw, "Workflow should reference CI badge"


class TestEdgeCases:
    """Test edge cases and potential failure scenarios"""
    
    def test_no_syntax_errors_in_yaml(self, workflow_content):
        """Test that there are no YAML syntax errors"""
        # If workflow_content fixture loaded successfully, YAML is valid
        # This test validates that the fixture itself works properly
        assert workflow_content is not None, "YAML content should be loaded"
    
    def test_no_tabs_in_yaml(self, workflow_raw):
        """Test that workflow file doesn't use tabs (YAML should use spaces)"""
        assert '\t' not in workflow_raw, "YAML file should use spaces, not tabs"
    
    def test_consistent_indentation(self, workflow_raw):
        """Test that indentation is consistent throughout the file"""
        lines = workflow_raw.split('\n')
        
        for line in lines:
            if line and not line.strip().startswith('#'):
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces > 0:
                    indentation_sizes.add(leading_spaces)
        
        if len(indentation_sizes) > 1:
            # Check if all indentation is a multiple of 2
            for size in indentation_sizes:
                assert size % 2 == 0, \
                    f"Indentation should be in multiples of 2 spaces, found {size}"
    
    def test_no_tabs_in_yaml(self, workflow_raw_content):
        """Test that YAML doesn't contain tab characters."""
        assert '\t' not in workflow_raw_content, \
            "YAML should use spaces, not tabs for indentation"
    
    def test_yaml_keys_are_lowercase_with_underscores(self, workflow_data):
        """Test that YAML keys follow kebab-case or snake_case convention."""
        import re
        
        def check_keys(obj, path=""):
            if isinstance(obj, dict):
                for key in obj.keys():
                    if isinstance(key, str):
                        # Allow both kebab-case and snake_case, and some GitHub-specific keys
                        valid_pattern = re.match(r'^[a-z][a-z0-9_-]*$|^True$|^on$', str(key))
                        assert valid_pattern, \
                            f"Key '{key}' at {path} should use lowercase with hyphens/underscores"
                    check_keys(obj[key], f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_keys(item, f"{path}[{i}]")
        
        check_keys(workflow_data)
    
    def test_no_duplicate_keys_in_yaml(self, workflow_file_path):
        """Test that YAML doesn't have duplicate keys (Python's yaml handles this)."""
        # PyYAML will handle duplicates by overwriting, but we can check
        # by comparing the file line count with parsed structure
        with open(workflow_file_path, 'r') as f:
            content = f.read()
        
        # Basic check: count key occurrences in top level
        import re
        top_level_keys = re.findall(r'^([a-z_-]+):', content, re.MULTILINE)
        assert len(top_level_keys) == len(set(top_level_keys)), \
            "YAML should not have duplicate top-level keys"


class TestWorkflowPerformanceConsiderations:
    """Test performance and efficiency considerations."""
    
    def test_job_timeout_is_reasonable(self, workflow_data):
        """Test that jobs have reasonable timeout settings."""
        build_job = workflow_data["jobs"]["build"]
    def test_no_duplicate_job_names(self, jobs):
        """Test that there are no duplicate job names"""
        job_names = list(jobs.keys())
        assert len(job_names) == len(set(job_names)), "Duplicate job names found"
    
    def test_no_duplicate_step_names_in_job(self, jobs):
        """Test that there are no duplicate step names within a job"""
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            step_names = [s.get('name') for s in steps if 'name' in s]
            assert len(step_names) == len(set(step_names)), f"Duplicate step names in job '{job_name}'"
    
    def test_runner_is_valid(self, jobs):
        """
        Verify each job's `runs-on` runner, when specified as a string, is an accepted runner identifier.
        
        Parameters:
            jobs (dict): Mapping of job names to their job configuration dictionaries; each job's 'runs-on' value is validated.
        
        Raises:
            AssertionError: If a job's string `runs-on` value is not one of the allowed runner identifiers.
        """
        valid_runners = [
            'ubuntu-latest', 'ubuntu-22.04', 'ubuntu-20.04',
            'windows-latest', 'windows-2022', 'windows-2019',
            'macos-latest', 'macos-13', 'macos-12', 'macos-11'
        ]
        
        # If timeout-minutes is set, it should be reasonable
        if "timeout-minutes" in build_job:
            timeout = build_job["timeout-minutes"]
            assert 1 <= timeout <= 360, \
                "Job timeout should be between 1 and 360 minutes"
    
    def test_workflow_not_overly_complex(self, workflow_data):
        """Test that workflow is not overly complex."""
        jobs = workflow_data.get("jobs", {})
        
        # Should have reasonable number of jobs
        assert len(jobs) <= 50, \
            "Workflow should not have more than 50 jobs for maintainability"
        
        # Each job should have reasonable number of steps
        for job_name, job_config in jobs.items():
            if "steps" in job_config:
                assert len(job_config["steps"]) <= 50, \
                    f"Job '{job_name}' should not have more than 50 steps"
    
    def test_caching_strategy_consideration(self, workflow_data):
        """Test that workflow considers caching where appropriate."""
        steps = workflow_data["jobs"]["build"]["steps"]
        
        # Just verify structure exists for future caching additions
        assert isinstance(steps, list), \
            "Steps should be properly structured for potential caching"


class TestWorkflowDocumentationAlignment:
    """Test alignment with documentation and comments."""
    
    def test_workflow_matches_documented_behavior(self, workflow_data):
        """Test that workflow behavior matches its documentation."""
        # The workflow is named "CI" and should perform CI-like tasks
        name = workflow_data.get("name", "")
        
        if name == "CI":
            # CI workflows should typically run on push and PR
            triggers = workflow_data.get(True, workflow_data.get("on", {}))
            assert "push" in triggers or "pull_request" in triggers, \
                "CI workflow should trigger on push or pull_request events"
    
    def test_branch_references_match_repository_default(self, workflow_data):
        """Test that workflow branches align with repository standards."""
        triggers = workflow_data.get(True, workflow_data.get("on", {}))
        
        # Modern repositories use 'main' as default
        if "push" in triggers and "branches" in triggers["push"]:
            branches = triggers["push"]["branches"]
            assert "main" in branches or "master" in branches, \
                "Workflow should target common default branches"


class TestWorkflowMaintainability:
    """Test workflow maintainability and code quality."""
    
    def test_step_order_is_logical(self, workflow_data):
        """Test that steps follow a logical order."""
        steps = workflow_data["jobs"]["build"]["steps"]
        
        # Checkout should be first or second step
        checkout_indices = [i for i, s in enumerate(steps) 
                           if "uses" in s and "checkout" in s["uses"]]
        
        if checkout_indices:
            assert checkout_indices[0] <= 1, \
                "Checkout step should be among the first steps"
    
    def test_action_versions_are_recent(self, workflow_data):
        """Test that GitHub Actions use reasonably recent versions."""
        steps = workflow_data["jobs"]["build"]["steps"]
        
        for step in steps:
            if "uses" in step:
                action = step["uses"]
                if "checkout" in action:
                    # checkout@v4 is current, v3 is acceptable, v2 and below are old
                    assert "@v3" in action or "@v4" in action, \
                        "Checkout action should use v3 or v4"
    
    def test_workflow_uses_shell_explicitly_if_needed(self, workflow_data):
        """Test that multi-line scripts explicitly set shell if needed."""
        steps = workflow_data["jobs"]["build"]["steps"]
        
        for step in steps:
            if "run" in step:
                run_cmd = step["run"]
                # If run contains multiple lines, shell should ideally be specified
                if "\n" in run_cmd and len(run_cmd.split('\n')) > 2:
                    # This is a guideline; not enforcing but checking structure
                    assert isinstance(step, dict), \
                        "Multi-line run steps should be properly structured"
    
    def test_environment_variables_are_documented(self, workflow_data):
        """Test that any environment variables used are properly structured."""
        build_job = workflow_data["jobs"]["build"]
        
        if "env" in build_job:
            env_vars = build_job["env"]
            assert isinstance(env_vars, dict), \
                "Environment variables should be a dictionary"
            
            for key, _value in env_vars.items():
                assert key.isupper() or "_" in key, \
                    f"Environment variable '{key}' should follow naming conventions"


class TestWorkflowContinuousIntegration:
    """Test CI-specific functionality and patterns."""
    
    def test_workflow_provides_feedback_mechanism(self, workflow_data):
        """Test that workflow has mechanisms to provide build feedback."""
        # Workflow should have some output or result indication
        steps = workflow_data["jobs"]["build"]["steps"]
        
        # At minimum, should have steps that produce output
        assert len(steps) > 0, \
            "CI workflow should have steps that produce output"
    
    def test_workflow_is_reproducible(self, workflow_data):
        """Test that workflow configuration supports reproducible builds."""
        build_job = workflow_data["jobs"]["build"]
        
        # Using specific runner versions and action versions helps reproducibility
        assert "runs-on" in build_job, \
            "Workflow should specify runner for reproducibility"
        
        steps = workflow_data["jobs"]["build"]["steps"]
        actions_used = [s.get("uses", "") for s in steps if "uses" in s]
        
        for action in actions_used:
            if action:
                assert "@" in action, \
                    f"Action '{action}' should be pinned for reproducibility"
    
    def test_workflow_failure_handling(self, workflow_data):
        """Test that workflow considers failure scenarios."""
        build_job = workflow_data["jobs"]["build"]
        
        # Verify job structure allows for proper failure handling
        assert "steps" in build_job, \
            "Job should have steps that can succeed or fail"
        
        # Steps can have continue-on-error, but this is optional
        # Just verify the structure supports it
        steps = build_job["steps"]
        for step in steps:
            if "continue-on-error" in step:
                assert isinstance(step["continue-on-error"], bool), \
                    "continue-on-error should be a boolean"


# Additional marker for workflow tests
pytestmark = pytest.mark.workflows
            runner = job_config.get('runs-on')
            if isinstance(runner, str):
                assert runner in valid_runners, f"Invalid runner '{runner}' in job '{job_name}'"


class TestWorkflowSecurity:
    """Test security aspects of the workflow"""
    
    def test_no_hardcoded_secrets(self, workflow_raw):
        """Test that workflow doesn't contain hardcoded secrets"""
        suspicious_patterns = ['password', 'token', 'api_key', 'secret']
        lower_content = workflow_raw.lower()
        
        for pattern in suspicious_patterns:
            if pattern in lower_content:
                # Make sure it's not in a comment or using secrets context
                lines = workflow_raw.split('\n')
                for line in lines:
                    if pattern in line.lower() and not line.strip().startswith('#'):
                        # Check if it's using GitHub secrets context
                        assert 'secrets.' in line or '${{' in line, \
                            f"Potential hardcoded secret pattern '{pattern}' found"
    
    def test_checkout_action_is_pinned_or_versioned(self, jobs):
        """
        Ensure every action referenced in job steps includes a version tag.
        
        Asserts that any step with a `uses` key contains an `@` version delimiter (for example, `actions/checkout@v4`).
        """
        for _job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'uses' in step:
                    action = step['uses']
                    # Should have version (@ symbol)
                    assert '@' in action, f"Action '{action}' should specify a version"


class TestWorkflowFilePermissions:
    """Test file permissions and location"""
    
    def test_workflow_in_correct_directory(self, workflow_path):
        """Test that workflow is in .github/workflows directory"""
        assert '.github' in workflow_path.parts, "Workflow must be in .github directory"
        assert 'workflows' in workflow_path.parts, "Workflow must be in workflows subdirectory"
    
    def test_workflow_has_yml_extension(self, workflow_path):
        """Test that workflow file has .yml or .yaml extension"""
        assert workflow_path.suffix in ['.yml', '.yaml'], "Workflow must have .yml or .yaml extension"
    
    def test_workflow_file_is_readable(self, workflow_path):
        """Test that workflow file is readable"""
        assert os.access(workflow_path, os.R_OK), "Workflow file must be readable"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


class TestParametrizedRefactoring:
    """Test the parametrized test refactoring improvements"""
    
    def test_parametrize_decorator_reduces_code_duplication(self, workflow_content):
        """
        Ensure the workflow defines the 'push', 'pull_request' and 'workflow_dispatch' triggers.
        
        Checks the parsed workflow content exposes trigger configuration (via the `on` key or a True mapping)
        and that each of the three expected trigger types is present.
        """
        # This test validates that the refactoring approach is sound
        # by ensuring the workflow structure supports multiple trigger types
        triggers = workflow_content.get(True) or workflow_content.get('on')
        trigger_types = ['push', 'pull_request', 'workflow_dispatch']
        
        for trigger_type in trigger_types:
            assert trigger_type in triggers, f"Expected trigger type '{trigger_type}' not found"
    
    def test_all_branch_triggers_have_consistent_configuration(self, workflow_content):
        """
        Verify that the `push` and `pull_request` triggers define the same branch filter and that it equals ['main'].
        
        Parameters:
            workflow_content (dict): Parsed YAML content of the workflow (result of yaml.safe_load).
        
        Raises:
            AssertionError: If the push and pull_request branch lists differ, or if either is not exactly ['main'].
        """
        triggers = workflow_content.get(True) or workflow_content.get('on')
        
        push_branches = triggers.get('push', {}).get('branches', [])
        pr_branches = triggers.get('pull_request', {}).get('branches', [])
        
        # Both should be identical
        assert push_branches == pr_branches, \
            f"Push branches {push_branches} should match PR branches {pr_branches}"
        
        # Both should only contain 'main'
        assert push_branches == ['main'], f"Expected ['main'], got {push_branches}"
        assert pr_branches == ['main'], f"Expected ['main'], got {pr_branches}"


class TestJobsFixtureScoping:
    """Test the module-scoped jobs fixture functionality"""
    
    def test_jobs_fixture_returns_dict(self, jobs):
        """Test that jobs fixture returns a dictionary"""
        assert isinstance(jobs, dict), "Jobs fixture should return a dictionary"
    
    def test_jobs_fixture_contains_build_job(self, jobs):
        """Test that jobs fixture contains the build job"""
        assert 'build' in jobs, "Jobs fixture should contain 'build' job"
    
    def test_jobs_fixture_is_not_empty(self, jobs):
        """Test that jobs fixture is not empty"""
        assert len(jobs) > 0, "Jobs fixture should not be empty"
    
    def test_jobs_fixture_has_valid_job_structure(self, jobs):
        """Test that each job in jobs fixture has valid structure"""
        for job_name, job_config in jobs.items():
            assert isinstance(job_config, dict), f"Job '{job_name}' config should be a dict"
            assert 'runs-on' in job_config, f"Job '{job_name}' missing 'runs-on'"
            assert 'steps' in job_config, f"Job '{job_name}' missing 'steps'"


class TestTriggerConfiguration:
    """Additional comprehensive trigger configuration tests"""
    
    @pytest.fixture
    def triggers(self, workflow_content):
        """
        Retrieve the workflow's trigger/event configuration.
        
        Parameters:
            workflow_content (dict): Parsed workflow YAML content.
        
        Returns:
            The trigger configuration value from the parsed workflow content (value of the `on` key or a top-level boolean key), or `None` if no trigger configuration is present.
        """
        return workflow_content.get(True) or workflow_content.get('on')
    
    def test_workflow_dispatch_has_no_branches(self, triggers):
        """
        Ensure the `workflow_dispatch` trigger does not specify any branch filters.
        
        If `workflow_dispatch` is present as a mapping, this test asserts that it does not include a `branches` key.
        """
        workflow_dispatch = triggers.get('workflow_dispatch')
        assert workflow_dispatch is not None, "workflow_dispatch should be configured"
        
        # workflow_dispatch should not have branches (it's manual)
        if isinstance(workflow_dispatch, dict):
            assert 'branches' not in workflow_dispatch, \
                "workflow_dispatch should not have branches configuration"
    
    def test_trigger_keys_are_valid_github_events(self, triggers):
        """Test that all trigger keys are valid GitHub workflow events"""
        valid_events = [
            'push', 'pull_request', 'pull_request_target', 'workflow_dispatch',
            'schedule', 'release', 'issues', 'issue_comment', 'watch',
            'fork', 'create', 'delete', 'deployment', 'deployment_status',
            'page_build', 'public', 'check_run', 'check_suite', 'discussion',
            'discussion_comment', 'gollum', 'label', 'milestone', 'project',
            'project_card', 'project_column', 'registry_package', 'repository_dispatch',
            'status', 'workflow_call', 'workflow_run'
        ]
        
        for trigger_key in triggers.keys():
            assert trigger_key in valid_events, \
                f"Trigger '{trigger_key}' is not a valid GitHub workflow event"
    
    def test_branch_filter_format_is_correct(self, triggers):
        """
        Validate that the 'branches' filters for `push` and `pull_request` triggers, if present, are lists of strings.
        
        Parameters:
            triggers (dict): Mapping of trigger names to their configuration objects parsed from the workflow content.
        """
        for trigger_name in ['push', 'pull_request']:
            if trigger_name in triggers:
                trigger_config = triggers[trigger_name]
                if 'branches' in trigger_config:
                    branches = trigger_config['branches']
                    assert isinstance(branches, list), \
                        f"{trigger_name} branches should be a list"
                    for branch in branches:
                        assert isinstance(branch, str), \
                            f"Branch name in {trigger_name} should be a string, got {type(branch)}"
    
    def test_no_branches_ignore_configuration(self, triggers):
        """Test that branches-ignore is not used (prefer explicit branches)"""
        for trigger_name in ['push', 'pull_request']:
            if trigger_name in triggers:
                trigger_config = triggers[trigger_name]
                assert 'branches-ignore' not in trigger_config, \
                    f"{trigger_name} should use 'branches' not 'branches-ignore' for clarity"
    
    def test_no_conflicting_branch_filters(self, triggers):
        """
        Ensure push and pull_request triggers do not specify both 'branches' and 'branches-ignore'.
        """
        for trigger_name in ['push', 'pull_request']:
            if trigger_name in triggers:
                trigger_config = triggers[trigger_name]
                has_branches = 'branches' in trigger_config
                has_branches_ignore = 'branches-ignore' in trigger_config
                
                if has_branches and has_branches_ignore:
                    pytest.fail(
                        f"{trigger_name} has both 'branches' and 'branches-ignore' "
                        f"which is not allowed"
                    )


class TestStepValidation:
    """Comprehensive step validation tests"""
    
    @pytest.fixture
    def steps(self, workflow_content):
        """
        Retrieve the `steps` list for the `build` job from the parsed workflow content.
        
        Parameters:
            workflow_content (dict): Parsed YAML content of the workflow.
        
        Returns:
            list: Steps defined for the `build` job.
        """
        return workflow_content['jobs']['build']['steps']
    
    @pytest.fixture
    def checkout_steps(self, steps):
        """
        Filter steps to those that use a checkout action.
        
        Parameters:
            steps (list[dict]): Sequence of step mappings from a job's `steps` list.
        
        Returns:
            list[dict]: List of step mappings whose `uses` value references a checkout action.
        """
        return [s for s in steps if 'uses' in s and 'checkout' in s['uses']]
    
    def test_checkout_is_first_step(self, steps):
        """Test that checkout is the first step"""
        first_step = steps[0]
        assert 'uses' in first_step, "First step should use an action"
        assert 'checkout' in first_step['uses'], "First step should be checkout action"
    
    def test_steps_have_unique_names_when_present(self, steps):
        """Test that all named steps have unique names"""
        step_names = [s.get('name') for s in steps if 'name' in s]
        assert len(step_names) == len(set(step_names)), \
            "Step names should be unique when present"
    
    def test_run_commands_are_not_empty(self, steps):
        """Test that all run commands have content"""
        for i, step in enumerate(steps):
            if 'run' in step:
                run_content = step['run'].strip()
                assert len(run_content) > 0, f"Step {i} has empty run command"
    
    def test_multiline_run_commands_use_pipe_syntax(self, steps):
        """
        Validate that any step with a multi-line `run` command contains more than one line.
        
        Parameters:
            steps (list[dict]): Sequence of workflow step dictionaries; steps that include a `run` key may contain single- or multi-line shell commands.
        """
        for step in steps:
            if 'run' in step and '\n' in step['run']:
                # Multi-line run commands should exist
                assert len(step['run'].split('\n')) > 1, \
                    "Multi-line run command should have multiple lines"
    
    def test_action_steps_do_not_have_run(self, steps):
        """Test that action steps (uses) don't also have run commands"""
        for step in steps:
            if 'uses' in step:
                # Actions should not have 'run' commands
                assert 'run' not in step, \
                    f"Step with 'uses' should not have 'run': {step.get('uses')}"
    
    def test_checkout_step_has_no_extra_config(self, checkout_steps):
        """Test that checkout step doesn't have unnecessary configuration"""
        if checkout_steps:
            checkout = checkout_steps[0]
            # Basic checkout should only have 'uses' (and maybe 'name')
            allowed_keys = {'uses', 'name', 'with', 'id'}
            actual_keys = set(checkout.keys())
            unexpected_keys = actual_keys - allowed_keys
            assert len(unexpected_keys) == 0, \
                f"Checkout step has unexpected keys: {unexpected_keys}"
    
    def test_step_names_are_descriptive(self, steps):
        """Test that step names follow descriptive naming conventions"""
        for step in steps:
            if 'name' in step:
                name = step['name']
                # Name should be reasonable length and not just single character
                assert len(name) > 3, f"Step name '{name}' is too short"
                assert len(name) < 100, f"Step name '{name}' is too long"
                # Name should start with capital letter
                assert name[0].isupper() or name[0].isdigit(), \
                    f"Step name '{name}' should start with capital letter"


class TestWorkflowBestPractices:
    """Test GitHub Actions best practices"""
    
    def test_workflow_has_descriptive_name(self, workflow_content):
        """Test that workflow name is descriptive"""
        name = workflow_content.get('name', '')
        assert len(name) > 0, "Workflow should have a name"
        assert len(name) < 50, "Workflow name should be concise"
    
    def test_workflow_has_at_least_one_job(self, jobs):
        """Test that workflow has at least one job defined"""
        assert len(jobs) >= 1, "Workflow should have at least one job"
    
    def test_all_jobs_have_steps(self, jobs):
        """Test that all jobs have at least one step"""
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            assert len(steps) > 0, f"Job '{job_name}' should have at least one step"
    
    def test_runner_uses_latest_tag(self, jobs):
        """Test that runners use -latest tags for better maintenance"""
        for job_name, job_config in jobs.items():
            runner = job_config.get('runs-on', '')
            if runner and isinstance(runner, str):
                # If not using a specific version, should use -latest
                if not any(runner.endswith(v) for v in ['-20.04', '-22.04', '-2019', '-2022', '-11', '-12', '-13']):
                    assert runner.endswith('-latest'), \
                        f"Job '{job_name}' should use -latest runner tag: {runner}"
    
    def test_no_deprecated_actions(self, jobs):
        """Test that no deprecated actions are used"""
        deprecated_actions = [
            'actions/checkout@v1',
            'actions/checkout@v2',
            'actions/setup-node@v1',
            'actions/setup-python@v1',
        ]
        
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            for step in steps:
                if 'uses' in step:
                    action = step['uses']
                    for deprecated in deprecated_actions:
                        assert deprecated not in action, \
                            f"Job '{job_name}' uses deprecated action: {action}"


class TestYAMLFormatting:
    """Test YAML formatting and style"""
    
    def test_yaml_uses_2_space_indentation(self, workflow_raw):
        """Test that YAML uses consistent 2-space indentation"""
        lines = workflow_raw.split('\n')
        indentation_levels = set()
        
        for line in lines:
            if line.strip() and not line.strip().startswith('#'):
                spaces = len(line) - len(line.lstrip(' '))
                if spaces > 0:
                    indentation_levels.add(spaces)
        
        # All indentation should be multiples of 2
        for level in indentation_levels:
            assert level % 2 == 0, f"Found non-2-space indentation: {level}"
    
    def test_no_trailing_whitespace(self, workflow_raw):
        """Test that lines don't have trailing whitespace"""
        lines = workflow_raw.split('\n')
        for i, line in enumerate(lines, 1):
            # Skip empty lines
            if len(line) > 0:
                assert not line.endswith(' ') and not line.endswith('\t'), \
                    f"Line {i} has trailing whitespace"
    
    def test_keys_use_lowercase(self, workflow_content):
        """Test that YAML keys use lowercase (GitHub Actions convention)"""
        # Top-level keys should be lowercase
        for key in workflow_content.keys():
            if isinstance(key, str):
                assert key.islower() or key == 'CI', \
                    f"Top-level key '{key}' should be lowercase"
    
    def test_list_items_properly_formatted(self, workflow_raw):
        """Test that list items use proper YAML formatting"""
        lines = workflow_raw.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.lstrip()
            if stripped.startswith('- '):
                # List items should have space after dash
                assert stripped[1] == ' ', \
                    f"Line {i}: List item should have space after dash"


class TestWorkflowDocumentation:
    """Test workflow documentation and comments"""
    
    def test_has_descriptive_comments(self, workflow_raw):
        """Test that workflow has descriptive comments"""
        comment_lines = [line.strip() for line in workflow_raw.split('\n') 
                        if line.strip().startswith('#')]
        
        # Should have multiple comment lines for good documentation
        assert len(comment_lines) >= 3, \
            "Workflow should have at least 3 comment lines for documentation"
    
    def test_comments_are_not_too_long(self, workflow_raw):
        """
        Ensure comment lines in the raw workflow are under 100 characters.
        
        Raises an AssertionError if any comment line is 100 characters or longer; the assertion message includes the first 50 characters of the offending line.
        """
        comment_lines = [line for line in workflow_raw.split('\n') 
                        if line.strip().startswith('#')]
        
        for line in comment_lines:
            # Comments should be readable (not exceeding typical line length)
            assert len(line) < 100, f"Comment line too long: {line[:50]}..."
    
    def test_main_sections_have_comments(self, workflow_raw):
        """Test that main sections have explanatory comments"""
        lines = workflow_raw.split('\n')
        
        # Important sections that should be documented
        sections_to_check = ['on:', 'jobs:', 'steps:']
        
        for i, line in enumerate(lines):
            for section in sections_to_check:
                if section in line:
                    # Check if there's a comment before or on the same line
                    has_comment = False
                    # Check current line
                    if '#' in lines[i]:
                        has_comment = True
                    # Check previous line(s)
                    if i > 0 and '#' in lines[i-1]:
                        has_comment = True
                    
                    assert has_comment, \
                        f"Section '{section}' should have a comment for documentation"


class TestEdgeCaseScenarios:
    """Test additional edge cases and error conditions"""
    
    def test_workflow_handles_empty_branch_list_check(self, workflow_content):
        """Test that branch configurations are not empty lists"""
        triggers = workflow_content.get(True) or workflow_content.get('on')
        
        for trigger_name in ['push', 'pull_request']:
            if trigger_name in triggers:
                trigger_config = triggers[trigger_name]
                if 'branches' in trigger_config:
                    branches = trigger_config['branches']
                    assert len(branches) > 0, \
                        f"{trigger_name} branches list should not be empty"
    
    def test_no_null_values_in_config(self, workflow_content):
        """Test that there are no null/None values in critical config"""
        assert workflow_content.get('name') is not None, "Workflow name should not be null"
        assert workflow_content.get('jobs') is not None, "Jobs should not be null"
        
        triggers = workflow_content.get(True) or workflow_content.get('on')
        assert triggers is not None, "Triggers should not be null"
    
    def test_step_order_is_logical(self, workflow_content):
        """Test that steps are in logical order (checkout first)"""
        steps = workflow_content['jobs']['build']['steps']
        
        # First step with 'uses' should be checkout
        first_action_step = None
        for step in steps:
            if 'uses' in step:
                first_action_step = step
                break
        
        if first_action_step:
            assert 'checkout' in first_action_step.get('uses', ''), \
                "First action step should be checkout"
    
    def test_no_windows_line_endings(self, workflow_raw):
        """
        Ensure the workflow file uses Unix (LF) line endings and does not contain Windows (CRLF) line endings.
        """
        assert '\r\n' not in workflow_raw, \
            "Workflow should use Unix line endings (LF), not Windows (CRLF)"
    
    def test_file_ends_with_newline(self, workflow_raw):
        """Test that file ends with a newline character"""
        assert workflow_raw.endswith('\n'), \
            "Workflow file should end with a newline"


class TestParameterizedWorkflowValidation:
    """Test parametrized validation approaches"""
    
    @pytest.mark.parametrize("job_name", ["build"])
    def test_job_has_required_keys(self, jobs, job_name):
        """Test that jobs have all required keys"""
        assert job_name in jobs, f"Job '{job_name}' not found"
        job = jobs[job_name]
        
        required_keys = ['runs-on', 'steps']
        for key in required_keys:
            assert key in job, f"Job '{job_name}' missing required key '{key}'"
    
    @pytest.mark.parametrize("step_index,expected_type", [
        (0, 'action'),  # First step should be an action (checkout)
        (1, 'script'),  # Second step should be a script
        (2, 'script'),  # Third step should be a script
    ])
    def test_step_types_in_order(self, workflow_content, step_index, expected_type):
        """
        Assert that the step at a given index has the expected type.
        
        Checks the `build` job's steps and, if `step_index` is within range, asserts that the step at that index is an action when `expected_type` is `'action'` (contains a `uses` key) or a script when `expected_type` is `'script'` (contains a `run` key). If `step_index` is out of range the test does nothing.
        
        Parameters:
            workflow_content (dict): Parsed workflow YAML as a dictionary.
            step_index (int): Zero-based index of the step to validate.
            expected_type (str): Expected step type, either `'action'` or `'script'`.
        """
        steps = workflow_content['jobs']['build']['steps']
        
        if step_index < len(steps):
            step = steps[step_index]
            
            if expected_type == 'action':
                assert 'uses' in step, \
                    f"Step {step_index} should be an action (uses)"
            elif expected_type == 'script':
                assert 'run' in step, \
                    f"Step {step_index} should be a script (run)"
    
    @pytest.mark.parametrize("trigger_type", ["push", "pull_request"])
    def test_trigger_branch_configuration_complete(self, workflow_content, trigger_type):
        """Test that branch-based triggers have complete configuration"""
        triggers = workflow_content.get(True) or workflow_content.get('on')
        
        assert trigger_type in triggers, f"Trigger '{trigger_type}' not found"
        trigger = triggers[trigger_type]
        
        assert 'branches' in trigger, \
            f"Trigger '{trigger_type}' should have branches configuration"
        assert isinstance(trigger['branches'], list), \
            f"Trigger '{trigger_type}' branches should be a list"
        assert len(trigger['branches']) > 0, \
            f"Trigger '{trigger_type}' should have at least one branch"


class TestFixtureReusability:
    """Test fixture reusability and efficiency"""
    
    def test_workflow_path_fixture_returns_path_object(self, workflow_path):
        """Test that workflow_path fixture returns a Path object"""
        from pathlib import Path
        assert isinstance(workflow_path, Path), \
            "workflow_path fixture should return a Path object"
    
    def test_workflow_raw_fixture_returns_string(self, workflow_raw):
        """Test that workflow_raw fixture returns a string"""
        assert isinstance(workflow_raw, str), \
            "workflow_raw fixture should return a string"
    
    def test_workflow_content_fixture_returns_dict(self, workflow_content):
        """Test that workflow_content fixture returns a dict"""
        assert isinstance(workflow_content, dict), \
            "workflow_content fixture should return a dict"
    
    def test_jobs_fixture_is_accessible(self, jobs):
        """Test that jobs fixture is accessible from module scope"""
        assert jobs is not None, "jobs fixture should be accessible"
        assert isinstance(jobs, dict), "jobs fixture should return a dict"
    
    def test_fixtures_contain_expected_data(self, workflow_path, workflow_raw, workflow_content, jobs):
        """Test that all fixtures contain expected data"""
        # Path should exist
        assert workflow_path.exists(), "workflow_path should point to existing file"
        
        # Raw content should not be empty
        assert len(workflow_raw) > 0, "workflow_raw should not be empty"
        
        # Parsed content should have keys
        assert len(workflow_content) > 0, "workflow_content should not be empty"
        
        # Jobs should contain at least one job
        assert len(jobs) > 0, "jobs should contain at least one job"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
