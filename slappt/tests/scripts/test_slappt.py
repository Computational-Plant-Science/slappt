from os import environ
from pprint import pprint
from uuid import uuid4

import pytest

from slappt.models import SlapptConfig
from slappt.slappt import generate_script

partition = environ.get("CLUSTER_PARTITION")
account = environ.get("CLUSTER_ACCOUNT")
email = environ.get("CLUSTER_EMAIL")


# todo parametrize with optional params (e.g. account)
@pytest.mark.parametrize("file", [None, "job.sh"])
def test_script_hello_world(tmp_path, file):
    config = SlapptConfig(
        file=str(tmp_path / file) if file else None,
        name=str(uuid4()),
        image="alpine",
        entrypoint="echo 'hello world'",
        workdir=str(tmp_path),
        email=email,
        partition=partition,
    )

    script = generate_script(config)
    pprint(script)
    assert script[0].startswith("#!/bin/bash")


@pytest.mark.parametrize("file", [None, "job.sh"])
def test_script_with_inputs_file(tmp_path, file):
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
        file=str(tmp_path / file) if file else None,
        name=str(uuid4()),
        image="alpine",
        entrypoint="cat $SLAPPT_INPUT",
        workdir=str(tmp_path),
        email=email,
        partition=partition,
        inputs=str(inputs_file),
    )

    script = generate_script(config)
    pprint(script)
    assert script[0].startswith("#!/bin/bash")
