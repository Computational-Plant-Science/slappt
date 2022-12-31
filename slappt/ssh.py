import logging
import os
import platform
import re
from pathlib import Path
from typing import List

import paramiko
from paramiko.ssh_exception import (
    AuthenticationException,
    ChannelException,
    NoValidConnectionsError,
    SSHException,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

_system = platform.system()
_logger = logging.getLogger(__name__)


def default_known_hosts_path():
    if _system == "Windows":
        appdata_path = os.environ.get("APPDATA", None)
        return (
            (appdata_path if appdata_path else Path.home())
            / "SSH"
            / "UserKeys"
        )
    else:
        return Path.home() / ".ssh" / "known_hosts"


class SSH:
    """
    Wraps a Paramiko client with password or SSH keypair authentication.
    Supports proxy-jump pattern and preserves context manager usability.
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str = None,
        pkey: str = None,
        jump_host: str = None,
        jump_port: int = None,
        known_hosts: str = None,
        require_host_key: bool = False,
        timeout: int = 10,
    ):
        self.client = None
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.pkey = pkey
        self.jump_host = jump_host
        self.jump_port = jump_port
        self.require_host_key = require_host_key
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)

        if known_hosts:
            self.known_hosts = Path(known_hosts).expanduser().absolute()
            if not self.known_hosts.is_file():
                raise FileNotFoundError(
                    f"Known hosts file {self.known_hosts} does not exist"
                )
        else:
            self.known_hosts = None

    def __enter__(self):
        client = paramiko.SSHClient()
        jump_client = paramiko.SSHClient()

        # load known hosts from specified file if provided or default location for platform
        known_hosts_path = (
            self.known_hosts
            if self.known_hosts
            else default_known_hosts_path()
        )

        client.load_host_keys(known_hosts_path)
        jump_client.load_host_keys(known_hosts_path)

        if self.require_host_key:
            client.set_missing_host_key_policy(paramiko.RejectPolicy())
            jump_client.set_missing_host_key_policy(paramiko.RejectPolicy())
        else:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            jump_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if self.password is not None:
            if self.jump_host:
                jump_client.connect(
                    self.jump_host,
                    self.jump_port,
                    self.username,
                    self.password,
                    timeout=self.timeout,
                )
                socket = jump_client.get_transport().open_channel(
                    "direct-tcpip", (self.host, self.port), ("", 0)
                )

                client.connect(
                    self.host,
                    self.port,
                    self.username,
                    self.password,
                    timeout=self.timeout,
                    sock=socket,
                )
            else:
                client.connect(
                    self.host,
                    self.port,
                    self.username,
                    self.password,
                    timeout=self.timeout,
                )
        elif self.pkey is not None:
            key = paramiko.RSAKey.from_private_key_file(
                os.path.expanduser(self.pkey)
            )
            if self.jump_host:
                jump_client.connect(
                    self.jump_host,
                    self.jump_port,
                    self.username,
                    pkey=key,
                    timeout=self.timeout,
                )
                socket = jump_client.get_transport().open_channel(
                    "direct-tcpip", (self.host, self.port), ("", 0)
                )
                client.connect(
                    self.host,
                    self.port,
                    self.username,
                    pkey=key,
                    timeout=self.timeout,
                    sock=socket,
                )
            else:
                client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    pkey=key,
                    timeout=self.timeout,
                )
        else:
            raise ValueError(f"No authentication strategy provided")

        self.client = client
        return self.client

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()


def clean_html(raw_html: str) -> str:
    expr = re.compile("<.*?>")
    text = re.sub(expr, "", raw_html)
    return text


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(
        retry_if_exception_type(AuthenticationException)
        | retry_if_exception_type(AuthenticationException)
        | retry_if_exception_type(ChannelException)
        | retry_if_exception_type(NoValidConnectionsError)
        | retry_if_exception_type(SSHException)
    ),
    reraise=True,
)
def execute_interactive_command(
    ssh: SSH,
    setup_command: str,
    command: str,
    responses: List[str],
    directory: str = None,
    allow_stderr: bool = False,
) -> List[str]:
    """
    Executes the given command on the given SSH connection, providing the given new-line separated responses via stdin.
    This method is a generator and will yield any output produced line by line.
    Args:
        ssh: The SSH client.
        setup_command: Commands to prepend to the primary command.
        command: The command.
        responses: The responses to be provided to input prompts following the command.
        directory: Directory to run the command in.
        allow_stderr: Whether to permit `stderr` output (by default an error is thrown).
    Returns:
    """
    full_command = f"{setup_command} && {command}"
    if directory is not None:
        full_command = f"cd {directory} && {full_command}"

    _logger.info(f"Executing command on '{ssh.host}': {full_command}")
    stdin, stdout, stderr = ssh.client.exec_command(
        f"bash --login -c '{full_command}'", get_pty=True
    )
    for response in responses:
        stdin.write(f"{response}\n")
        stdin.flush()
    stdin.close()

    for line in iter(lambda: stdout.readline(2048), ""):
        clean = clean_html(line)
        _logger.debug(f"Received stdout from '{ssh.host}': '{clean}'")
        yield clean

    errors = []
    for line in iter(lambda: stderr.readline(2048), ""):
        clean = clean_html(line)
        _logger.warning(f"Received stderr from '{ssh.host}': '{clean}'")
        yield clean

    if stdout.channel.recv_exit_status() != 0:
        raise Exception(f"Received non-zero exit status from '{ssh.host}'")
    elif not allow_stderr and len(errors) > 0:
        raise Exception(f"Received stderr: {errors}")


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(
        retry_if_exception_type(AuthenticationException)
        | retry_if_exception_type(AuthenticationException)
        | retry_if_exception_type(ChannelException)
        | retry_if_exception_type(NoValidConnectionsError)
        | retry_if_exception_type(SSHException)
    ),
    reraise=True,
)
def execute_command(
    ssh: SSH,
    setup_command: str,
    command: str,
    directory: str = None,
    allow_stderr: bool = False,
) -> List[str]:
    """
    Executes the given command on the given SSH connection. This method is a generator and will yield any output produced line by line.
    Args:
        ssh: The SSH client.
        setup_command: Commands to prepend to the primary command.
        command: The command.
        directory: Directory to run the command in.
        allow_stderr: Whether to permit `stderr` output (by default an error is thrown).
    Returns:
        A generator yielding line-by-line output from the command.
    """

    full_command = f"{setup_command} && {command}"
    if directory is not None:
        full_command = f"cd {directory} && {full_command}"

    _logger.info(f"Executing command on '{ssh.host}': {full_command}")
    stdin, stdout, stderr = ssh.client.exec_command(
        f"bash --login -c '{full_command}'", get_pty=True
    )
    stdin.close()

    for line in iter(lambda: stdout.readline(2048), ""):
        clean = clean_html(line)
        _logger.debug(f"Received stdout from '{ssh.host}': '{clean}'")
        yield clean

    errors = []
    for line in iter(lambda: stderr.readline(2048), ""):
        clean = clean_html(line)
        _logger.warning(f"Received stderr from '{ssh.host}': '{clean}'")
        yield clean

    if stdout.channel.recv_exit_status() != 0:
        raise Exception(f"Received non-zero exit status from '{ssh.host}'")
    elif not allow_stderr and len(errors) > 0:
        raise Exception(f"Received stderr: {errors}")
