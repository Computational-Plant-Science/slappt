# Developing `slappt`

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Requirements](#requirements)
- [Installation](#installation)
- [Linting](#linting)
- [Testing](#testing)
  - [Environment variables](#environment-variables)
  - [Test markers](#test-markers)
  - [Smoke tests](#smoke-tests)
- [Releases](#releases)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Requirements

Python 3.8+ is required to develop `slappt`.

## Installation

First, clone the repo with `git clone https://github.com/Computational-Plant-Science/slappt.git`.

Create a Python3 virtual environment, e.g. `python -m venv venv`, then install `slappt` and core dependencies with `pip install .`. Install testing and linting dependencies as well with `pip install ".[test]".

## Linting

To lint Python source files, run `python scripts/lint.py`. This will run `black` and `isort` on all files in the `slappt` directory.

## Testing

This project's tests are contained within the top-level source directory `slappt`. The tests can be run from the project root with `pytest` (or `python -m pytest`). Use `-v` for verbose mode and `-n auto` to run tests in parallel on as many cores as your machine will spare.

### Environment variables

The tests require some environment variables:

- `CLUSTER_HOST`
- `CLUSTER_USER`
- `CLUSTER_PASSWORD`
- `CLUSTER_KEY_PATH`
- `CLUSTER_HOME_DIR`
- `CLUSTER_PARTITION`

You can set these manually or put them in a `.env` file in the project root &mdash; `pytest-dotenv` will detect them in the latter case. 

**Note:** to run the full test suite, you must have key access to the cluster, and the cluster's login node must have standard Slurm commands (e.g. `sbatch`) available on the path.

*Jump proxy support is in development*.

### Test markers

A `slow` marker is provided for tests that take more than a few seconds to run.

### Smoke tests

Fast tests (i.e., those selected by `pytest -m "not slow"`) can be run with `pytest -S` (short for `--smoke`). The smoke tests should complete in under a minute.

## Releases

To create a `slappt` release candidate, create a branch from the tip of `develop` named `vX.Y.Zrc`, where `X.Y.Z` is the [semantic version](https://semver.org/) number. The `release.yml` CI workflow to build and test the release candidate, then draft a PR into `master`. To promote the candidate to an official release, merge the PR into `master`. This will trigger a final CI job to tag the release revision to `master`, rebase `master` on `develop`, publish the release to PyPI, and post the release notes to GitHub.