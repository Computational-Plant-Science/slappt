# `sshlurm`

There is an extra `sshlurm` command to submit scripts to remote clusters over SSH. 

## Usage

Assuming you're on a Unix machine with key authentication set up for your target cluster, and your private key is `~/.ssh/id_rsa`:

```shell
shhlurm <script> --host <cluster's IP or FQDN> --username <username>
```

If successfully submitted, the job ID will be shown.

Use the `--password` option for password authentication, and the `--pkey` option to provide a path to a private key file.

**Note**: `sshlurm` is not compatible with multi-factor authentication.

## Usage with `slappt`

The `sshlurm` command pairs especially nicely with `slappt` to submit jobs in parallel. It's smart enough to automatically handle job arrays and/or launcher scripts.

For instance, say you have a set of parameters:

```shell
1
2
3
```

Assuming you have key authentication set up:

```shell
slappt --image docker://alpine
       --shell sh
       --entrypoint "echo $SLAPPT_INPUT"
       --inputs inputs.txt > job.sh
sshlurm job.sh --host <your cluster IP or FQDN> --username <your username>
```

This will copy `inputs.txt` to the remote cluster, submit an array of jobs, each of which has an environment with `$SLAPPT_INPUT` set to one of the provided input values.
