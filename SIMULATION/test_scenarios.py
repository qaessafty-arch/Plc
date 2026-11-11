import pytest
from scenarios import SCENARIOS


@pytest.mark.parametrize("name,fn", SCENARIOS, ids=[s[0][:3] for s in SCENARIOS])
def test_scenario(name, fn):
    res, checks, _ = fn()
    failed = [c for c, ok in checks if not ok]
    assert not failed, f"{name}: {failed}\n{res}"
