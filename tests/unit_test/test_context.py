from dataclasses import dataclass
from typing import Callable
from unittest.mock import ANY

import pytest

from ezyquant_execution.context import ExecuteContext, ExecuteContextSymbol

SYMBOL = "AOT"


@pytest.fixture
def ctx():
    return ExecuteContextSymbol(
        settrade_user=ANY,
        account_no=ANY,
        symbol=SYMBOL,
    )


@dataclass
class TestStruct:
    id: int
    symbol: str


@pytest.mark.parametrize(
    ("l", "condition", "expected"),
    [
        # Test empty list
        ([], lambda x: True, []),
        ([], lambda x: False, []),
        # Test list with one element
        (
            [TestStruct(id=1, symbol=SYMBOL)],
            lambda x: True,
            [TestStruct(id=1, symbol=SYMBOL)],
        ),
        ([TestStruct(id=1, symbol="BBL")], lambda x: True, []),
        # Test condition
        (
            [TestStruct(id=1, symbol=SYMBOL)],
            lambda x: x.id == 1,
            [TestStruct(id=1, symbol=SYMBOL)],
        ),
        ([TestStruct(id=1, symbol="BBL")], lambda x: x.id == 1, []),
    ],
)
def test_filter_list(ctx: ExecuteContext, l: list, condition: Callable, expected: list):
    result = ctx._filter_list(l, condition=condition)
    assert result == expected


@pytest.mark.parametrize(
    ("balance", "status", "meaning", "expected"),
    [
        (100, "Queuing", "Queuing", True),
        (100, "Pending(OF)", "Pending", True),
        (0, "Queuing", "Queuing", False),
        (100, "Expired", "Expired", False),
        (100, "Cancelled", "Cancelled by user", False),
        (100, "Rejected", "Rejected", False),
        (100, "Rejected(SET)", "Order rejected", False),
    ],
)
def test_is_pending_order(balance: int, status: str, meaning: str, expected: bool):
    from types import SimpleNamespace

    from ezyquant_execution.context import _is_pending_order

    order = SimpleNamespace(
        balance=balance, show_order_status=status, show_order_status_meaning=meaning
    )
    assert _is_pending_order(order) is expected  # type: ignore[arg-type]
