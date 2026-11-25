from src.manager import Manager
from src.models import Bill, Parameters, Tenant, TenantSettlement


def make_bill(amount, type_, apartment='apart-polanka'):
    return Bill(
        amount_pln = amount,
        date_due = '2025-02-15',
        settlement_year = 2025,
        settlement_month = 1,
        apartment = apartment,
        type = type_
    )


def make_tenant(name, apartment='apart-polanka'):
    return Tenant(
        name = name,
        apartment = apartment,
        room = 'room-bigger',
        rent_pln = 1000.0,
        deposit_pln = 2000.0,
        date_agreement_from = '2024-01-01',
        date_agreement_to = '2025-12-31'
    )


def test_create_tenant_settlements():
    manager = Manager(Parameters())
    manager.bills = [
        make_bill(900.0, 'rent'),
        make_bill(150.0, 'electricity'),
        make_bill(60.0, 'water'),
    ]
    apartment_settlement = manager.create_apartment_settlement('apart-polanka', 2025, 1)
    # czynsz 900, media 210, razem 1110

    # 2 najemców (trzeci należy do innego mieszkania, więc nie dzielimy z nim kosztów)
    manager.tenants = {
        'tenant-1': make_tenant('Jan Nowak'),
        'tenant-2': make_tenant('Adam Kowalski'),
        'tenant-3': make_tenant('Ewa Adamska', 'other-apart'),
    }

    settlements = manager.create_tenant_settlements(apartment_settlement)

    # 2 najemców - podział kosztów
    assert len(settlements) == 2
    assert {s.tenant for s in settlements} == {'tenant-1', 'tenant-2'}
    for s in settlements:
        assert isinstance(s, TenantSettlement)
        assert s.apartment_settlement == 'apart-polanka'
        assert s.month == 1
        assert s.year == 2025
        assert s.rent_pln == 450.0
        assert s.bills_pln == 105.0
        assert s.total_due_pln == 555.0
        assert s.balance_pln == -555.0   # brak przelewów

    # 1 najemca - ponosi całość kosztów
    manager.tenants = {'tenant-1': make_tenant('Jan Nowak')}
    settlements = manager.create_tenant_settlements(apartment_settlement)
    assert len(settlements) == 1
    assert settlements[0].tenant == 'tenant-1'
    assert settlements[0].rent_pln == 900.0
    assert settlements[0].bills_pln == 210.0
    assert settlements[0].total_due_pln == 1110.0

    # brak najemców w tym mieszkaniu - nie tworzymy rozliczeń
    manager.tenants = {'tenant-3': make_tenant('Ewa Adamska', 'other-apart')}
    assert manager.create_tenant_settlements(apartment_settlement) == []
    manager.tenants = {}
    assert manager.create_tenant_settlements(apartment_settlement) == []