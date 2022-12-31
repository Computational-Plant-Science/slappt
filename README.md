<div align="center">
<br/>
<img src="slappt.png" style="position:relative;width:250px;" />

[Slurm](https://slurm.schedmd.com/overview.html) scripts for [Apptainer](http://apptainer.org) jobs

[![PyPI Version](https://img.shields.io/pypi/v/slappt.png)](https://pypi.python.org/pypi/slappt)
[![PyPI Status](https://img.shields.io/pypi/status/slappt.png)](https://pypi.python.org/pypi/slappt)
[![PyPI Versions](https://img.shields.io/pypi/pyversions/slappt.png)](https://pypi.python.org/pypi/slappt)

[![CI](https://github.com/Computational-Plant-Science/slappt/actions/workflows/ci.yml/badge.svg)](https://github.com/Computational-Plant-Science/slappt/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/slappt/badge/?version=latest)](https://slappt.readthedocs.io/en/latest/?badge=latest)

</div>

## Contents

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quickstart](#quickstart)
  - [Caveats](#caveats)
    - [Shell selection](#shell-selection)
    - [Singularity support](#singularity-support)
    - [Pre-commands](#pre-commands)
- [Documentation](#documentation)
- [Disclaimer](#disclaimer)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Overview

`slappt` generates and submits Slurm job scripts for [Apptainer](https://apptainer.org/docs/user/main/) workflows. Jobs can be configured in YAML or via CLI.


## Requirements

`slappt` requires Python3.8+ and a few core dependencies, including `click`, `pyaml`, `paramiko`, and `requests`, among others.

To submit a job script, the host machine must either run `slurmctld` with standard commands available, or must be able to connect via key- or password-authenticated SSH to the target cluster.

## Installation

`slappt` is [available on the Python Package Index](https://pypi.org/project/slappt/) and can be installed with `pip`:

```shell
pip install slappt
```

## Quickstart

Say you have access to a Slurm cluster with `apptainer` installed, and you have permission to submit to the `batch` partition.

Copy the `hello.yaml` file from the `examples` directory to your current working directory, then run:

```shell
slappt hello.yaml > job.sh
```

Alternatively, without the configuration file:

```shell
slappt --image docker://alpine \
       --shell sh \
       --partition batch \
       --entrypoint "echo 'hello world'" > hello.sh
```

Your `hello.sh` script should now contain:

```shell
#!/bin/bash
#SBATCH --job-name=0477f4b9-e119-4354-8384-f50d7a96adad
#SBATCH --output=slappt.0477f4b9-e119-4354-8384-f50d7a96adad.%j.out
#SBATCH --error=slappt.0477f4b9-e119-4354-8384-f50d7a96adad.%j.err
#SBATCH --partition=batch
#SBATCH -c 1
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --time=01:00:00
#SBATCH --mem=1GB
apptainer exec docker://alpine sh -c "echo 'hello world'"
```

If already on the cluster, use the `--submit` flag to submit the job directly. (Standard Slurm commands must be available for this to work.) In this case the job ID is shown if submission was successful.

You can provide authentication information to submit the script to remote clusters over SSH. For instance, assuming you have key authentication set up and your key is `~/.ssh/id_rsa`:

```shell
slappt ... --host <cluster IP or FQDN> --username <username>
```

### Caveats

There are a few things to note about the example above.

#### Shell selection

For most image definitions, specifying the `shell` is likely not necessary, as the default is `bash`. However, for images that don't have `bash` installed (e.g., `alphine` only has `sh`) a different shell must be selected.

#### Singularity support

If your cluster still uses `singularity`, pass the `--singularity` flag (or set the `singularity` key in the configuration file to `true`) to substitute `singularity` for `apptainer` in the command wrapping your workflow entrypoint.

#### Pre-commands

**Note:** if `apptainer` or `singularity` are not available by default on your cluster's compute nodes, you may need to add `--pre` commands (or a `pre` section to the configuration file), for instance `--pre "module load apptainer"`, or:

```yaml
...
pre:
  - module load apptainer
...
```

## Documentation

Documentation is available at [slappt.readthedocs.io](https://slappt.readthedocs.io/en/latest/).

<!--

## Related

There is a companion repository [`slappt-action`](https://github.com/Computational-Plant-Science/slappt-action) for easy integration with GitHub Actions.

-->

## Disclaimer

This project is not affiliated with Slurm, Apptainer or Singularity and cannot guarantee compatibility with all cluster configurations.