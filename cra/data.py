"""Loads the German Credit data: 1,000 real consumer credit applications with a good/bad outcome."""
from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

import pandas as pd

URL = "https://raw.githubusercontent.com/selva86/datasets/master/GermanCredit.csv"
CACHE = Path("data/german_credit.csv")

# Not used to make credit decisions (fair lending / risk governance); age is used only to report segments.
PROTECTED = ["personal_status_sex", "foreign_worker", "age"]
NUMERIC = ["duration", "amount", "installment_rate", "present_residence", "age", "number_credits", "people_liable"]

DATA_DICTIONARY = {
    "status": "Checking account balance at application",
    "duration": "Requested loan term in months",
    "credit_history": "Past repayment behaviour",
    "purpose": "Loan purpose",
    "amount": "Requested amount (DM)",
    "savings": "Savings account balance",
    "employment_duration": "Time with current employer",
    "installment_rate": "Instalment as % of disposable income (1 = low, 4 = high)",
    "other_debtors": "Co-applicant or guarantor",
    "property": "Most valuable property",
    "other_installment_plans": "Other instalment plans (bank, stores)",
    "housing": "Rent, own or free",
    "number_credits": "Existing credits at this bank",
    "job": "Job category",
    "bad": "Outcome: 1 = bad (defaulted), 0 = good",
}


def load(path: Path = CACHE) -> pd.DataFrame:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(URL, path)
    df = pd.read_csv(path)
    df["bad"] = 1 - df.pop("credit_risk")          # source: 1 = good, 0 = bad
    df.insert(0, "application_id", range(1, len(df) + 1))
    return df


def fingerprint(path: Path = CACHE) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]
