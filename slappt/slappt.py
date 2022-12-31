import uuid
from os import linesep
from pathlib import Path

import click
import yaml

import slappt
from slappt.models import Parallelism, Shell, SlapptConfig
from slappt.scripts import ScriptGenerator


def generate_script(config: SlapptConfig):
    generator = ScriptGenerator(config)
    return generator.gen_job_script()


@click.group(invoke_without_command=True)
@click.pass_context
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
@click.option("--iterations", required=False)
@click.option(
    "--parallelism",
    required=False,
    type=click.Choice(["jobarray", "launcher"], case_sensitive=False),
)
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
@click.option("--singularity", required=False, type=bool, default=False)
def cli(
    ctx,
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
    iterations,
    parallelism,
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
):
    if ctx.invoked_subcommand:
        return

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
            iterations=iterations,
            parallelism=Parallelism[parallelism.lower()]
            if parallelism
            else Parallelism.JOBARRAY,
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
        )

    script = generate_script(config)
    click.echo(linesep.join(script))
