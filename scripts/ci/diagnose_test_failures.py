#!/usr/bin/env python3
"""
Script to diagnose common test failures in the backend.
This script analyzes test failure outputs and provides diagnostic information.
"""

import os
import re
import sys
import json
import glob
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Define common failure patterns and their likely causes
FAILURE_PATTERNS = {
    r"ImportError: No module named '(\w+)'": "Missing dependency: {0}",
    r"AssertionError: assert (.*) == (.*)": "Assertion failed: expected {1}, got {0}",
    r"TypeError: (.*) takes (\d+) positional argument but (\d+) were given": "Function signature mismatch: {0}",
    r"AttributeError: '(\w+)' object has no attribute '(\w+)'": "Missing attribute: {1} in {0} object",
    r"KeyError: '(\w+)'": "Missing key: {0}",
    r"ValueError: (.*)": "Value error: {0}",
    r"RuntimeError: (.*)": "Runtime error: {0}",
    r"PermissionError: (.*)": "Permission error: {0}",
    r"FileNotFoundError: (.*)": "File not found: {0}",
    r"IndentationError: (.*)": "Indentation error: {0}",
    r"SyntaxError: (.*)": "Syntax error: {0}",
    r"ModuleNotFoundError: No module named '(\w+)'": "Module not found: {0}",
    r"ConnectionError: (.*)": "Connection error: {0}",
    r"TimeoutError: (.*)": "Timeout error: {0}",
}

def find_test_output_files() -> List[Path]:
    """Find test output files in the current directory and subdirectories."""
    # Look for pytest output files or other test output files
    output_files = []
    for pattern in ["pytest-*.xml", "test-output-*.txt", "test-results-*.xml"]:
        output_files.extend(glob.glob(f"**/{pattern}", recursive=True))
    
    return [Path(file) for file in output_files]

def parse_test_output(file_path: Path) -> List[Dict]:
    """Parse test output file and extract failure information."""
    failures = []
    
    # Check file extension to determine parsing method
    if file_path.suffix == ".xml":
        # Parse XML output (e.g., JUnit format)
        import xml.etree.ElementTree as ET
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Look for failure elements
            for test_case in root.findall(".//testcase"):
                failure = test_case.find("failure")
                if failure is not None:
                    failures.append({
                        "test_name": test_case.get("name"),
                        "test_class": test_case.get("classname"),
                        "message": failure.get("message"),
                        "traceback": failure.text
                    })
        except Exception as e:
            print(f"Error parsing XML file {file_path}: {e}")
    else:
        # Parse text output
        try:
            with open(file_path, "r") as f:
                content = f.read()
                
            # Look for test failure patterns in text output
            # This is a simplified example and may need to be adapted for your specific output format
            test_blocks = re.split(r"={70,}", content)
            for block in test_blocks:
                if "FAILED" in block:
                    test_name_match = re.search(r"FAILED (\w+::\w+::\w+)", block)
                    test_name = test_name_match.group(1) if test_name_match else "Unknown"
                    
                    traceback_match = re.search(r"Traceback.*?(?=\n\n|\Z)", block, re.DOTALL)
                    traceback = traceback_match.group(0) if traceback_match else ""
                    
                    failures.append({
                        "test_name": test_name,
                        "test_class": test_name.split("::")[0] if "::" in test_name else "",
                        "message": "",
                        "traceback": traceback
                    })
        except Exception as e:
            print(f"Error parsing text file {file_path}: {e}")
    
    return failures

def diagnose_failure(failure: Dict) -> Tuple[str, Optional[str]]:
    """Diagnose the cause of a test failure and suggest a fix."""
    traceback = failure.get("traceback", "")
    message = failure.get("message", "")
    
    # Check for known failure patterns
    for pattern, diagnosis_template in FAILURE_PATTERNS.items():
        match = re.search(pattern, traceback + " " + message)
        if match:
            groups = match.groups()
            diagnosis = diagnosis_template.format(*groups)
            
            # Suggest a fix based on the diagnosis
            fix = suggest_fix(diagnosis, pattern, groups)
            return diagnosis, fix
    
    # If no known pattern is found
    return "Unknown failure cause", None

