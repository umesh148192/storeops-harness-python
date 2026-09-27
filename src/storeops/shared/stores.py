from __future__ import annotations

from storeops.shared.entities import Store

_SEED_STORES = [
    Store(id="store-1", name="Downtown", region="North"),
    Store(id="store-2", name="Uptown", region="North"),
    Store(id="store-3", name="Southside", region="South"),
]


def list_stores_by_region(region: str) -> list[Store]:
    return [store for store in _SEED_STORES if store.region == region]
