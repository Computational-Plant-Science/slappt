from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from pprint import pformat
from typing import List, Optional


class Shell(Enum):
    BASH = "bash"
    ZSH = "zsh"
    SH = "sh"


class Parallelism(Enum):
    JOBARRAY = "jobarray"
    LAUNCHER = "launcher"


@dataclass
class BindMount:
    host_path: str
    container_path: str

    def __repr__(self):
        return f"{self.host_path}:{self.container_path}"


@dataclass
class EnvironmentVariable:
    key: str
    value: str


@dataclass
class SlapptConfig:
    # script attributes
    image: Optional[str] = None
    partition: Optional[str] = None
    entrypoint: Optional[str] = None
    workdir: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    file: Optional[str] = None
    shell: Shell = Shell.BASH
    inputs: Optional[str] = None
    iterations: Optional[int] = None
    parallelism: Parallelism = Parallelism.JOBARRAY
    environment: Optional[List[EnvironmentVariable]] = None
    bind_mounts: Optional[List[BindMount]] = None
    log_file: Optional[str] = None
    no_cache: bool = False
    gpus: int = 0
    time: str = "01:00:00"
    account: Optional[str] = None
    mem: str = "1GB"
    nodes: int = 1
    cores: int = 1
    tasks: int = 1
    header_skip: Optional[str] = None
    singularity: bool = False
    # jobqueue attributes
    host: Optional[str] = None
    port: int = 22
    username: Optional[str] = None
    password: Optional[str] = None
    pkey: Optional[str] = None
    key: Optional[str] = None
    allow_stderr: bool = False
    timeout: int = 15

    def __repr__(self):
        return pformat(deepcopy(self))
