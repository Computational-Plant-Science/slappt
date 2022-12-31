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

## Inputs

`slappt` is convenient not only for one-off container jobs, but for mapping a workflow over a list of inputs. This is accomplished with [job arrays]() and can be configured via the `--inputs` options.

**Note:** your job's parallelism remains limited by the number of nodes allocated to it by the scheduler. To run containers in parallel, you must request multiple nodes.

<!--
By default, `slappt` uses Slurm [job arrays](https://slurm.schedmd.com/job_array.html) to submit containers in parallel. An alternative mechanism is the [TACC `launcher`](https://github.com/TACC/launcher).

To use the `launcher` instead of job arrays, add the `--parallelism launcher` option. This option is required on some TACC systems (e.g. [Stampede2](https://www.tacc.utexas.edu/systems/stampede2)) where job arrays are not available.
-->

The `--inputs` option's value must be the path to a text file containing a list of inputs, one on each line. This can be useful for parameter sweeps or to process a collection of files.

For instance, say we have some files:

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
       --partition batch \
       --entrypoint "cat \$SLAPPT_INPUT" \
       --inputs inputs.txt > job.sh
```

This will generate a script to spawn a container, reading the input from the `SLAPPT_INPUT` environment variable.

It can be then submitted with, for instance:

```shell
sbatch --array=1-2 job.sh
```

## Submissions

`slappt` can also submit jobs to a local or remote Slurm cluster via the `--submit` option. For instance, if you've cloned this repository to a cluster filesystem, standard Slurm commands (e.g. `sbatch`) are available:

```shell
slappt example/hello.yaml --submit
```

If successfully submitted, the job ID will be shown.

To submit to a remote cluster, use the `--host` and `--username` options, as well as the optional `--password` for password authentication, or `--pkey` to provide a path to a private key file.

**Note**: `sshlurm` is not compatible with multi-factor authentication.

Say you have a set of parameters:

```shell
1
2
3
```

Assuming you're on a Slurm cluster with permission to submit to the `batch` partition, you can generate and submit a parameter sweep job script with:

```shell
slappt --image docker://alpine \
       --shell sh \
       --partition batch \
       --entrypoint "echo $SLAPPT_INPUT" \
       --inputs inputs.txt  \
       --submit
```

You can also submit to a remote cluster. For instance, assuming you have key authentication set up, and your private key is the default location/name `~/.ssh/id_rsa`:

```shell
slappt --image docker://alpine \
       --shell sh \
       --partition batch \
       --entrypoint "echo $SLAPPT_INPUT" \
       --inputs inputs.txt \
       --submit \
       --host <your cluster IP or FQDN> \
       --username <your username>
```

The `--password` or `--pkey` options can be used to provide a password or a private key file, respectively.
