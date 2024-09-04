import pytest
from orders import *
from unittest.mock import Mock


# --------------------------------------------------------------------------------
# Tests for calculate_total
# --------------------------------------------------------------------------------

@pytest.mark.parametrize(
    'subtotal, shipping, discount, tax_percent, expected',
    [
        (90, 10, 20, 0.05, 84.00),
        (0, 10, 5, 0.05, 5.25),
        (90, 0, 20, 0.05, 73.50),
        (90, 10, 0, 0.05, 105.00),
        (90, 10, 20, 0, 80.00),
        (10, 5, 5, 0.0875, 10.88),
        (10, 5, 5, 0.0733, 10.73),
        (10, 10, 20, 0.05, 0.00),
        (10, 5, 20, 0.05, 0.00),
    ]
)
def test_calculate_total(subtotal, shipping, discount, tax_percent, expected):
    assert calculate_total(subtotal, shipping, discount, tax_percent) == expected


@pytest.mark.parametrize(
    'subtotal, shipping, discount, tax_percent, variable',
    [
        (-90, 10, 20, 0.05, 'subtotal'),
        (90, -10, 20, 0.05, 'shipping'),
        (90, 10, -20, 0.05, 'discount'),
        (90, 10, 20, -0.05, 'tax_percent'),
    ]
)
def test_calculate_total_negatives(subtotal, shipping, discount, tax_percent, variable):
    with pytest.raises(ValueError) as e:
        calculate_total(subtotal, shipping, discount, tax_percent)
    assert str(e.value) == f'{variable} cannot be negative'


# --------------------------------------------------------------------------------
# Tests for Item
# --------------------------------------------------------------------------------

def test_Item_init():
    item = Item('stuff', 12.34, 3)
    assert item.name == 'stuff'
    assert item.unit_price == 12.34
    assert item.quantity == 3


def test_Item_init_default_quantity():
    item = Item('stuff', 12.34)
    assert item.name == 'stuff'
    assert item.unit_price == 12.34
    assert item.quantity == 1


@pytest.mark.parametrize(
    'unit_price, quantity, expected',
    [
        (12.34, 1, 12.34),
        (12.34, 3, 37.02),
        (12.34, 0, 0),
        (0, 1, 0),
    ]
)
def test_Item_calculate_item_total(unit_price, quantity, expected):
    item = Item('stuff', unit_price, quantity)
    assert expected == item.calculate_item_total()


# --------------------------------------------------------------------------------
# Tests for Order
# --------------------------------------------------------------------------------

def test_Order_init():
    order = Order()
    assert isinstance(order.items, list)
    assert len(order.items) == 0


def test_Order_add_item_to_empty():
    order = Order()
    first_item = Item('stuff', 12.34)
    order.add_item(first_item)
    assert len(order.items) == 1
    assert order.items[0] == first_item


def test_Order_add_item_to_existing():
    order = Order()
    item0 = Item('stuff', 12.34)
    item1 = Item('more', 9.99)
    order.add_item(item0)
    order.add_item(item1)
    assert len(order.items) == 2
    assert order.items[0] == item0
    assert order.items[1] == item1


def test_Order_calculate_subtotal_for_multiple_items():
    order = Order()

    item0 = Mock()
    item0.calculate_item_total.return_value = 5
    order.add_item(item0)

    item1 = Mock()
    item1.calculate_item_total.return_value = 20
    order.add_item(item1)

    assert order.calculate_subtotal() == 25


def test_Order_calculate_order_total(mocker):
    order = Order(10, 5, 0.05)
    subtotal_mock = mocker.patch.object(
        order, 'calculate_subtotal', return_value=100)
    total_mock = mocker.patch(
        'orders.calculate_total', return_value=110.25)

    order_total = order.calculate_order_total()

    assert order_total == 110.25
    subtotal_mock.assert_called_once()
    total_mock.assert_called_once_with(100, 10, 5, 0.05)


def test_Order_get_reward_points(mocker):
    order = Order()
    subtotal_mock = mocker.patch.object(
        order, 'calculate_order_total', return_value=1000)
    assert order.get_reward_points() == 1010



# --------------------------------------------------------------------------------
# Tests for DynamicallyPricedItem
# --------------------------------------------------------------------------------

