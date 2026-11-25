import pytest

from src.manager import Manager
from src.models import ApartmentSettlement, Bill, Parameters


def make_bill(amount, year, month, type_, apartment='apart-polanka'):
    return Bill(
        amount_pln = amount,
        date_due = f'{year}-{month:02d}-15',
        settlement_year = year,
        settlement_month = month,
        apartment = apartment,
        type = type_
    )


def test_create_apartment_settlement():
    manager = Manager(Parameters())
    manager.bills = [
        make_bill(760.0, 2025, 1, 'rent'),
        make_bill(150.0, 2025, 1, 'electricity'),
        make_bill(40.5, 2025, 1, 'water'),
        make_bill(999.0, 2025, 2, 'rent'),                # inny miesiąc
        make_bill(888.0, 2024, 1, 'rent'),                # inny rok
        make_bill(777.0, 2025, 1, 'rent', 'other-apart'), # inne mieszkanie
    ]

    # mieszkanie z rachunkami w tym miesiącu
    settlement = manager.create_apartment_settlement('apart-polanka', 2025, 1)
    assert isinstance(settlement, ApartmentSettlement)
    assert settlement.apartment == 'apart-polanka'
    assert settlement.month == 1
    assert settlement.year == 2025
    assert settlement.total_rent_pln == 760.0
    assert settlement.total_bills_pln == 190.5
    assert settlement.total_due_pln == 950.5

    # mieszkanie bez rachunków w tym miesiącu
    settlement = manager.create_apartment_settlement('apart-polanka', 2025, 3)
    assert settlement.month == 3
    assert settlement.total_rent_pln == 0.0
    assert settlement.total_bills_pln == 0.0
    assert settlement.total_due_pln == 0.0


def test_create_apartment_settlement_edge_cases():
    manager = Manager(Parameters())

    # mieszkanie nie istnieje
    assert manager.create_apartment_settlement('invalid-key', 2025, 1) is None

    # niepoprawny miesiąc
    with pytest.raises(ValueError):
        manager.create_apartment_settlement('apart-polanka', 2025, 13)