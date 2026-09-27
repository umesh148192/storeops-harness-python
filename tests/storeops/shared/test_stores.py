from __future__ import annotations

from storeops.shared.stores import list_stores_by_region


def test_list_stores_by_region_returns_only_matching_stores():
    stores = list_stores_by_region("North")

    assert {store.id for store in stores} == {"store-1", "store-2"}
    assert all(store.region == "North" for store in stores)


def test_list_stores_by_region_returns_empty_list_for_unknown_region():
    assert list_stores_by_region("Nonexistent") == []