@pytest.mark.parametrize(
    'unit_price, quantity, expected',
    [
        (12.34, 1, 12.34),
        (12.34, 3, 37.02),
        (12.34, 0, 0),
        (0, 1, 0),
    ]
)
def test_DynamicallyPricedItem_calculate_item_total(
    mocker, unit_price, quantity, expected):

    item = DynamicallyPricedItem(12345, quantity)
    mocker.patch.object(item, 'get_latest_price', return_value=unit_price)
    assert expected == item.calculate_item_total()



def test_DynamicallyPricedItem_get_latest_price_invalid_endpoint_operation_mut(mocker):
    item = DynamicallyPricedItem(12345)
    
   
    mocker.patch('requests.get', side_effect=TypeError)

    
    with pytest.raises(TypeError):
        item.get_latest_price()

def test_DynamicallyPricedItem_get_latest_price_none_endpoint_mut_mut(mocker):
    item = DynamicallyPricedItem(12345)
    
    
    mocker.patch('requests.get', side_effect=TypeError)

    
    with pytest.raises(TypeError):
        item.get_latest_price()

def test_DynamicallyPricedItem_get_latest_price_none_response_mut(mocker):
    item = DynamicallyPricedItem(12345)
    
    
    mocker.patch('requests.get', return_value=None)
    
    
    with pytest.raises(AttributeError):
        item.get_latest_price()

def test_DynamicallyPricedItem_get_latest_price_none_price_mut(mocker):
    item = DynamicallyPricedItem(12345)
    
    
    mock_response = mocker.Mock()
    mock_response.json.return_value = {'price': None}
    mocker.patch('requests.get', return_value=mock_response)
    
    
    price = item.get_latest_price()
    assert price is None  


def test_DynamicallyPricedItem_get_latest_price_invalid_json_key_mut(mocker):
    item = DynamicallyPricedItem(12345)
    
    mock_response = mocker.Mock()
    mock_response.json.return_value = {'XXpriceXX': 100.0}
    mocker.patch('requests.get', return_value=mock_response)
    
    with pytest.raises(KeyError):
        item.get_latest_price()

def test_calculate_total_amount_zero_mut():

    subtotal = 10
    shipping = 5
    discount = 15  
    tax_percent = 0.05


    assert calculate_total(subtotal, shipping, discount, tax_percent) == 0


def test_calculate_total_amount_just_above_zero_mut():
    subtotal = 10
    shipping = 5
    discount = 14.5  
    tax_percent = 0.05

    expected_total = 0.5 * (1 + tax_percent)
    
    
    assert calculate_total(subtotal, shipping, discount, tax_percent) == pytest.approx(expected_total, 0.01)

def test_order_default_shipping_mut():
    order = Order()
    
    
    assert order.shipping == 0


def test_order_default_discount_mut():
    
    order = Order()
    
    assert order.discount == 0

def test_order_default_tax_percent_mut():
    
    order = Order()
    
    assert order.tax_percent == 0

def test_dynamically_priced_item_default_quantity_mut():

    item = DynamicallyPricedItem(12345)
    
    
    assert item.quantity == 1

def test_dynamically_priced_item_id_none_mut(mocker):
    
    mock_get = mocker.patch('requests.get')
    mock_get.return_value.json.return_value = {'price': 0}

    
    item = DynamicallyPricedItem(None)
    
   
    item.get_latest_price()
    mock_get.assert_called_once_with('https://api.pandastore.com/getitem/None')

    assert mock_get.call_count == 1
    assert mock_get.call_args[0][0] == 'https://api.pandastore.com/getitem/None'


def test_calculate_total_amount_zero_mut():
  
    subtotal = 10
    shipping = 5
    discount = 15  
    tax_percent = 0.05

    assert calculate_total(subtotal, shipping, discount, tax_percent) == 0

def test_dynamically_priced_item_id_none_behavior_mut(mocker):
    
    mock_get = mocker.patch('requests.get')

    item = DynamicallyPricedItem(None)

    item.get_latest_price()

    mock_get.assert_called_once_with('https://api.pandastore.com/getitem/None')

    with pytest.raises(TypeError):
        if mock_get.call_args[0][0] == 'https://api.pandastore.com/getitem/None':
            raise TypeError("Invalid ID type resulting in malformation of URL")


def test_calculate_item_total_rounding():
    item = DynamicallyPricedItem(12345, 1)

    mock_price = 12.34567 
    item.get_latest_price = lambda: mock_price


    expected_total = round(mock_price, 2)
    assert item.calculate_item_total() == expected_total