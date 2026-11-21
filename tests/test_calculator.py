import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.calculator import SmartFinancialCalculator
from src.pattern_learner import InvoicePatternLearner


def test_tax_calculations():
    res = SmartFinancialCalculator.calculate_invoice_taxes(1000.0, vat_rate=0.23, income_tax_rate=0.12)
    assert res["vat"] == 230.0
    assert res["brutto"] == 1230.0
    assert res["zysk_na_reke"] == 880.0


def test_anomaly_detection():
    history = [5000.0, 5000.0, 5000.0]
    assert SmartFinancialCalculator.detect_anomaly(5100.0, history) is False
    assert SmartFinancialCalculator.detect_anomaly(7500.0, history) is True


def test_pattern_learning(tmp_path):
    test_file = tmp_path / "test_invoices.json"
    learner = InvoicePatternLearner(str(test_file))
    learner.add_invoice("Klient A", 3000.0, 0.23, "Serwis")
    learner.add_invoice("Klient A", 3000.0, 0.23, "Serwis")

    template = learner.predict_monthly_template("Klient A")
    assert template is not None
    assert template["suggested_net_amount"] == 3000.0