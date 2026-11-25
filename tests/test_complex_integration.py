import pytest

from src.manager import Manager
from src.models import Bill, Parameters
from src.manager import Manager
from src.models import Parameters
from src.models import Bill


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


def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    costs = manager.get_apartment_costs('apartment-1', 2024, 1)
    assert costs is None

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == 0.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0
    
    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0

    costs = manager.get_apartment_costs('apart-polanka')
    assert costs == 3532.0
