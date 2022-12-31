import dataclasses
import logging
from datetime import timedelta
from math import ceil
from os import linesep
from typing import List, Optional, Tuple
from uuid import uuid4

from slappt import docker
from slappt.models import (  # Parallelism,
    BindMount,
    EnvironmentVariable,
    Shell,
    SlapptConfig,
)

SHEBANG = "#!/bin/bash"


class ScriptGenerator:
    def __init__(self, config: SlapptConfig):
        valid, validation_errors = ScriptGenerator.validate_config(config)
        if not valid:
            raise ValueError(f"Invalid config: {validation_errors}")

        self.config = config
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def validate_config(config: SlapptConfig) -> Tuple[bool, List[str]]:
        errors = []

        # check required attributes
        fields = dataclasses.fields(SlapptConfig)
        ftypes = {f.name: f.type for f in fields}
        missing = [
            f
            for f, t in ftypes.items()
            if getattr(config, f) is None and t != Optional[t]
        ]
        if len(missing) > 0:
            errors.append(f"Missing required fields: {', '.join(missing)}")

        # check image is on DockerHub
        image_owner, image_name, image_tag = docker.parse_image_components(
            config.image
        )
        if not docker.image_exists(
            image_name, owner=image_owner, tag=image_tag
        ):
            errors.append(f"Image {config.image} not found on Docker Hub")

        return len(errors) == 0, errors

    @staticmethod
    def get_job_time(config: SlapptConfig):
        if config.time is None:
            walltime = timedelta(hours=1)
        else:
            s = config.time.split(":")
            hours, minutes, seconds = int(s[0]), int(s[1]), int(s[2])
            walltime = timedelta(hours=hours, minutes=minutes, seconds=seconds)

        # round to nearest hour and convert to HH:mm:ss
        hours = ceil(walltime.total_seconds() / 60 / 60)
        hours = (
            "1" if hours == 0 else f"{hours}"
        )  # if we rounded down to zero, bump to 1
        if len(hours) == 1:
            hours = f"0{hours}"
        return f"{hours}:00:00"

    def gen_job_headers(self) -> List[str]:
        job_name = self.config.name or str(uuid4())
        headers = [f"#SBATCH --job-name={job_name}"]
        headers.append(f"#SBATCH --output=slappt.{job_name}.%j.out")
        headers.append(f"#SBATCH --error=slappt.{job_name}.%j.err")
        headers.append(f"#SBATCH --partition={self.config.partition}")
        headers.append(f"#SBATCH -c {int(self.config.cores)}")
        headers.append(f"#SBATCH -N {self.config.nodes}")
        headers.append(f"#SBATCH --ntasks={self.config.tasks}")
        headers.append(
            f"#SBATCH --time={ScriptGenerator.get_job_time(self.config)}"
        )

        if self.config.email:
            headers.append("#SBATCH --mail-type=END,FAIL")
            headers.append(f"#SBATCH --mail-user={self.config.email}")

        if self.config.account:
            headers.append(f"#SBATCH -A {self.config.account}")

        if self.config.gpus:
            headers.append(f"#SBATCH --gres=gpu:1")
        if (
            not self.config.header_skip
            or "--mem" not in self.config.header_skip
        ):
            headers.append(f"#SBATCH --mem={str(self.config.mem)}")

        self.logger.debug(f"Using run headers: {linesep.join(headers)}")
        return headers

    def gen_job_command(self) -> List[str]:
        commands = []

        if self.config.inputs:
            commands.append(
                f"SLAPPT_INPUT=$(head -n $SLURM_ARRAY_TASK_ID {self.config.inputs} | tail -1)"
            )

        commands = commands + ScriptGenerator.generate_invocation(
            work_dir=self.config.workdir,
            image=self.config.image,
            commands=self.config.entrypoint,
            env=self.config.environment,
            bind_mounts=self.config.bind_mounts,
            no_cache=self.config.no_cache,
            gpus=self.config.gpus,
            shell=self.config.shell,
            singularity=self.config.singularity,
        )

        self.logger.debug(f"Using run commands: {linesep.join(commands)}")
        return commands

    def gen_job_script(self) -> List[str]:
        headers = self.gen_job_headers()
        precmds = self.config.pre if self.config.pre else []
        command = self.gen_job_command()
        return [SHEBANG] + headers + precmds + command

    @staticmethod
    def generate_invocation(
        image: str,
        commands: str,
        work_dir: str = None,
        env: List[EnvironmentVariable] = None,
        bind_mounts: List[BindMount] = None,
        no_cache: bool = False,
        gpus: int = 0,
        shell: Shell = None,
        docker_username: str = None,
        docker_password: str = None,
        singularity: bool = False,
    ) -> List[str]:
        command = ""
        program = "singularity" if singularity else "apptainer"
        # prepend env vars
        if env is not None:
            if len(env) > 0:
                prefix = f"{program.upper()}ENV_"
                command += " ".join(
                    [
                        f"{prefix}{v['key'].upper().replace(' ', '_')}=\"{v['value']}\""
                        for v in env
                    ]
                )
                command += " "

        # command base
        command += f"{program} exec"

        # working directory (container home)
        if work_dir is not None:
            command += f" --home {work_dir}"

        # bind mounts
        if bind_mounts is not None and len(bind_mounts) > 0:
            command += " --bind " + ",".join([str(bm) for bm in bind_mounts])

        # whether to use the cache
        if no_cache:
            command += " --disable-cache"

        # whether to use GPUs (Nvidia)
        if gpus:
            command += " --nv"

        # shell selection
        if shell is None:
            shell = "sh"

        # construct the command
        command += f' {image} {shell.value if isinstance(shell, Shell) else shell} -c "{commands}"'

        # docker auth info
        if docker_username is not None and docker_password is not None:
            command = (
                f"{program.upper()}_DOCKER_USERNAME={docker_username} {program.upper()}_DOCKER_PASSWORD={docker_password} "
                + command
            )

        return [command]
