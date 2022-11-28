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

The `sshlurm` command pairs nicely with `slappt`, for instance:

```shell
slappt config.yaml > job.sh
sshlurm job.sh --host <your cluster IP or FQDN> --username <your username>
```