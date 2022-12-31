# Quickstart

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
module load apptainer  # only if you need, some clusters
apptainer exec docker://alpine sh -c "echo 'hello world'"
```

If already on the cluster, use the `--submit` flag to submit the job directly. (Standard Slurm commands must be available for this to work.) In this case the job ID is shown if submission was successful.

You can provide authentication information to submit the script to remote clusters over SSH. For instance, assuming you have key authentication set up and your key is `~/.ssh/id_rsa`:

```shell
slappt ... --host <cluster IP or FQDN> --username <username>
```

## Caveats

There are a few things to note about the example above.

### Shell

For most image definitions, specifying the `shell` is likely not necessary, as the default is `bash`. However, for images that don't have `bash` installed (e.g., `alphine` only has `sh`) a different shell must be selected.

### Singularity support

If your cluster still uses `singularity`, pass the `--singularity` flag (or set the `singularity` key in the configuration file to `true`) to substitute `singularity` for `apptainer` in the command wrapping your workflow entrypoint.

### Pre-commands

**Note:** if `apptainer` or `singularity` are not available by default on your cluster's compute nodes, you may need to add `--pre` commands (or a `pre` section to the configuration file), for instance `--pre "module load apptainer"`, or:

```yaml
pre:
  - module load apptainer
```