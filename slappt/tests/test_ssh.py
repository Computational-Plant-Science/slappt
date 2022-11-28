from os import environ

import pytest

from slappt.ssh import SSH

CLUSTER_HOST = environ.get("CLUSTER_HOST")
CLUSTER_USER = environ.get("CLUSTER_USER")
CLUSTER_PASSWORD = environ.get("CLUSTER_PASSWORD")
CLUSTER_KEY_PATH = environ.get("CLUSTER_KEY_PATH")
CLUSTER_HOME_DIR = environ.get("CLUSTER_HOME_DIR")


@pytest.mark.skipif(not CLUSTER_HOST, reason="need Slurm cluster")
def test_connection_password_auth():
    with SSH(
        host=CLUSTER_HOST,
        port=22,
        username=CLUSTER_USER,
        password=CLUSTER_PASSWORD,
    ) as client:
        assert client.get_transport()
        assert client.get_transport().is_active()


@pytest.mark.skipif(not CLUSTER_HOST, reason="need Slurm cluster")
def test_connection_key_auth():
    with SSH(
        host=CLUSTER_HOST,
        port=22,
        username=CLUSTER_USER,
        pkey=CLUSTER_KEY_PATH,
    ) as client:
        assert client.get_transport()
        assert client.get_transport().is_active()


@pytest.mark.skipif(not CLUSTER_HOST, reason="need Slurm cluster")
def test_command_password_auth():
    with SSH(
        host=CLUSTER_HOST,
        port=22,
        username=CLUSTER_USER,
        password=CLUSTER_PASSWORD,
    ) as client:
        stdin, stdout, stderr = client.exec_command("pwd")
        assert f"{CLUSTER_HOME_DIR}\n" == stdout.readlines()[0]


@pytest.mark.skipif(not CLUSTER_HOST, reason="need Slurm cluster")
def test_command_key_auth():
    with SSH(
        host=CLUSTER_HOST,
        port=22,
        username=CLUSTER_USER,
        pkey=CLUSTER_KEY_PATH,
    ) as client:
        stdin, stdout, stderr = client.exec_command("pwd")
        assert f"{CLUSTER_HOME_DIR}\n" == stdout.readlines()[0]
