# YAML Specification

`slappt` supports declarative YAML configuration to make container workflows reusable.

```yaml
# standard attributes
image:          # the container image definition to use, e.g. docker://alpine (registry prefix is required)
shell:          # the shell to use (default: bash)
partition:      # the cluster partition to submit to
entrypoint:     # the command to run inside the container
workdir:        # the working directory to use 
email:          # the email address to send notifications to
name:           # the name of the job (default: slappt.<guid>)
inputs:         # a text file containing a newline-separated list of input files
environment:    # a dictionary of environment variables to set
bind_mounts:    # a list of bind mounts to use, in format <host path>:<container path>
no_cache:       # don't use the apptainer/singularity cache, force a rebuild of the image (default: false)
gpus:           # the number of GPUs to request 
time:           # the job's walltime
account:        # the account name to associate the job with
mem:            # the amount of memory to request (default: 1GB)
nodes:          # the number of nodes to request (default: 1)
cores:          # the number of cores to request (default: 1)
tasks:          # the number of tasks to request (default: 1)
header_skip:    # a list of header lines to skip when parsing the input file (can be useful e.g. for clusters which have virtual memory and reject --mem headers)
singularity:    # whether to invoke singularity instead of apptainer (default: false)
# submission attributes
host:           # the hostname, IP or FQDN of the remote cluster to submit to
port:           # the port to use for the SSH connection (default: 22)
username:       # the username to use for the SSH connection
password:       # the password to use for SSH authentication
pkey:           # the path to the private key to use for SSH authentication
allow_stderr:   # don't raise an error if sshlurm encounters stderr output (default: false)
timeout:        # the timeout for the SSH connection (default: 10)
```