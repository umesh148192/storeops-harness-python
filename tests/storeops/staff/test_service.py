from __future__ import annotations

import pytest

from storeops.shared.errors import NotFoundError
from storeops.staff.service import service


def test_get_user_success():
    user = service.get_user("stub-user-1")
    assert user.id == "stub-user-1"


def test_get_user_missing_raises_not_found():
    with pytest.raises(NotFoundError):
        service.get_user("missing")
