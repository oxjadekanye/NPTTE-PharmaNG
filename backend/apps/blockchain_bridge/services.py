"""Blockchain anchoring service stub."""
import hashlib
import json

from apps.blockchain_bridge.models import BlockchainAnchor


def queue_anchor(*, entity_type: str, entity_id, payload: dict) -> BlockchainAnchor:
    """Queue entity for future Hyperledger anchoring."""
    payload_hash = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
    return BlockchainAnchor.objects.create(
        entity_type=entity_type,
        entity_id=entity_id,
        payload_hash=payload_hash,
        anchor_status="pending",
    )
