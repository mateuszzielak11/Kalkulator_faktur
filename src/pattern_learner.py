import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class InvoicePatternLearner:
    def __init__(self, history_file: str = "data/invoices_history.json"):
        self.history_path = Path(history_file)
        self.history: List[Dict] = self._load_history()

    def _load_history(self) -> List[Dict]:
        """NFR3: Odporność na brak pliku - zwraca pustą listę zamiast błędu."""
        if not self.history_path.exists():
            return []
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def add_invoice(self, client: str, net_amount: float, vat_rate: float, description: str) -> None:
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "day_of_month": datetime.now().day,
            "client": client,
            "net_amount": net_amount,
            "vat_rate": vat_rate,
            "description": description,
        }
        self.history.append(entry)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def predict_monthly_template(self, client: str) -> Optional[Dict]:
        """FR1: Uczy się wzorca dla kontrahenta na podstawie historii."""
        client_invoices = [inv for inv in self.history if inv["client"].lower() == client.lower()]
        if not client_invoices:
            return None

        # Znajdź najczęściej powtarzającą się kwotę, stawkę VAT i opis
        most_common_amount = Counter(inv["net_amount"] for inv in client_invoices).most_common(1)[0][0]
        most_common_vat = Counter(inv["vat_rate"] for inv in client_invoices).most_common(1)[0][0]
        most_common_desc = Counter(inv["description"] for inv in client_invoices).most_common(1)[0][0]
        avg_day = round(sum(inv["day_of_month"] for inv in client_invoices) / len(client_invoices))

        return {
            "client": client_invoices[-1]["client"],
            "suggested_net_amount": most_common_amount,
            "suggested_vat_rate": most_common_vat,
            "suggested_description": most_common_desc,
            "typical_billing_day": avg_day,
            "confidence_samples": len(client_invoices),
        }