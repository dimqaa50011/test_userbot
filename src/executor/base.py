from typing import Any, NamedTuple


class ExecData(NamedTuple):
    ...


class BaseExecutor:
    def __call__(self, *args: Any, exec_data: ExecData, **kwds: Any) -> Any:
        pass
