import os
import sys
from src.calculator import SmartFinancialCalculator
from src.pattern_learner import InvoicePatternLearner


def verify_service_principal_env() -> bool:
    """NFR1: Sprawdza obecność zmiennych środowiskowych Service Principal."""
    required_vars = ["AZURE_CLIENT_ID", "AZURE_TENANT_ID", "AZURE_CLIENT_SECRET"]
    return all(os.getenv(var) for var in required_vars)


def main():
    print("=== Inteligentny Kalkulator Faktur ===")
    sp_status = "AKTYWNY (autoryzacja z ENV)" if verify_service_principal_env() else "TRYB LOKALNY (brak zmiennych SP)"
    print(f"Status Service Principal: {sp_status}\n")

    learner = InvoicePatternLearner()
    calc = SmartFinancialCalculator()
    client_name = "Firma XYZ Sp. z o.o."

    # 1. Jeśli istnieje historia, pokaż czego kalkulator się nauczył (FR1)
    template = learner.predict_monthly_template(client_name)
    if template:
        print(f"[FR1] Wykryto schemat dla: {template['client']} (na bazie {template['confidence_samples']} faktur)")
        print(f"      Sugerowany opis: {template['suggested_description']}")
        print(f"      Sugerowana kwota netto: {template['suggested_net_amount']} PLN\n")
    else:
        print(f"[FR1] Brak historii dla {client_name}. Pierwsza faktura rozpocznie naukę wzorca.\n")

    # 2. Wpisanie nowej kwoty (w trybie CI/CD bez klawiatury użyje podpowiedzi lub domyślnej kwoty)
    if sys.stdin.isatty():
        default_val = template["suggested_net_amount"] if template else 5000.0
        user_input = input(f"Podaj kwotę netto nowej faktury [Enter = akceptuj {default_val} PLN]: ").strip()
        new_amount = float(user_input.replace(",", ".")) if user_input else default_val
    else:
        new_amount = template["suggested_net_amount"] if template else 5000.0

    # Sprawdzenie anomalii względem historii (FR2)
    historical_amounts = [inv["net_amount"] for inv in learner.history]
    if calc.detect_anomaly(new_amount, historical_amounts):
        print(f"\n[UWAGA - FR2] Wykryto anomalię! Kwota {new_amount} PLN odbiega o ponad 20% od średniej z poprzednich miesięcy!")

    # Zapisanie nowej faktury do bazy wiedzy (FR1)
    learner.add_invoice(client_name, new_amount, 0.23, "Usługi IT - abonament miesięczny")

    # Wyliczenie podatków dla nowej kwoty (FR2)
    taxes = calc.calculate_invoice_taxes(new_amount, 0.23)
    print(f"\n[FR2] Rozliczenie podatkowe dla kwoty {new_amount} PLN netto:")
    for k, v in taxes.items():
        print(f"      - {k.capitalize()}: {v} PLN")


if __name__ == "__main__":
    main()