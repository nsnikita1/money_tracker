import pytest
from utils import parse_amount, format_money

def test_parse_amount():
    assert parse_amount('500') == 50000
    assert parse_amount('500.50') == 50050
    assert parse_amount('0.01') == 1

@pytest.mark.parametrize(
    'bad',
    ['abc', '0', '-5', 'nan']
)
def test_parse_amount_fails(bad):
    with pytest.raises(ValueError):
        parse_amount(bad)

def test_format_money():
    assert format_money(500) == '5.00'
    assert format_money(50050) == '500.50'
    assert format_money(5) == '0.05'
