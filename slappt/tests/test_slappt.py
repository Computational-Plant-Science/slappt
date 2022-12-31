from os import environ
from os.path import join
from pathlib import Path
from pprint import pprint
from uuid import uuid4

import pytest

from slappt.models import SlapptConfig
from slappt.slappt import generate_script, submit_script
from slappt.ssh import SSH

CLUSTER_HOST = environ.get("CLUSTER_HOST")
CLUSTER_USER = environ.get("CLUSTER_USER")
CLUSTER_ACCOUNT = environ.get("CLUSTER_ACCOUNT")
CLUSTER_PASSWORD = environ.get("CLUSTER_PASSWORD")
CLUSTER_KEY_PATH = environ.get("CLUSTER_KEY_PATH")
CLUSTER_HOME_DIR = environ.get("CLUSTER_HOME_DIR")
CLUSTER_PARTITION = environ.get("CLUSTER_PARTITION")
CLUSTER_EMAIL = environ.get("CLUSTER_EMAIL")
SCRIPT_NAME = "slurm_template.sh"
SCRIPT_PATH_REMOTE = Path(CLUSTER_HOME_DIR) / SCRIPT_NAME
SCRIPT_BODY = """\
#!/bin/bash
#SBATCH --job-name=slappt_test
#SBATCH --time=00:10:00
#SBATCH --partition={partition}
#SBATCH --mem=1GB
#SBATCH -c 1
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user={email}
#SBATCH --output=slappt_test.%j.out
#SBATCH --error=slappt_test.%j.err

echo "hello world"
""".format(
    partition=CLUSTER_PARTITION, email=CLUSTER_EMAIL
)


# todo parametrize with optional params (e.g. account)
def test_script_hello_world(tmp_path):
    config = SlapptConfig(
        name=str(uuid4()),
        image="alpine",
        entrypoint="echo 'hello world'",
        workdir=str(tmp_path),
        email=CLUSTER_EMAIL,
        partition=CLUSTER_PARTITION,
    )

    script = generate_script(config)
    pprint(script)
    assert script[0].startswith("#!/bin/bash")


def test_script_with_inputs_file(tmp_path):
    input_file_1 = tmp_path / "input_1.txt"
    input_file_2 = tmp_path / "input_2.txt"
    inputs_file = tmp_path / "inputs.txt"

    with open(input_file_1, "w") as f:
        f.write("input 1")

    with open(input_file_2, "w") as f:
        f.write("input 2")

    with open(inputs_file, "w") as f:
        f.write(str(input_file_1))
        f.write(str(input_file_2))

    config = SlapptConfig(
        name=str(uuid4()),
        image="alpine",
        entrypoint="cat $SLAPPT_INPUT",
        workdir=str(tmp_path),
        email=CLUSTER_EMAIL,
        partition=CLUSTER_PARTITION,
        inputs=str(inputs_file),
    )

    script = generate_script(config)
    pprint(script)
    assert script[0].startswith("#!/bin/bash")
    assert script[-2].startswith("SLAPPT_INPUT=")


def test_script_with_singularity_flag(tmp_path):
    config = SlapptConfig(
        name=str(uuid4()),
        image="alpine",
        entrypoint="echo 'hello world'",
        workdir=str(tmp_path),
        email=CLUSTER_EMAIL,
        partition=CLUSTER_PARTITION,
        singularity=True,
    )

    script = generate_script(config)
    pprint(script)
    assert script[0].startswith("#!/bin/bash")
    assert any(s.startswith("singularity exec") for s in script)
    assert not any(s.startswith("apptainer exec") for s in script)


def test_script_with_pre_commands(tmp_path):
    precmds = ["echo 'pre command 1'", "echo 'pre command 2'"]
    config = SlapptConfig(
        name=str(uuid4()),
        image="alpine",
        entrypoint="echo 'hello world'",
        workdir=str(tmp_path),
        email=CLUSTER_EMAIL,
        partition=CLUSTER_PARTITION,
    )

    script = generate_script(config)
    pprint(script)
    assert script[0].startswith("#!/bin/bash")
    assert not any(s.startswith("echo 'pre") for s in script)

    config = SlapptConfig(
        name=str(uuid4()),
        image="alpine",
        entrypoint="echo 'hello world'",
        workdir=str(tmp_path),
        email=CLUSTER_EMAIL,
        partition=CLUSTER_PARTITION,
        pre=precmds,
    )

    script = generate_script(config)
    pprint(script)
    assert script[0].startswith("#!/bin/bash")
    for cmd in precmds:
        assert any(s.startswith(cmd) for s in script)
    for i, line in enumerate(script):
        if line.startswith(precmds[0]):
            assert script[i + 1].startswith(precmds[1])
            assert script[i + 2].startswith("apptainer exec")


@pytest.mark.skipif(not CLUSTER_HOST, reason="need Slurm cluster")
def upload_script(local, remote):
    with SSH(
        host=CLUSTER_HOST,
        port=22,
        username=CLUSTER_USER,
        password=CLUSTER_PASSWORD,
    ) as client:
        with client.open_sftp() as sftp:
            sftp.put(str(local), str(remote))


@pytest.mark.skipif(not CLUSTER_HOST, reason="need Slurm cluster")
def test_submit_with_password_auth(tmp_path):
    test_id = str(uuid4())
    script_path = tmp_path / SCRIPT_NAME
    with open(script_path, "w") as f:
        f.writelines(SCRIPT_BODY)
    upload_script(script_path, SCRIPT_PATH_REMOTE)
    config = SlapptConfig(
        host=CLUSTER_HOST,
        port=22,
        username=CLUSTER_USER,
        password=CLUSTER_PASSWORD,
        workdir=join(CLUSTER_HOME_DIR, test_id),
        file=str(script_path),
    )
    submit_script(config)


@pytest.mark.skipif(not CLUSTER_HOST, reason="need Slurm cluster")
def test_submit_with_key_auth(tmp_path):
    test_id = str(uuid4())
    script_path = tmp_path / SCRIPT_NAME
    with open(script_path, "w") as f:
        f.writelines(SCRIPT_BODY)
    upload_script(script_path, SCRIPT_PATH_REMOTE)
    config = SlapptConfig(
        host=CLUSTER_HOST,
        port=22,
        username=CLUSTER_USER,
        pkey=CLUSTER_KEY_PATH,
        workdir=join(CLUSTER_HOME_DIR, test_id),
        file=str(script_path),
    )
    submit_script(config)
