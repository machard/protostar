from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from starkware.starknet.testing.objects import StarknetTransactionExecutionInfo
from starkware.starkware_utils.error_handling import StarkException

from protostar.commands.test.test_environment_exceptions import (
    StarknetRevertableException,
)
from protostar.starknet.cheatable_execute_entry_point import (
    CheatableExecuteEntryPoint,
)
from protostar.starknet.cheatcode_factory import CheatcodeFactory
from protostar.starknet.execution_state import ExecutionState

InvokeResultT = TypeVar("InvokeResultT")


class ExecutionEnvironment(ABC, Generic[InvokeResultT]):
    def __init__(self, state: ExecutionState):
        self.state: ExecutionState = state

    @abstractmethod
    async def invoke(self, function_name: str) -> InvokeResultT:
        ...

    async def perform_invoke(
        self, function_name: str, *args, **kwargs
    ) -> StarknetTransactionExecutionInfo:
        try:
            func = getattr(self.state.contract, function_name)
            return await func(*args, **kwargs).invoke()
        except StarkException as ex:
            raise StarknetRevertableException(
                error_message=StarknetRevertableException.extract_error_messages_from_stark_ex_message(
                    ex.message
                ),
                error_type=ex.code.name,
                code=ex.code.value,
                details=ex.message,
            ) from ex

    # TODO(mkaput): Replace these two with stateless parameters passing to ForkableStarknet.
    @staticmethod
    def set_cheatcodes(cheatcode_factory: CheatcodeFactory):
        CheatableExecuteEntryPoint.cheatcode_factory = cheatcode_factory
