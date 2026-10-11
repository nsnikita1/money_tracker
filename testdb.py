from db import init_db, add_expense, get_month_total

init_db()
add_expense(111, 50000, 'еда', 'обед')
add_expense(222, 10000, 'транспорт')

print(get_month_total(111))  # ждём 50000 (плюс старые записи, если были)
print(get_month_total(222))  # ждём 10000 (плюс старые записи, если были)
