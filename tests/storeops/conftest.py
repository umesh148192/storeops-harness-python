from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from storeops.activities.repository import repository as activities_repo
from storeops.alerts.repository import repository as alerts_repo
from storeops.main import app
from storeops.programmes.repository import repository as programmes_repo
from storeops.reports.repository import repository as reports_repo
from storeops.shared.deps import UserContext, get_current_store, get_current_user
from storeops.shared.entities import StaffRole, Store
from storeops.staff.repository import repository as staff_repo

FAKE_STORE = Store(id="store-1", name="Downtown", region="North")
FAKE_USER_CONTEXT = UserContext(user_id="stub-user-1", store_id=FAKE_STORE.id, role=StaffRole.STORE_MANAGER)


@pytest.fixture(autouse=True)
def _reset_repositories():
    activities_repo.reset()
    programmes_repo.reset()
    staff_repo.reset()
    alerts_repo.reset()
    reports_repo.reset()
    yield


@pytest.fixture()
def client():
    app.dependency_overrides[get_current_user] = lambda: FAKE_USER_CONTEXT
    app.dependency_overrides[get_current_store] = lambda: FAKE_STORE
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
