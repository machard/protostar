from asyncio import Future
from pathlib import Path
from typing import cast

import pytest
from pytest_mock import MockerFixture
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId

from protostar.commands.migrate.migrate_command import MigrateCommand
from protostar.commands.test.test_environment_exceptions import CheatcodeException
from protostar.migrator import Migrator
from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import GatewayFacade
from protostar.utils.input_requester import InputRequester


def mock_migrator_builder(
    mocker: MockerFixture, migrator_mock: Migrator
) -> Migrator.Builder:
    migrator_mock_future = Future()
    migrator_mock_future.set_result(migrator_mock)
    migrator_builder_mock = cast(Migrator.Builder, mocker.MagicMock())
    cast(
        mocker.MagicMock, migrator_builder_mock.build
    ).return_value = migrator_mock_future
    return migrator_builder_mock


def setup_migrate(mocker: MockerFixture):
    input_requester_mock = cast(InputRequester, mocker.MagicMock())
    requester_confirm_mock = cast(mocker.MagicMock, input_requester_mock.confirm)
    migrator_mock = cast(Migrator, mocker.MagicMock())
    migration_result_future = Future()
    migration_result_future.set_result(Migrator.History(starknet_requests=[]))
    migrator_run_mock = cast(mocker.MagicMock, migrator_mock.run)
    migrator_run_mock.return_value = migration_result_future
    project_root_path = mocker.MagicMock()

    migrate_command = MigrateCommand(
        project_root_path=project_root_path,
        migrator_builder=mock_migrator_builder(mocker, migrator_mock),
        logger=mocker.MagicMock(),
        log_color_provider=mocker.MagicMock(),
        requester=input_requester_mock,
    )

    async def migrate(no_confirm: bool):
        await migrate_command.migrate(
            migration_file_path=Path(),
            rollback=False,
            output_dir_path=None,
            no_confirm=no_confirm,
            gateway_facade=GatewayFacade(
                project_root_path=project_root_path,
                gateway_client=GatewayClient(
                    net="http://localhost:3000/", chain=StarknetChainId.TESTNET
                ),
            ),
            migrator_config=mocker.MagicMock(),
        )

    return migrate, migrator_run_mock, requester_confirm_mock


async def test_cheatcode_exceptions_are_pretty_printed(mocker: MockerFixture):
    migrator_mock = cast(Migrator, mocker.MagicMock())
    cast(mocker.MagicMock, migrator_mock.run).side_effect = CheatcodeException(
        cheatcode="CHEATCODE_NAME", message="CHEATCODE_EX_MSG"
    )

    migrate_command = MigrateCommand(
        migrator_builder=mock_migrator_builder(mocker, migrator_mock),
        logger=mocker.MagicMock(),
        log_color_provider=mocker.MagicMock(),
        requester=mocker.MagicMock(),
        project_root_path=mocker.MagicMock(),
    )

    with pytest.raises(ProtostarException, match="CHEATCODE_EX_MSG"):
        await migrate_command.migrate(
            gateway_facade=mocker.MagicMock(),
            migration_file_path=Path(),
            rollback=False,
            output_dir_path=None,
            no_confirm=True,
            migrator_config=mocker.MagicMock(),
        )


async def test_skipping_confirmation(mocker: MockerFixture):
    (migrate, migrator_run_mock, requester_confirm_mock) = setup_migrate(mocker)

    await migrate(no_confirm=True)

    requester_confirm_mock.assert_not_called()
    migrator_run_mock.assert_called()


async def test_lack_of_confirmation_preventing_migration(mocker: MockerFixture):
    (migrate, migrator_run_mock, requester_confirm_mock) = setup_migrate(mocker)
    requester_confirm_mock.return_value = False

    await migrate(no_confirm=False)

    requester_confirm_mock.assert_called_once()
    migrator_run_mock.assert_not_called()


async def test_confirmation_not_preventing_migration(mocker: MockerFixture):
    (migrate, migrator_run_mock, requester_confirm_mock) = setup_migrate(mocker)

    await migrate(no_confirm=False)

    requester_confirm_mock.assert_called()
    migrator_run_mock.assert_called_once()
