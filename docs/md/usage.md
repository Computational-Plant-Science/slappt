# Usage

To show CLI usage help run `slappt --help`. To show the current version run `slappt --version` (short form `-v`).

At minimum, `slappt` needs to know a few things before it can generate and/or submit a job script:

- `image`: the Docker image to use (e.g. `docker://ubuntu:latest` &mdash; note the `docker://` prefix is required, as support for other registries is in development)
- `partition`: the Slurm partition to submit the job to
- `entrypoint`: the command to run inside the container

## Interactive usage

To generate and/or submit a job script interactively, just run `slappt`. 

## Programmatic usage

Parameters may be provided as CLI options or in a YAML configuration file. 

For instance, to submit a job specified in `hello.yaml` to a SLURM scheduler on the local machine, your configuration file should something look:

```yaml
image: docker://alpine
shell: sh
partition: batch
entrypoint: echo "hello world"
```

By default, `slappt` assumes the host machine is part of a Slurm cluster. To submit this job to a local Slurm cluster, just run `slappt hello.yaml`. By default, the job will run in the current working directory. (To specify a different directory, use the `--workdir` option.) If the job was submitted successfully, its ID will be printed to `stdout`.

Equivalently, using only CLI arguments (no configuration file):

```shell
slappt --image docker://alpine \
       --shell sh \
       --partition batch \
       --entrypoint "echo 'hello world'"
```

## Remote submissions

To submit to a remote cluster, you will need password or key access. A `--host`, `--username` and `--password` may be provided on the command line, or a `--pkey` may be provided to specify a private key. If a `--username` is provided without a password, `slappt` will check for an SSH key called `id_rsa` in the default location (on Unix systems, `~/.ssh/id_rsa`, on Windows `C:\%APPDATA%\SSH\UserKeys`).

This is a good opportunity to mention that YAML configuration and CLI options can be mixed. For instance, to use a private key in the default location:

```shell
slappt hello.yaml --host hostname --user username
```

By default, connections are opened on port 22. To use a different port, use the `--port` option. (Alternatively, use equivalently named attributes in a YAML configuration file.)