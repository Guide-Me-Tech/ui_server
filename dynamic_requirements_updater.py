#!/usr/bin/env python3
import os
import subprocess
import logging
import sys
from typing import Dict, Optional

"""
Why this code is needed:
- Automatically detects, updates, and merges Python dependencies in requirements.txt using pipreqs.
- Preserves pinned versions, removes stale packages, and tries to resolve version conflicts automatically.
- Deep logging and environment-driven behavior, no manual intervention needed.
- Flexible and robust: tries multiple strategies to fix conflicts if they occur.

Key Steps:
1. Ensure pipreqs is installed.
2. Run pipreqs to generate a temporary requirements file based on the codebase.
3. Parse old and new requirements, merge them.
4. Attempt to write merged requirements and check if installation works.
5. If conflicts appear, attempt multiple conflict resolution strategies:
   - Remove strict pins (==) one by one and re-test.
   - Remove pins from other operators (>=, <=, ~=, !=) similarly.
   - Try removing all pins of a certain operator at once.
   - Remove all pins if nothing else works.
6. Once stable, rewrite final requirements.txt.
7. Log everything at DEBUG level for troubleshooting, INFO for normal operations.

Set LOG_LEVEL=DEBUG for step-by-step tracing.
Default LOG_LEVEL=INFO for cleaner output.

Save resources by stopping early if a solution is found, and only making network calls if needed.
"""

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="[%(asctime)s][%(levelname)s]: %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


def ensure_pipreqs_installed() -> bool:
    """
    Janis Rubins step 1: Ensure pipreqs is installed.
    If not found, try `pip install pipreqs`.
    If still fail, log and return False.
    """
    logger.debug("Checking if pipreqs is installed.")
    try:
        import pipreqs  # noqa: F401

        logger.debug("pipreqs already installed.")
        return True
    except ImportError:
        logger.info("pipreqs not found, attempting to install it now...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pipreqs"])
            import pipreqs  # noqa: F401

            logger.debug("pipreqs installation successful.")
            return True
        except Exception as e:
            logger.error(f"Failed to install pipreqs automatically: {e}", exc_info=True)
            return False


