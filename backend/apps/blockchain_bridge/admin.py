from django.contrib import admin

from apps.blockchain_bridge.models import BlockchainAnchor


@admin.register(BlockchainAnchor)
class BlockchainAnchorAdmin(admin.ModelAdmin):
    list_display = ("entity_type", "entity_id", "anchor_status", "network", "created_at")
    list_filter = ("anchor_status", "network")
    readonly_fields = ("payload_hash", "created_at")
