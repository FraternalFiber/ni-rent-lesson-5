from src.models import Apartment, Bill, Parameters, Tenant, Transfer, ApartmentSettlement


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key: str, year: int | None = None, month: int | None = None) -> float | None:
        if month is not None:
            if year is None:
                raise ValueError("Month can't be given without year")
            if not isinstance(month, int) or not 1 <= month <= 12:
                raise ValueError(f"Invalid month: {month}")
        
        if apartment_key not in self.apartments:
            return None

        total = sum(
            bill.amount_pln
            for bill in self.bills
            if bill.apartment == apartment_key
            and (year is None or bill.settlement_year == year)
            and (month is None or bill.settlement_month == month)
        )

        return round(total, 2)

    def create_apartment_settlement(self, apartment_key: str, year: int, month: int) -> ApartmentSettlement | None:
        if year is None or month is None:
            raise ValueError("Year and month are required")

        total_due = self.get_apartment_costs(apartment_key, year, month)

        if total_due is None:
            return None

        total_rent = sum(
            bill.amount_pln
            for bill in self.bills
            if bill.apartment == apartment_key
            and bill.settlement_year == year
            and bill.settlement_month == month
            and bill.type == 'rent'
        )

        return ApartmentSettlement(
            apartment = apartment_key,
            month = month,
            year = year,
            total_rent_pln = round(total_rent, 2),
            total_bills_pln = round(total_due - total_rent, 2),
            total_due_pln = total_due
        )