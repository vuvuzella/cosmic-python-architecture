import pytest
import requests

from flask_api.settings import flask_api_setting
from tests.common import add_stock, random_batch_ref, random_order_id, random_sku


# Test about web stuff (end 2 end)
@pytest.mark.usefixtures("restart_api")
def test_api_returns_allocations():
    sku_one, sku_two = random_sku(), random_sku("other")
    early_batch = random_batch_ref(1)
    later_batch = random_batch_ref(2)
    other_batch = random_batch_ref(3)

    add_stock(
        [
            (later_batch, sku_one, 100, "2011-01-02"),
            (early_batch, sku_one, 100, "2011-01-01"),
            (other_batch, sku_two, 100, None),
        ]
    )

    # strucure of the Batch model
    data = {"orderid": random_order_id(), "sku": sku_one, "qty": 3}
    url = flask_api_setting.API_URL

    result = requests.post(f"{url}/allocate", json=data)

    assert result.status_code == 201
    assert result.json()["batchref"] == early_batch


@pytest.mark.usefixtures("restart_api")
def test_allocations_are_persisted(add_stock):
    sku = random_sku()
    batch1, batch2 = random_batch_ref(1), random_batch_ref(2)
    order1, order2 = random_order_id(1), random_order_id(2)
    add_stock([(batch1, sku, 10, "2011-01-01"), (batch2, sku, 10, "2011-01-02")])

    line1 = {"orderid": order1, "sku": sku, "qty": 10}
    line2 = {"orderid": order2, "sku": sku, "qty": 10}

    url = flask_api_setting.API_URL

    result1 = requests.post(f"{url}/allocate", json=line1)

    # first order uses up all stock in batch 1
    assert result1.status_code == 201
    assert result1.json()["batchref"] == batch1

    result2 = requests.post(f"{url}/allocate", json=line2)

    # second order uses up all stock in batch 2
    assert result2.status_code == 201
    assert result2.json()["batchref"] == batch2


@pytest.mark.usefixtures("restart_api")
def test_400_message_for_out_of_stock(add_stock):
    sku, small_batch, large_order = random_sku(), random_batch_ref(), random_order_id()
    add_stock([(small_batch, sku, 10, "2011-01-01")])
    data = {"orderid": large_order, "sku": sku, "qty": 20}
    url = flask_api_setting.API_URL

    result = requests.post(f"{url}/allocate", json=data)

    assert result.status_code == 400
    assert result.json()["message"] == f"Out of stock for sku {sku}"


@pytest.mark.usefixtures("restart_api")
def test_400_message_for_invalid_sku():
    unknown_sku, order_id = random_sku(), random_order_id()

    data = {"orderid": order_id, "sku": unknown_sku, "qty": 10}
    url = flask_api_setting.API_URL
    result = requests.post(f"{url}/allocate", data=data)

    assert result.status_code == 400
    assert result.json()["message"] == f"Invalid sku: {unknown_sku}"
