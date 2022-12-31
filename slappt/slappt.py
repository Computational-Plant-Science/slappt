import uuid
from os import linesep
from os.path import join
from pathlib import Path
from subprocess import PIPE, Popen

import click
import yaml
from _warnings import warn

import slappt
from slappt.exceptions import ExitStatusException
from slappt.models import Shell, SlapptConfig
from slappt.scripts import ScriptGenerator
from slappt.ssh import SSH
from slappt.utils import clean_html, parse_job_id


def generate_script(config: SlapptConfig):
    generator = ScriptGenerator(config)
    return generator.gen_job_script()


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


def run_cmd(*args, verbose: bool = False, **kwargs):
    args = [str(g) for g in args]
    if verbose:
        print("running: " + " ".join(args))
    p = Popen(args, stdout=PIPE, stderr=PIPE, **kwargs)
    stdout, stderr = p.communicate()
    stdout = stdout.decode()
    stderr = stderr.decode()
    returncode = p.returncode
    if verbose:
        print(f"stdout:\n{stdout}")
        print(f"stderr:\n{stderr}")
        print(f"returncode: {returncode}")
    return returncode, stdout, stderr


def submit_script(config: SlapptConfig, verbose: bool = False) -> str:
    def read_stream(str, name="stdout"):
        for line in iter(lambda: str.readline(2048), ""):
            clean = clean_html(line).strip()
            if verbose:
                print(f"Received {name} from '{config.host}': '{clean}'")
            yield clean

    # compose the submission command, determining if we have inputs to map over
    input_lines = []
    if config.inputs:
        input_lines = Path(config.inputs).open("r").readlines()
        command = f"sbatch --array=1-{len(input_lines)}"
    else:
        command = f"sbatch {Path(config.file).name}"

    # copy files to the remote host
    if config.host:
        with get_client(config) as client:
            with client.open_sftp() as sftp:

                # set working directory and make sure it exists
                workdir = config.workdir if config.workdir else "~"
                try:
                    sftp.mkdir(workdir)
                except:
                    warn(f"Working directory {workdir} already exists")

                # copy inputs file if we have one
                if config.inputs:
                    remote_path = join(workdir, Path(config.inputs).name)
                    with sftp.file(remote_path, "w") as remote_file:
                        for line in input_lines:
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
                    print(
                        f"Uploaded job script {remote_path} for {config.name}"
                    )

            if verbose:
                print(f"Submitting '{config.file}' to '{config.host}'")

            stdin, stdout, stderr = client.exec_command(
                f"bash --login -c '{command}'", get_pty=True
            )
            stdin.close()

            if stdout.channel.recv_exit_status() != 0:
                raise ExitStatusException(
                    f"Received non-zero exit status from '{config.host}': {stdout + stderr}"
                )

            stdout = [line for line in read_stream(stdout, "stdout")]
            stderr = [line for line in read_stream(stderr, "stderr")]
    else:
        if verbose:
            print(f"Submitting '{config.file}'")

        returncode, stdout, stderr = run_cmd(command, verbse=verbose)

        if returncode != 0:
            raise ExitStatusException(
                f"Received non-zero exit status: {stdout + stderr}"
            )

    if not config.allow_stderr and len(stderr) > 0:
        raise ExitStatusException(f"Received stderr: {stderr}")

    # return the job id
    job_id = parse_job_id(stdout[-1])
    return job_id


@click.command()
@click.argument("file", required=False)
@click.option(
    "--version",
    "-v",
    required=False,
    is_flag=True,
    help="Show the version and exit.",
)
@click.option("--image", required=False)
@click.option("--partition", required=False)
@click.option("--entrypoint", required=False)
@click.option("--workdir", required=False)
@click.option("--email", required=False)
@click.option("--name", required=False)
@click.option(
    "--shell",
    required=False,
    type=click.Choice(["bash", "sh"], case_sensitive=False),
)
@click.option("--inputs", required=False)
# @click.option(
#     "--parallelism",
#     required=False,
#     type=click.Choice(["jobarray", "launcher"], case_sensitive=False),
# )
@click.option("--environment", required=False, multiple=True)
@click.option("--bind_mounts", required=False)
@click.option("--no_cache", required=False, default=False)
@click.option("--gpus", required=False, type=int, default=0)
@click.option("--time", required=False, default="01:00:00")
@click.option("--project", required=False)
@click.option("--mem", required=False, default="1GB")
@click.option("--nodes", required=False, type=int, default=1)
@click.option("--cores", required=False, type=int, default=1)
@click.option("--tasks", required=False, type=int, default=1)
@click.option("--header_skip", required=False)
@click.option("--singularity", is_flag=True, default=False)
@click.option("--submit", is_flag=True, default=False)
@click.option("--host", required=False, type=str)
@click.option("--port", required=False, type=int, default=22)
@click.option("--username", required=False, type=str)
@click.option("--password", required=False, type=str)
@click.option("--pkey", required=False, type=str, default="~/.ssh/id_rsa")
@click.option("--allow_stderr", required=False, type=bool, default=False)
@click.option("--timeout", required=False, type=int, default=15)
@click.option("--verbose", is_flag=True, default=False)
def cli(
    file,
    version,
    image,
    partition,
    entrypoint,
    workdir,
    email,
    name,
    shell,
    inputs,
    # parallelism,
    environment,
    bind_mounts,
    no_cache,
    gpus,
    time,
    project,
    mem,
    nodes,
    cores,
    tasks,
    header_skip,
    singularity,
    submit,
    host,
    port,
    username,
    password,
    pkey,
    allow_stderr,
    timeout,
    verbose,
):
    if version:
        click.echo(slappt.__version__)
        return

    if file:
        if not Path(file).is_file():
            raise ValueError(f"Invalid path to configuration file: {file}")

        with open(file, "r") as f:
            yml = yaml.safe_load(f)
            config = SlapptConfig(**yml)
    else:
        config = SlapptConfig(
            image=image,
            partition=partition,
            entrypoint=entrypoint,
            workdir=workdir,
            email=email,
            name=name if name else str(uuid.uuid4()),
            shell=Shell(shell),
            inputs=inputs,
            # parallelism=Parallelism[parallelism.lower()]
            # if parallelism
            # else Parallelism.JOBARRAY,
            environment=environment,
            bind_mounts=bind_mounts,
            no_cache=no_cache,
            gpus=gpus,
            time=time,
            account=project,
            mem=mem,
            nodes=nodes,
            cores=cores,
            tasks=tasks,
            header_skip=header_skip,
            singularity=singularity,
            host=host,
            port=port,
            username=username,
            password=password,
            pkey=pkey,
            allow_stderr=allow_stderr,
            timeout=timeout,
        )

    script = generate_script(config)

    if submit:
        click.echo(submit_script(config, verbose))
    else:
        click.echo(linesep.join(script))
