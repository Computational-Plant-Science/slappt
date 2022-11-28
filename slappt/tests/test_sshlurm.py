from os import environ
from pathlib import Path

import pytest

from slappt.models import SlapptConfig
from slappt.ssh import SSH
from slappt.sshlurm import submit_script

CLUSTER_HOST = environ.get("CLUSTER_HOST")
CLUSTER_USER = environ.get("CLUSTER_USER")
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

echo "hello world
""".format(
    partition=CLUSTER_PARTITION, email=CLUSTER_EMAIL
)


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
    script_path = tmp_path / SCRIPT_NAME
    with open(script_path, "w") as f:
        f.writelines(SCRIPT_BODY)
    upload_script(script_path, SCRIPT_PATH_REMOTE)
    config = SlapptConfig(
        host=CLUSTER_HOST,
        port=22,
        username=CLUSTER_USER,
        password=CLUSTER_PASSWORD,
        workdir=CLUSTER_HOME_DIR,
        file=str(SCRIPT_PATH_REMOTE),
    )
    job_id = submit_script(config)
    assert job_id.isdigit()


@pytest.mark.skipif(not CLUSTER_HOST, reason="need Slurm cluster")
def test_submit_with_key_auth(tmp_path):
    script_path = tmp_path / SCRIPT_NAME
    with open(script_path, "w") as f:
        f.writelines(SCRIPT_BODY)
    upload_script(script_path, SCRIPT_PATH_REMOTE)
    config = SlapptConfig(
        host=CLUSTER_HOST,
        port=22,
        username=CLUSTER_USER,
        pkey=CLUSTER_KEY_PATH,
        workdir=CLUSTER_HOME_DIR,
        file=str(SCRIPT_PATH_REMOTE),
    )
    job_id = submit_script(config)
    assert job_id.isdigit()