def run_pipreqs(output_file: str) -> bool:
    """
    Janis Rubins step 2: Run pipreqs to detect dependencies.
    Returns True if successful, False otherwise.
    """
    logger.debug("Running pipreqs to detect requirements from code.")
    try:
        subprocess.check_call(["pipreqs", ".", "--force", "--savepath", output_file])
        logger.debug("pipreqs run successfully. Temporary requirements generated.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"pipreqs failed with error: {e}", exc_info=True)
        return False


def parse_requirements(file_path: str) -> Dict[str, str]:
    """
    Janis Rubins step 3: Parse requirements into {package: version_string}.
    'requests==2.25.1' -> {"requests": "==2.25.1"}
    No pin: {"requests": ""}
    """
    reqs = {}
    if not os.path.exists(file_path):
        logger.debug(f"No file at {file_path}, returning empty dict.")
        return reqs
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            operators = ["==", ">=", "<=", "~=", "!="]
            version_info = ""
            package = line
            for op in operators:
                if op in line:
                    parts = line.split(op, 1)
                    package = parts[0].strip()
                    version_info = op + parts[1].strip()
                    break
            reqs[package.lower()] = version_info
    logger.debug(f"Parsed {file_path}: {reqs}")
    return reqs


def merge_requirements(
    old_reqs: Dict[str, str], new_reqs: Dict[str, str]
) -> Dict[str, str]:
    """
    Janis Rubins step 4: Merge new_reqs with old pinned versions.
    - If old has pinned version, keep it.
    - If package not in new_reqs, remove it.
    """
    merged = {}
    for pkg, ver in new_reqs.items():
        old_ver = old_reqs.get(pkg, "")
        if old_ver:
            merged[pkg] = old_ver
        else:
            merged[pkg] = ver
    logger.debug(f"Merged requirements: {merged}")
    return merged


def try_install_requirements(reqs: Dict[str, str]) -> bool:
    """
    Janis Rubins step 5: Test installing given reqs to check for conflicts.
    This is a mock implementation. In a real scenario:
    - Write reqs to a temp file
    - Run `pip install -r temp_file` in a subprocess
    - Check exit code
    For now, return False to simulate a conflict scenario.

    Replace with real logic as needed.
    """
    logger.debug("Mock: Checking installation of current requirements (fake logic).")
    # TODO: Implement real installation check logic here.
    # For demonstration, return False to show conflict resolution attempts.
    return False


def write_requirements(file_path: str, reqs: Dict[str, str]) -> None:
    """
    Janis Rubins step 6: Write final requirements sorted by package name.
    """
    with open(file_path, "w") as f:
        for pkg in sorted(reqs.keys()):
            line = pkg
            if reqs[pkg]:
                line += reqs[pkg]
            f.write(line + "\n")
    logger.debug(f"Updated {file_path} with merged requirements: {reqs}")


def attempt_conflict_resolution(merged: Dict[str, str]) -> Dict[str, str]:
    """
    Janis Rubins step 7: Attempt conflict resolution if direct installation fails.
    Strategy (enhanced and robust):
    - Try removing pins operator by operator, one by one.
    - Try removing all pins of a certain operator at once.
    - Finally try removing all pins.
    - Return updated dict if success, else return original if no success.
    """

    logger.debug("Attempting conflict resolution by adjusting pinned versions.")
    operators_priority = ["==", ">=", "<=", "~=", "!="]

    def test_and_return(
        test_reqs: Dict[str, str], msg: str
    ) -> Optional[Dict[str, str]]:
        logger.debug(msg)
        if try_install_requirements(test_reqs):
            logger.info("Conflict resolved: " + msg)
            return test_reqs
        else:
            logger.debug("Attempt failed: " + msg)
            return None

    def try_unpin_packages(
        current_reqs: Dict[str, str], operator: str, all_at_once: bool = False
    ) -> Optional[Dict[str, str]]:
        pkgs_with_op = [p for p, v in current_reqs.items() if operator in v]
        if not pkgs_with_op:
            logger.debug(f"No packages pinned with {operator}, skipping.")
            return None

        if all_at_once:
            # Remove operator pin from all packages with this operator
            test_reqs = dict(current_reqs)
            for pkg in pkgs_with_op:
                logger.debug(f"Removing {operator} pin from {pkg} simultaneously.")
                test_reqs[pkg] = ""
            return test_and_return(test_reqs, f"Removing all {operator} pins at once.")
        else:
            # One by one
            for pkg in pkgs_with_op:
                test_reqs = dict(current_reqs)
                logger.debug(f"Trying to remove {operator} pin from {pkg}.")
                test_reqs[pkg] = ""
                result = test_and_return(
                    test_reqs, f"Removing {operator} pin from {pkg}"
                )
                if result is not None:
                    return result
            return None

    current = dict(merged)

    # Step 1: Try removing pins operator by operator, one by one
    for op in operators_priority:
        logger.debug(f"Removing {op} pins one by one.")
        result = try_unpin_packages(current, op, all_at_once=False)
        if result is not None:
            return result
        else:
            logger.debug(f"No success removing {op} pins one by one.")

    # Step 2: Removing all pins of each operator at once
    for op in operators_priority:
        logger.debug(f"Removing all {op} pins at once.")
        result = try_unpin_packages(current, op, all_at_once=True)
        if result is not None:
            return result
        else:
            logger.debug(f"No success removing all {op} pins at once.")

    # Step 3: Remove all pins from all packages
    logger.debug("Attempting to remove all pins from all packages.")
    all_unpinned = {p: "" for p in current}
    if try_install_requirements(all_unpinned):
        logger.info("Conflict resolved by removing all pins from all packages.")
        return all_unpinned
    else:
        logger.debug("Removing all pins from all packages did not resolve conflicts.")

    # Step 4: If still fail, log final error
    logger.error("Failed to resolve conflicts even after multiple strategies.")
    return merged


def main():
    logger.debug("Starting dynamic requirements update process.")
    if not ensure_pipreqs_installed():
        logger.error("Could not install or verify pipreqs. Exiting.")
        sys.exit(1)

    temp_req_file = ".temp_requirements.txt"

    if not run_pipreqs(temp_req_file):
        logger.error("pipreqs failed, cannot update requirements.")
        if os.path.exists(temp_req_file):
            os.remove(temp_req_file)
        sys.exit(1)

    old_reqs = parse_requirements("requirements.txt")
    new_reqs = parse_requirements(temp_req_file)
    merged = merge_requirements(old_reqs, new_reqs)

    # Try installing merged directly
    if try_install_requirements(merged):
        logger.info("Requirements installed successfully with no conflicts.")
        write_requirements("requirements.txt", merged)
        os.remove(temp_req_file)
        sys.exit(0)
    else:
        logger.warning("Conflicts detected, attempting automatic resolution.")
        resolved = attempt_conflict_resolution(merged)
        if resolved != merged:
            # If resolved differs, try again to confirm installation
            if try_install_requirements(resolved):
                logger.info("Conflicts resolved successfully!")
                write_requirements("requirements.txt", resolved)
                if os.path.exists(temp_req_file):
                    os.remove(temp_req_file)
                sys.exit(0)
            else:
                logger.error("Installation still failed after resolution attempts.")
                if os.path.exists(temp_req_file):
                    os.remove(temp_req_file)
                sys.exit(1)
        else:
            logger.error("No resolution found, exiting.")
            if os.path.exists(temp_req_file):
                os.remove(temp_req_file)
            sys.exit(1)


if __name__ == "__main__":
    main()
