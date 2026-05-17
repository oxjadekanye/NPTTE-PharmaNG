"""Traceability validators."""
from django.core.exceptions import ValidationError

from apps.core.constants import SupplyChainTransactionType


def validate_transaction_type(value: str) -> None:
    valid = {c for c, _ in SupplyChainTransactionType.CHOICES}
    if value not in valid:
        raise ValidationError(f"Invalid transaction type: {value}")
