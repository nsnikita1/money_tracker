from datetime import datetime
from decimal import Decimal, InvalidOperation


def parse_amount(text):
    '''Превращает '500' или '500,50' в копейки: 50000 или 50050.'''
    try:
        value = Decimal(text.replace(',', '.'))
    except InvalidOperation:
        raise ValueError('Сумма должна быть числом')
    if not value.is_finite() or value <= 0:
        raise ValueError('Сумма должна быть больше нуля')
    if value > 1_000_000_000:
        raise ValueError('Слишком большая сумма')
    return int(value * 100)


def parse_date(text):
    '''Проверяет дату вида 2026-10-07 и возвращает её же.'''
    try:
        return datetime.strptime(text, '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
        raise ValueError('Дата должна быть в формате 2026-10-07')


def format_money(kopeks):
    return f'{kopeks // 100}.{kopeks % 100:02d}'