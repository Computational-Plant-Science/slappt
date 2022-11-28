# Quickstart

Say you're on a Slurm cluster with an active Python3.8+ environment and permission to submit to the `batch` partition. First make sure `slappt` is installed:

```shell
pip install slappt
```

Then we're off to the races:

```shell
slappt --image docker://alpine \
       --shell sh \
       --partition batch \
       --entrypoint "echo 'hello world'"
```

**Note:** for most image definitions, specifying the `shell` is likely not necessary &mdash; the default is `bash`. However, for images that don't have `bash` installed (`alphine` only has `sh`) you'll need to specify a different shell.

