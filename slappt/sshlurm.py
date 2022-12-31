from os.path import join
from pathlib import Path
from warnings import warn

import click

from slappt.exceptions import ExitStatusException
from slappt.models import Parallelism, SlapptConfig
from slappt.ssh import SSH
from slappt.utils import clean_html, parse_job_id

SLURM_RUNNING_STATES = [
    "CF",
    "CONFIGURING",
    "PD",
    "PENDING",
    "R",
    "RUNNING",
    "RD",
    "RESV_DEL_HOLD",
    "RF",
    "REQUEUE_FED",
    "RH",
    "REQUEUE_HOLD",
    "RQ",
    "REQUEUED",
    "RS",
    "RESIZING",
    "SI",
    "SIGNALING",
    "SO",
    "STAGE_OUT",
    "S",
    "SUSPENDED",
    "ST",
    "STOPPED",
]

SLURM_SUCCESS_STATES = [
    "CG",
    "COMPLETING",
    "CD",
    "COMPLETED",
]

SLURM_CANCELLED_STATES = ["CA", "CANCELLED", "RV", "REVOKED"]

SLURM_TIMEOUT_STATES = ["DL", "DEADLINE", "TO", "TIMEOUT"]

SLURM_FAILURE_STATES = [
    "BF",
    "BOOT_FAIL",
    "F",
    "FAILED",
    "NF",
    "NODE_FAIL",
    "OOM",
    "OUT_OF_MEMORY",
    "PR",
    "PREEMPTED",
]


def is_success(status):
    return status in SLURM_SUCCESS_STATES


def is_failure(status):
    return status in SLURM_FAILURE_STATES


def is_timeout(status):
    return status in SLURM_TIMEOUT_STATES


def is_cancelled(status):
    return status in SLURM_CANCELLED_STATES


def is_complete(status):
    return (
        is_success(status)
        or is_failure(status)
        or is_timeout(status)
        or is_cancelled(status)
    )


def get_client(config: SlapptConfig) -> SSH:
    if config.password:
        return SSH(
            host=config.host,
            port=config.port,
            username=config.username,
            password=config.password,
            timeout=config.timeout,
        )
    else:
        return SSH(
            host=config.host,
            port=config.port,
            username=config.username,
            pkey=config.pkey,
            timeout=config.timeout,
        )


def submit_script(config: SlapptConfig, verbose: bool = False) -> str:
    with get_client(config) as client:

        # copy files to the remote host
        with client.open_sftp() as sftp:

            # expand the working directory
            workdir = config.workdir if config.workdir else "~"

            # make sure the remote workdir exists
            try:
                sftp.mkdir(workdir)
            except:
                warn(f"Working directory {workdir} already exists")

            num_inputs = 0
            if config.inputs:
                # copy inputs file
                remote_path = join(workdir, Path(config.inputs).name)
                with Path(config.inputs).open("r") as local_file, sftp.file(
                    remote_path, "w"
                ) as remote_file:
                    lines = local_file.readlines()
                    num_inputs = len(lines)
                    for line in lines:
                        remote_file.write(f"{line}\n".encode("utf-8"))
                    remote_file.seek(0)
                    print(
                        f"Uploaded inputs file {remote_path} for {config.name}"
                    )

            # copy job script
            remote_path = join(workdir, Path(config.file).name)
            with Path(config.file).open("r") as local_file, sftp.file(
                remote_path, "w"
            ) as remote_file:
                for line in local_file.readlines():
                    remote_file.write(f"{line}\n".encode("utf-8"))
                remote_file.seek(0)
                print(f"Uploaded job script {remote_path} for {config.name}")

        # submit the job
        # TODO: support TACC launcher instead of job arrays
        if config.inputs:
            command = f"sbatch --array=1-{num_inputs}"
        elif config.iterations:
            command = f"sbatch --array=1-{config.iterations}"
        else:
            command = f"sbatch {Path(config.file).name}"

        if verbose:
            print(f"Submitting '{config.file}' to '{config.host}'")
        stdin, stdout, stderr = client.exec_command(
            f"bash --login -c '{command}'", get_pty=True
        )
        stdin.close()

        def read_stdout():
            for line in iter(lambda: stdout.readline(2048), ""):
                clean = clean_html(line).strip()
                if verbose:
                    print(f"Received stdout from '{config.host}': '{clean}'")
                yield clean

        def read_stderr():
            for line in iter(lambda: stderr.readline(2048), ""):
                clean = clean_html(line).strip()
                if verbose:
                    print(f"Received stderr from '{config.host}': '{clean}'")
                yield clean

        output = [line for line in read_stdout()]
        errors = [line for line in read_stderr()]

        if stdout.channel.recv_exit_status() != 0:
            raise ExitStatusException(
                f"Received non-zero exit status from '{config.host}'"
            )
        elif not config.allow_stderr and len(errors) > 0:
            raise ExitStatusException(f"Received stderr: {errors}")

        # return the job id
        job_id = parse_job_id(output[-1])
        return job_id


# @click.group(invoke_without_command=True)
@click.command()
@click.argument("file", required=True)
@click.option("--host", required=False, type=str)
@click.option("--port", required=False, type=int, default=22)
@click.option("--workdir", required=False, type=str)
@click.option("--username", required=False, type=str)
@click.option("--password", required=False, type=str)
@click.option("--pkey", required=False, type=str, default="~/.ssh/id_rsa")
@click.option("--allow_stderr", required=False, type=bool, default=False)
@click.option("--timeout", required=False, type=int, default=15)
@click.option("--verbose", required=False, type=bool, default=False)
def cli(
    file,
    workdir,
    host,
    port,
    username,
    password,
    pkey,
    allow_stderr,
    timeout,
    verbose,
):
    config = SlapptConfig(
        file=file,
        workdir=workdir,
        host=host,
        port=port,
        username=username,
        password=password,
        pkey=pkey,
        allow_stderr=allow_stderr,
        timeout=timeout,
    )
    click.echo(submit_script(config, verbose))
