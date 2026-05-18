from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.serialization.gs1 import decode_gs1_scan
from apps.serialization.models import ProductSerial, SerialPackagingUnit, SerialScanRecord
from apps.serialization.operations import build_printable_label, create_packaging_unit, record_serial_scan


class SerializationDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        total = ProductSerial.objects.count()
        scanned = ProductSerial.objects.filter(scan_count__gt=0).count()
        suspicious_count = SerialScanRecord.objects.filter(is_suspicious=True).count()
        packaging = SerialPackagingUnit.objects.count()
        return api_response(
            data={
                "total_serials": total,
                "serials_with_scans": scanned,
                "suspicious_scan_events": suspicious_count,
                "packaging_units": packaging,
                "duplicate_scans_24h": SerialScanRecord.objects.filter(is_duplicate=True).count(),
            },
            message="Serialization operations dashboard",
        )


class SerializationDecodeScanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        raw = request.data.get("raw_scan") or request.data.get("payload") or ""
        decoded = decode_gs1_scan(raw)
        return api_response(
            data={
                "gtin": decoded.gtin,
                "serial": decoded.serial,
                "national_serial": decoded.national_serial,
                "batch": decoded.batch,
                "expiry": decoded.expiry,
                "format_hint": decoded.format_hint,
            },
            message="Scan decoded",
        )


class SerializationLabelView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request, serial_id):
        serial = ProductSerial.objects.select_related("batch", "batch__product").get(pk=serial_id)
        return api_response(data=build_printable_label(product_serial=serial), message="Printable label payload")


class SerializationPackagingCreateView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request):
        from apps.products.models import ProductBatch

        batch = ProductBatch.objects.get(pk=request.data["batch_id"])
        level = request.data.get("level", SerialPackagingUnit.LEVEL_CARTON)
        parent_id = request.data.get("parent_id")
        parent = SerialPackagingUnit.objects.filter(pk=parent_id).first() if parent_id else None
        serial_ids = request.data.get("serial_ids") or []
        unit = create_packaging_unit(
            batch=batch,
            level=level,
            parent=parent,
            serial_ids=serial_ids,
            actor=request.user,
        )
        return api_response(
            data={"pack_code": unit.pack_code, "level": unit.level, "serial_count": unit.serial_count},
            message="Packaging unit created",
            status_code=201,
        )


class SerializationScanHistoryView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        serial = request.query_params.get("serial_number")
        qs = SerialScanRecord.objects.order_by("-created_at")[:100]
        if serial:
            qs = qs.filter(serial_number=serial)
        rows = [
            {
                "serial_number": r.serial_number,
                "scan_source": r.scan_source,
                "outcome": r.outcome,
                "is_duplicate": r.is_duplicate,
                "is_suspicious": r.is_suspicious,
                "created_at": r.created_at.isoformat(),
            }
            for r in qs
        ]
        return api_response(data={"scans": rows, "count": len(rows)}, message="Serial scan history")
