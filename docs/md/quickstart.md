# Quickstart

Say you have a Slurm cluster with `apptainer` installed, and you have permission to submit to the `batch` partition.

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

**Note:** for most image definitions, specifying the `shell` is likely not necessary, as the default is `bash`. However, for images that don't have `bash` installed (e.g., `alphine` only has `sh`) a different shell must be selected.

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

If already on the cluster, just submit it as usual:

```shell
sbatch hello.sh
```

If you're on a different machine, you can use the extra `sshlurm` command to submit the script over SSH. For instance, assuming you have key authentication set up for the cluster, and your key is `~/.ssh/id_rsa`:

```shell
sshlurm hello.sh --host <cluster IP or FQDN> --username <username>
```