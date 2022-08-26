import ctypes
from multiprocessing.managers import SyncManager
from typing import TYPE_CHECKING, List

from protostar.commands.test.test_results import PassedTestCaseResult, TestResult
from starkware.cairo.lang.compiler.error_handling import Location

if TYPE_CHECKING:
    from protostar.commands.test.test_collector import TestCollector


class SharedTestsState:
    def __init__(
        self,
        test_collector_result: "TestCollector.Result",
        manager: SyncManager,
    ) -> None:
        self._shared_queue = manager.Queue()
        self._locations_queue = manager.Queue()
        self._any_failed_or_broken_shared_value = manager.Value(
            ctypes.c_bool,
            (len(test_collector_result.broken_test_suites) > 0),
        )

    def get_result(self) -> TestResult:
        return self._shared_queue.get(block=True, timeout=1000)

    def put_result(self, item: TestResult) -> None:
        if not isinstance(item, PassedTestCaseResult):
            self._any_failed_or_broken_shared_value.value = True
        self._shared_queue.put(item)

    def any_failed_or_broken(self) -> bool:
        return self._any_failed_or_broken_shared_value.value

    def append_covered_locations(self, locations: List[Location]):
        self._locations_queue.put(locations)

    def get_covered_locations(self) -> List[Location]:
        return self._locations_queue.get(block=True, timeout=1000)
