from datetime import datetime, time, timedelta
from typing import Any, Callable, Dict, Optional
from unittest.mock import ANY, Mock

import pytest

from ezyquant_execute.context import ExecuteContext
from ezyquant_execute.executing import execute


class TestExecuting:
    @pytest.mark.parametrize("signal_dict", [{}, {"a": 1}, {"a": 1, "b": 2}])
    def test_signal_dict(self, signal_dict: Dict[str, Any]):
        self._test(signal_dict=signal_dict)

    def test_execute_algorithm_event_set(self):
        """If event.set() is called, this function will be stopped after iteration."""
        # Mock
        signal_dict = {"a": 1, "b": 2}

        # Test
        self._test(signal_dict=signal_dict)

    def test_execute_algorithm_raise(self):
        """If execute_algorithm raise exception, this function will be stopped immediately."""
        # Mock
        signal_dict = {"a": 1, "b": 2}
        m = Mock(side_effect=BufferError)

        # Test
        with pytest.raises(BufferError):
            self._test(signal_dict=signal_dict, execute_algorithm=m)

        # Check
        m.assert_called_once()

    def _test(
        self,
        signal_dict: Dict[str, Any] = {"a": 1},
        execute_algorithm: Optional[Callable[[ExecuteContext], None]] = None,
        interval: float = 1.0,
        start_time: time = time(0, 0, 0),
        end_time: Optional[time] = None,
    ):
        if not end_time:
            end_time = (datetime.now() + timedelta(seconds=1)).time()

        if not execute_algorithm:
            execute_algorithm = Mock()

        execute(
            settrade_user=ANY,
            signal_dict=signal_dict,
            execute_algorithm=execute_algorithm,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
        )

        if isinstance(execute_algorithm, Mock):
            if not signal_dict:
                execute_algorithm.assert_not_called()
            for k, v in signal_dict.items():
                execute_algorithm.assert_any_call(
                    ExecuteContext(settrade_user=ANY, event=ANY, symbol=k, signal=v)
                )