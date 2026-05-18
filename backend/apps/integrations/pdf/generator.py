"""Server-side PDF generation with optional QR embedding."""
from __future__ import annotations

import io
from typing import Iterable


def _pdf_via_reportlab(*, title: str, lines: Iterable[str], qr_data: str | None = None) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 30 * mm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20 * mm, y, title[:80])
    y -= 12 * mm
    c.setFont("Helvetica", 11)
    for line in lines:
        if y < 20 * mm:
            c.showPage()
            y = height - 30 * mm
            c.setFont("Helvetica", 11)
        c.drawString(20 * mm, y, str(line)[:100])
        y -= 7 * mm
    if qr_data:
        try:
            import qrcode
            from reportlab.lib.utils import ImageReader

            img = qrcode.make(qr_data)
            qr_buf = io.BytesIO()
            img.save(qr_buf, format="PNG")
            qr_buf.seek(0)
            c.drawImage(ImageReader(qr_buf), width - 55 * mm, 20 * mm, 35 * mm, 35 * mm)
        except ImportError:
            c.drawString(20 * mm, 15 * mm, f"QR: {qr_data[:60]}")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def _pdf_minimal(*, title: str, lines: Iterable[str], qr_data: str | None = None) -> bytes:
    """Minimal valid PDF without external dependencies."""
    content_lines = [f"({title}) Tj", "0 -14 Td"]
    for line in lines:
        safe = str(line).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content_lines.append(f"({safe[:90]}) Tj")
        content_lines.append("0 -14 Td")
    if qr_data:
        safe_qr = qr_data.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content_lines.append(f"(QR: {safe_qr[:60]}) Tj")
    stream = "\nBT /F1 12 Tf 50 750 Td\n" + "\n".join(content_lines) + "\nET"
    stream_bytes = stream.encode("latin-1", errors="replace")
    pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>>>"
        b"/Contents 4 0 R>>endobj\n"
        b"4 0 obj<</Length " + str(len(stream_bytes)).encode() + b">>stream\n" + stream_bytes + b"\nendstream\nendobj\n"
        b"xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000052 00000 n \n0000000101 00000 n \n0000000280 00000 n \n"
        b"trailer<</Size 5/Root 1 0 R>>\nstartxref\n380\n%%EOF"
    )
    return pdf


def generate_document_pdf(*, title: str, lines: Iterable[str], qr_data: str | None = None) -> bytes:
    try:
        import reportlab  # noqa: F401

        return _pdf_via_reportlab(title=title, lines=lines, qr_data=qr_data)
    except ImportError:
        return _pdf_minimal(title=title, lines=lines, qr_data=qr_data)


def generate_qr_label_pdf(*, serial_number: str, product_name: str = "", batch_number: str = "") -> bytes:
    lines = [
        f"Serial: {serial_number}",
        f"Product: {product_name or 'N/A'}",
        f"Batch: {batch_number or 'N/A'}",
        "NPTTE PharmaNG — Sovereign Traceability",
    ]
    verify_url = f"https://verify.nptte.gov.ng/?serial={serial_number}"
    return generate_document_pdf(title="NPTTE QR Label", lines=lines, qr_data=verify_url)


def generate_batch_certificate_pdf(*, batch_number: str, product_name: str, regulator_status: str) -> bytes:
    return generate_document_pdf(
        title="Batch Regulatory Certificate",
        lines=[
            f"Batch: {batch_number}",
            f"Product: {product_name}",
            f"Status: {regulator_status}",
            "Issued by NPTTE National Platform",
        ],
    )


def generate_recall_notice_pdf(*, recall_code: str, reason: str) -> bytes:
    return generate_document_pdf(
        title="National Recall Notice",
        lines=[f"Recall: {recall_code}", f"Reason: {reason}", "Immediate quarantine required."],
    )
