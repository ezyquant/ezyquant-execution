from datetime import datetime, time, timedelta
from typing import Any, Callable, Dict, Optional
from unittest.mock import ANY, Mock

import pytest

from ezyquant_execution.context import ExecuteContextSymbol
from ezyquant_execution.executing import async_execute_on_timer, execute_on_timer
from tests.utils import AsyncMock


class TestExecuteOnTimer:
    @pytest.mark.parametrize("signal_dict", [{}, {"a": 1}, {"a": 1, "b": 2}])
    def test_signal_dict(self, signal_dict: Dict[str, Any]):
        self._test(signal_dict=signal_dict)

    def test_on_timer_event_set(self):
        """If event.set() is called, this function will be stopped after iteration."""
        # Mock
        signal_dict = {"a": 1, "b": 2}

        # Test
        self._test(signal_dict=signal_dict)

    def test_on_timer_raise(self):
        """If on_timer raise exception, this function will be stopped immediately."""
        # Mock
        signal_dict = {"a": 1, "b": 2}
        m = Mock(side_effect=BufferError)

        # Test
        with pytest.raises(BufferError):
            self._test(signal_dict=signal_dict, on_timer=m)

        # Check
        m.assert_called_once()

    def _test(
        self,
        signal_dict: Dict[str, Any] = {"a": 1},
        on_timer: Optional[Callable[[ExecuteContextSymbol], None]] = None,
        interval: float = 1.0,
        start_time: time = time(0, 0, 0),
        end_time: Optional[time] = None,
    ):
        if not end_time:
            end_time = (datetime.now() + timedelta(seconds=1)).time()

        if not on_timer:
            on_timer = Mock()

        execute_on_timer(
            settrade_user=ANY,
            account_no=ANY,
            pin=ANY,
            signal_dict=signal_dict,
            on_timer=on_timer,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
        )

        if isinstance(on_timer, Mock):
            if not signal_dict:
                on_timer.assert_not_called()
            for k, v in signal_dict.items():
                on_timer.assert_any_call(
                    ExecuteContextSymbol(
                        settrade_user=ANY,
                        account_no=ANY,
                        pin=ANY,
                        symbol=k,
                        signal=v,
                    )
                )


async def test_async_execute_on_timer():
    # Mock
    signal_dict = {"a": 1}
    on_timer = AsyncMock()
    interval = 1.0
    start_time = time(0, 0, 0)
    end_time = (datetime.now() + timedelta(seconds=1)).time()

    # Test
    await async_execute_on_timer(
        settrade_user=ANY,
        account_no=ANY,
        signal_dict=signal_dict,
        on_timer=on_timer,
        interval=interval,
        start_time=start_time,
        end_time=end_time,
    )

    # Check
    for k, v in signal_dict.items():
        on_timer.assert_any_call(
            ExecuteContextSymbol(
                settrade_user=ANY,
                account_no=ANY,
                pin=ANY,
                symbol=k,
                signal=v,
            )
        )
