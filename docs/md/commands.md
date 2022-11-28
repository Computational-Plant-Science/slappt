# Commands

Besides the primary `slappt` command, which generates and submits scripts, two other commands are available:

- `compat`
- `script`

## Compat

`slappt compat` determines whether jobs can be submitted to a host system, affirming to `stdout` if the following conditions are met:

- SLURM is up and standard commands `sbatch`, `squeue`, `sacct`, etc are available
- `singularity` is installed and available on the path

Otherwise the command terminates with an error signal and information on the missing or misconfigured dependencies is printed to `stderr`.

By default, `slappt compat` tests the current host. To test a remote host, use the `--host`, `--user`, and optional `--port` options.

## Scripts

To generate a job script non-interactively without submitting it, use `slappt script <config file>.yml` (or with CLI options).