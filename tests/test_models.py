import pytest

from ..models import CreateTips


@pytest.mark.parametrize("sats", [21, "21"])
def test_create_tip_accepts_numeric_and_string_amounts(sats):
    tip = CreateTips.model_validate(
        {"name": "Hal", "sats": sats, "tipjar": "test-tipjar", "message": "Thanks"}
    )

    assert tip.sats == 21
