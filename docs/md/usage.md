# Usage

## Introspection

To show CLI usage help run `slappt --help`.

To show the current version run `slappt --version` (short form `-v`).

## Basics

At minimum, `slappt` needs to know a few things before it can generate and/or submit a job script:

- `image`: the Docker image to use (e.g. `docker://ubuntu:latest` &mdash; note the `docker://` prefix is required &mdash; support for other registries is still in development)
- `partition`: the Slurm partition to submit the job to
- `entrypoint`: the command to run inside the container

To generate and/or submit a job script interactively, just run `slappt`. Parameters may also be provided as CLI options, or in a YAML configuration file. Config files are useful if the same workflow configurations is often reused &mdash; see the [YAML specification](spec.md) for more details

To create a script for a job specified in `hello.yaml` (see for instance [`examples/hello.yaml`](https://github.com/Computational-Plant-Science/slappt/blob/develop/examples/hello.yaml)), run:

```shell
slappt hello.yaml
```

Equivalently, using CLI arguments instead of a configuration file:

```shell
slappt --image docker://alpine \
       --shell sh \
       --partition batch \
       --entrypoint "echo 'hello world'"
```

## Parallelism

`slappt` is convenient not only for one-off container jobs, but for running multiple copies of a workflow in parallel (e.g. for Monte Carlo simulations), or mapping a workflow over a list of inputs. These use cases are accomplished with job arrays and can be configured via the `--iterations` and the `--inputs` options.

**Note:** your job remains limited by the number of nodes allocated to it by the scheduler. To run containers in parallel, you must request multiple nodes.

<!--
By default, `slappt` uses Slurm [job arrays](https://slurm.schedmd.com/job_array.html) to submit containers in parallel. An alternative mechanism is the [TACC `launcher`](https://github.com/TACC/launcher).

To use the `launcher` instead of job arrays, add the `--parallelism launcher` option. This option is required on some TACC systems (e.g. [Stampede2](https://www.tacc.utexas.edu/systems/stampede2)) where job arrays are not available.
-->

### Iterations

To run identical copies of a container, use the `--iterations` option. For example, to run 10 copies, use `--iterations 10`. The container will be run with the same parameters each time, with the `SLAPPT_ITERATION` environment variable set to the iteration number (starting at 1).

### Inputs

To map a container workflow over a set of inputs, use the `--inputs` option, whose value must be the path to a text file containing a list of inputs, one on each line. This can be useful for parameter sweeps or to process a collection of files.

For instance, say we have some files we want to process in parallel:

```shell
$ cat f1
> hello 1
$ cat f2
> hello 2
```

We can create a file `inputs.txt`:

```text
f1.txt
f2.txt
```

Assuming we have permission to submit to the `batch` partition, we can generate a script with:

```shell

```shell
slappt --image docker://alpine \
       --shell sh \
       --nodes 2 \
       --partition batch \
       --entrypoint "cat \$SLAPPT_INPUT" \
       --inputs inputs.txt
```

This script will request 2 nodes, spawning a container on each with the `SLAPPT_INPUT` environment variable set one of the input files.
