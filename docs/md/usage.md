# Usage

At minimum, `slappt` needs to know a few things before it can generate and/or submit a job script:

- `image`: the Docker image to use (e.g. `docker://ubuntu:latest` &mdash; note the `docker://` prefix is required, as support for other registries is in development)
- `partition`: the Slurm partition to submit the job to
- `entrypoint`: the command to run inside the container

## Interactive use

To generate and/or submit a job script interactively, just run `slappt`. 

## Programmatic use

Parameters may be provided as CLI options or in a YAML configuration file. 

### Configuration file

To make job configurations reusable, `slappt` supports a [YAML specification](spec.md) format.

To create a script for a job specified in `hello.yaml` (see for instance [`examples/hello.yaml`](https://github.com/Computational-Plant-Science/slappt/blob/develop/examples/hello.yaml)), run:

```shell
slappt hello.yaml
```

### CLI options

Equivalently, using CLI arguments instead of a configuration file:

```shell
slappt --image docker://alpine \
       --shell sh \
       --partition batch \
       --entrypoint "echo 'hello world'"
```

## Introspection

To show CLI usage help run `slappt --help`.

To show the current version run `slappt --version` (short form `-v`).

## Parallelism

`slappt` is convenient not only for one-off container jobs, but for running copies of a workflow in parallel, or mapping a workflow over a list of inputs. These use cases are accomplished with the `--iterations` and the `--inputs` options, respectively, as well as the `--parallelism` option to control the strategy.

**Note:** your job remains limited by the number of nodes allocated to it by the scheduler. To run containers in parallel, you must request multiple nodes.

### Strategy

By default, `slappt` uses Slurm [job arrays](https://slurm.schedmd.com/job_array.html) to submit containers in parallel. An alternative mechanism is the [TACC `launcher`](https://github.com/TACC/launcher).

To use the `launcher` instead of job arrays, add the `--parallelism launcher` option. This option is required on some TACC systems (e.g. [Stampede2](https://www.tacc.utexas.edu/systems/stampede2)) where job arrays are not available.

### Iterations

To run identical copies of a container, use the `--iterations` option. For example, to 10 copies, use `--iterations 10`. The container will be run with the same parameters each time, but the `SLAPPT_ITERATION` environment variable will be set to the iteration number (starting at 1).

### Mapping over inputs

To map a container workflow over a set of inputs, use the `--inputs` option, whose value must be the path to a text file containing a list of inputs, one on each line. This can be useful for parameter sweeps or to process a collection of files.

For instance, to process a set of images in parallel, you could create a file `images.txt` containing the paths to the images, one per line:

```text
img1.png
img2.png
```

You could then show the size of each image with:

```shell
slappt --image docker://alpine \
       --shell sh \
       --partition batch \
       --entrypoint "stat -c %s $SLAPPT_INPUT" \
       --inputs images.txt


