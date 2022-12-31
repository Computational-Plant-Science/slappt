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