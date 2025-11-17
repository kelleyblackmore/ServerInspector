"""
File checker module for serverinspector.

This module provides simple functions to check file-related aspects of a system.
"""

import logging
import os
import re

logger = logging.getLogger("serverinspector")


def check(params):
    """
    Perform a file check with the given parameters.

    Args:
        params (dict): Check parameters, including:
            - path: Path to the file to check
            - exists: Whether the file should exist
            - type: Type of file (file, directory, symlink)
            - contains: Text that should be contained in the file
            - content_pattern: Regex pattern to match in the file
            - permissions: File permissions (octal, e.g. "644")
            - owner: File owner
            - group: File group

    Returns:
        dict: Check result with success/failure and details
    """
    result = {"success": False, "message": "", "details": {}}

    # Required parameters
    if "path" not in params:
        result["message"] = "Missing required parameter: path"
        return result

    path = params["path"]
    result["details"]["path"] = path

    # Check if the file exists
    file_exists = os.path.exists(path)
    result["details"]["exists"] = file_exists

    # Check the existence requirement
    if "exists" in params:
        expected_exists = params["exists"]
        result["details"]["expected_exists"] = expected_exists

        if file_exists != expected_exists:
            if expected_exists:
                result["message"] = f"File '{path}' does not exist"
            else:
                result["message"] = f"File '{path}' exists but should not"
            return result

    # If we're expecting the file to not exist and it doesn't, we're done
    if "exists" in params and not params["exists"] and not file_exists:
        result["success"] = True
        result["message"] = f"File '{path}' does not exist as expected"
        return result

    # Only do the following checks if the file exists
    if file_exists:
        # Check file type
        if "type" in params:
            expected_type = params["type"]
            result["details"]["expected_type"] = expected_type

            # Get file type
            actual_type = "unknown"
            if os.path.isfile(path):
                actual_type = "file"
            elif os.path.isdir(path):
                actual_type = "directory"
            elif os.path.islink(path):
                actual_type = "symlink"

            result["details"]["actual_type"] = actual_type

            if actual_type != expected_type:
                result["message"] = (
                    f"File '{path}' is a '{actual_type}' but should be a '{expected_type}'"
                )
                return result

        # Get file type for other checks
        file_type = (
            "file"
            if os.path.isfile(path)
            else "directory" if os.path.isdir(path) else "other"
        )
        result["details"]["type"] = file_type

        # Check content if required
        if "contains" in params and file_type == "file":
            expected_content = params["contains"]
            try:
                with open(path, "r") as f:
                    content = f.read()
                has_content = expected_content in content
                result["details"]["has_content"] = has_content
                if not has_content:
                    result["message"] = (
                        f"File '{path}' does not contain '{expected_content}'"
                    )
                    return result
            except Exception as e:
                result["message"] = f"Error reading file '{path}': {str(e)}"
                return result

        # Check content pattern if required
        if "content_pattern" in params and file_type == "file":
            pattern = params["content_pattern"]
            try:
                with open(path, "r") as f:
                    content = f.read()
                pattern_match = bool(re.search(pattern, content))
                result["details"]["pattern_match"] = pattern_match
                if not pattern_match:
                    result["message"] = (
                        f"File '{path}' does not match pattern '{pattern}'"
                    )
                    return result
            except Exception as e:
                result["message"] = f"Error reading file '{path}': {str(e)}"
                return result

        # Check file permissions
        if "permissions" in params:
            expected_perms = params["permissions"]
            result["details"]["expected_permissions"] = expected_perms

            try:
                # Get the actual permissions
                actual_perms = oct(os.stat(path).st_mode)[-3:]
                result["details"]["actual_permissions"] = actual_perms

                if actual_perms != expected_perms:
                    result["message"] = (
                        f"File '{path}' has permissions {actual_perms}, expected {expected_perms}"
                    )
                    return result
            except Exception as e:
                result["message"] = f"Error checking file permissions: {str(e)}"
                return result

        # Check file owner
        if "owner" in params:
            import pwd

            expected_owner = params["owner"]
            result["details"]["expected_owner"] = expected_owner

            try:
                # Get the actual owner
                owner_uid = os.stat(path).st_uid
                try:
                    actual_owner = pwd.getpwuid(owner_uid).pw_name
                except KeyError:
                    actual_owner = str(
                        owner_uid
                    )  # Fallback to UID if name not available

                result["details"]["actual_owner"] = actual_owner

                if actual_owner != expected_owner:
                    result["message"] = (
                        f"File '{path}' owned by {actual_owner}, expected {expected_owner}"
                    )
                    return result
            except Exception as e:
                result["message"] = f"Error checking file owner: {str(e)}"
                return result

        # Check file group
        if "group" in params:
            import grp

            expected_group = params["group"]
            result["details"]["expected_group"] = expected_group

            try:
                # Get the actual group
                group_gid = os.stat(path).st_gid
                try:
                    actual_group = grp.getgrgid(group_gid).gr_name
                except KeyError:
                    actual_group = str(
                        group_gid
                    )  # Fallback to GID if name not available

                result["details"]["actual_group"] = actual_group

                if actual_group != expected_group:
                    result["message"] = (
                        f"File '{path}' has group {actual_group}, expected {expected_group}"
                    )
                    return result
            except Exception as e:
                result["message"] = f"Error checking file group: {str(e)}"
                return result

        # All checks passed
        result["success"] = True
        result["message"] = f"File '{path}' passed all checks"

    return result


def run(_runner, test_config):
    """
    Run a file test (legacy API for backward compatibility).

    Args:
        _runner: A runner instance (unused, kept for API compatibility)
        test_config (dict): Test configuration

    Returns:
        dict: Test result in the old format
    """
    # Convert parameters to the new format
    params = {"path": test_config.get("path")}

    # Set the expected type based on the test type
    test_type = test_config.get("type", "file")
    if test_type in ["directory", "symlink"]:
        params["type"] = test_type

    # Copy other parameters
    if "exists" in test_config:
        params["exists"] = test_config["exists"]
    if "type" in test_config:
        params["type"] = test_config["type"]
    if "content" in test_config:
        params["contains"] = test_config["content"]
    if "content_pattern" in test_config:
        params["content_pattern"] = test_config["content_pattern"]
    if "permissions" in test_config:
        params["permissions"] = test_config["permissions"]
    if "owner" in test_config:
        params["owner"] = test_config["owner"]
    if "group" in test_config:
        params["group"] = test_config["group"]

    # Run the check
    result = check(params)

    # Convert the result back to the old format
    old_result = {
        "name": test_config.get("name", "Unnamed file test"),
        "type": test_type,
        "result": result["success"],
        "details": result["details"],
    }

    # Add error message if check failed
    if not result["success"]:
        old_result["details"]["error"] = result["message"]

    return old_result
