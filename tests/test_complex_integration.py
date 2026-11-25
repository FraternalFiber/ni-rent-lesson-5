import pytest

from src.manager import Manager
from src.models import Bill, Parameters


def make_bill(amount, year, month, apartment='apart-polanka'):
    return Bill(
        amount_pln = amount,
        date_due = f'{year}-{month:02d}-15',
        settlement_year = year,
        settlement_month = month,
        apartment = apartment,
        type = 'rent'
    )


def test_get_apartment_costs():
    manager = Manager(Parameters())
    manager.bills = [
        make_bill(300.0, 2024, 3),
        make_bill(150.0, 2024, 3),
        make_bill(999.0, 2024, 4),   # inny miesiąc
        make_bill(888.0, 2023, 3),   # inny rok
    ]

    # mieszkanie nie istnieje
    with pytest.raises(ValueError):
        manager.get_apartment_costs('invalid-key', 2024, 3)

    # brak rachunków w tym miesiącu
    assert manager.get_apartment_costs('apart-polanka', 2024, 5) == 0.0

    # rachunki w tym miesiącu
    assert manager.get_apartment_costs('apart-polanka', 2024, 3) == 450.0

    # rok się zgadza, miesiąc nie
    assert manager.get_apartment_costs('apart-polanka', 2024, 4) == 999.0