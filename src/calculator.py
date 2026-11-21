
from typing import Dict, List


class SmartFinancialCalculator:
    @staticmethod
    def calculate_invoice_taxes(net_amount: float, vat_rate: float = 0.23, income_tax_rate: float = 0.12) -> Dict[str, float]:
        """FR2: Rozszerzone obliczenia VAT, Brutto, PIT oraz kwoty na rękę."""
        if net_amount < 0:
            raise ValueError("Kwota netto nie może być ujemna.")

        vat_amount = round(net_amount * vat_rate, 2)
        gross_amount = round(net_amount + vat_amount, 2)
        income_tax = round(net_amount * income_tax_rate, 2)
        real_profit = round(net_amount - income_tax, 2)

        return {
            "netto": round(net_amount, 2),
            "vat": vat_amount,
            "brutto": gross_amount,
            "podatek_dochodowy": income_tax,
            "zysk_na_reke": real_profit,
        }

    @staticmethod
    def detect_anomaly(new_amount: float, historical_amounts: List[float], threshold: float = 0.20) -> bool:
        """FR2: Wykrywa, czy nowa faktura odbiega o ponad 20% od średniej z poprzednich miesięcy."""
        if not historical_amounts:
            return False
        avg = sum(historical_amounts) / len(historical_amounts)
        if avg == 0:
            return False
        deviation = abs(new_amount - avg) / avg
        return deviation > threshold