def suggest_fix(diagnosis: str, pattern: str, groups: Tuple) -> Optional[str]:
    """Suggest a fix based on the diagnosis."""
    if "Missing dependency" in diagnosis:
        return f"Run: pip install {groups[0]}"
    
    elif "Missing module" in diagnosis or "Module not found" in diagnosis:
        return f"Run: pip install {groups[0]}"
    
    elif "Assertion failed" in diagnosis:
        return "Check the expected and actual values in the test"
    
    elif "Function signature mismatch" in diagnosis:
        return "Check the function signature and the number of arguments"
    
    elif "Missing attribute" in diagnosis:
        return f"Check if the attribute '{groups[1]}' exists in the '{groups[0]}' class"
    
    elif "Missing key" in diagnosis:
        return f"Ensure the key '{groups[0]}' exists in the dictionary"
    
    elif "File not found" in diagnosis:
        return "Check if the file exists and the path is correct"
    
    elif "Indentation error" in diagnosis or "Syntax error" in diagnosis:
        return "Fix the syntax in the indicated file"
    
    elif "Connection error" in diagnosis:
        return "Check network connectivity and service availability"
    
    elif "Timeout error" in diagnosis:
        return "Increase timeout value or optimize the operation"
    
    return None

def check_for_common_issues() -> List[Dict]:
    """Check for common issues in the codebase that might cause test failures."""
    issues = []
    
    # Check for missing __init__.py files in test directories
    test_dirs = glob.glob("**/tests", recursive=True)
    for test_dir in test_dirs:
        if not os.path.exists(os.path.join(test_dir, "__init__.py")):
            issues.append({
                "type": "missing_init",
                "location": test_dir,
                "description": "Missing __init__.py in test directory",
                "fix": f"Create an empty __init__.py file in {test_dir}"
            })
    
    # Check for inconsistent environment variables
    env_files = glob.glob("**/.env*", recursive=True)
    required_vars = set()
    for env_file in env_files:
        try:
            with open(env_file, "r") as f:
                for line in f:
                    if line.strip() and not line.strip().startswith("#"):
                        var_name = line.split("=")[0].strip()
                        required_vars.add(var_name)
        except Exception:
            pass
    
    for var in required_vars:
        if var not in os.environ:
            issues.append({
                "type": "missing_env_var",
                "location": "environment",
                "description": f"Missing environment variable: {var}",
                "fix": f"Set the {var} environment variable"
            })
    
    # Check for common database connection issues
    try:
        import psycopg2
        try:
            conn = psycopg2.connect(
                dbname=os.environ.get("POSTGRES_DB", "test_db"),
                user=os.environ.get("POSTGRES_USER", "postgres"),
                password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
                host=os.environ.get("POSTGRES_HOST", "localhost"),
                port=os.environ.get("POSTGRES_PORT", "5432")
            )
            conn.close()
        except Exception as e:
            issues.append({
                "type": "db_connection",
                "location": "database",
                "description": f"Database connection issue: {str(e)}",
                "fix": "Check database credentials and connection settings"
            })
    except ImportError:
        pass
    
    return issues

def main():
    """Main function to diagnose test failures."""
    print("Diagnosing test failures...")
    
    # Find test output files
    output_files = find_test_output_files()
    if not output_files:
        print("No test output files found.")
        
        # Check if we can run pytest to generate output
        try:
            subprocess.run(
                ["pytest", "--collect-only"],
                cwd="backend",
                check=False,
                capture_output=True,
                text=True
            )
            print("Pytest is available. You can run tests to generate output files.")
        except FileNotFoundError:
            print("Pytest not found. Make sure it's installed.")
        
        # Check for common issues anyway
        issues = check_for_common_issues()
        if issues:
            print("\nFound potential issues:")
            for issue in issues:
                print(f"- {issue['description']}")
                print(f"  Fix: {issue['fix']}")
        
        return
    
    # Parse test output files and diagnose failures
    all_failures = []
    for file_path in output_files:
        print(f"Analyzing {file_path}...")
        failures = parse_test_output(file_path)
        all_failures.extend(failures)
    
    if not all_failures:
        print("No test failures found in output files.")
        return
    
    # Diagnose each failure
    print(f"\nFound {len(all_failures)} test failures:")
    for i, failure in enumerate(all_failures, 1):
        test_name = failure.get("test_name", "Unknown test")
        test_class = failure.get("test_class", "")
        
        print(f"\n{i}. Test: {test_name} ({test_class})")
        
        diagnosis, fix = diagnose_failure(failure)
        print(f"   Diagnosis: {diagnosis}")
        
        if fix:
            print(f"   Suggested fix: {fix}")
        else:
            print("   No automatic fix available. Manual investigation required.")
    
    # Check for common issues
    issues = check_for_common_issues()
    if issues:
        print("\nAdditional potential issues:")
        for issue in issues:
            print(f"- {issue['description']}")
            print(f"  Fix: {issue['fix']}")
    
    # Write diagnostic report to file
    report = {
        "failures": all_failures,
        "diagnoses": [{"test": f.get("test_name"), "diagnosis": diagnose_failure(f)[0], "fix": diagnose_failure(f)[1]} for f in all_failures],
        "issues": issues
    }
    
    with open("test_diagnosis_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\nDiagnostic report written to test_diagnosis_report.json")

if __name__ == "__main__":
    main() 