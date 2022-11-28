from os import environ
from platform import system

import pytest


def is_in_ci():
    # if running in GitHub Actions CI, "CI" variable always set to true
    # https://docs.github.com/en/actions/learn-github-actions/environment-variables#default-environment-variables
    return bool(environ.get("CI", None))


def requires_platform(platform, ci_only=False):
    return pytest.mark.skipif(
        system().lower() != platform.lower() and (is_in_ci() if ci_only else True),
        reason=f"only compatible with platform: {platform.lower()}",
    )


def excludes_platform(platform, ci_only=False):
    return pytest.mark.skipif(
        system().lower() == platform.lower() and (is_in_ci() if ci_only else True),
        reason=f"not compatible with platform: {platform.lower()}",
    )


def pytest_addoption(parser):
    parser.addoption(
        "-S",
        "--smoke",
        action="store_true",
        default=False,
        help="Run only smoke tests (should complete in <1 minute)."
    )


def pytest_runtest_setup(item):
    smoke = item.config.getoption("--smoke")
    slow = list(item.iter_markers(name="slow"))
    if smoke and slow:
        pytest.skip()
