import re
from os import listdir
from pathlib import Path
from shutil import copyfile

import pytest
from starknet_py.net.models import StarknetChainId

from tests.e2e.conftest import ProtostarFixture


@pytest.mark.usefixtures("init")
def test_migrating_base_case(
    protostar: ProtostarFixture, devnet_gateway_url, datadir: Path
):
    protostar(["build"])
    migrations_dir_path = Path("./migrations")
    migrations_dir_path.mkdir()
    copyfile(
        src=str(datadir / "migration_up_down.cairo"),
        dst=str(migrations_dir_path / "migration.cairo"),
    )

    result = protostar(
        [
            "--no-color",
            "migrate",
            "migrations/migration.cairo",
            "--gateway-url",
            devnet_gateway_url,
            "--chain-id",
            str(StarknetChainId.TESTNET.value),
            "--no-confirm",
            "--output-dir",
            "migrations/output",
        ]
    )

    assert "Migration completed" in result
    assert len(listdir((migrations_dir_path / "output"))) == 1
    assert count_hex64(result) == 2


def count_hex64(x: str) -> int:
    return len(re.findall(r"0x[0-9a-f]{64}", x))
