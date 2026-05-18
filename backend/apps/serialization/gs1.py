"""
Phase 10 — GS1-compatible serial encoding and scan decoding (additive).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Gs1DecodedScan:
    """Parsed elements from a GS1 DataMatrix / QR / linear barcode payload."""

    raw: str
    gtin: str = ""
    serial: str = ""
    batch: str = ""
    expiry: str = ""
    national_serial: str = ""
    format_hint: str = "unknown"


def _digits_only(value: str, length: int) -> str:
    return re.sub(r"\D", "", value)[:length]


def build_gs1_element_string(*, gtin: str, serial: str, batch: str = "", expiry: str = "") -> str:
    """
    Build a GS1 element string (AI 01, 21, 10, 17) for QR embedding.
    GTIN should be 14 digits (padded); serial is AI (21).
    """
    gtin14 = _digits_only(gtin, 14).zfill(14)
    parts = [f"01{gtin14}", f"21{serial}"]
    if batch:
        parts.append(f"10{batch[:20]}")
    if expiry:
        exp = _digits_only(expiry, 6)
        if len(exp) == 6:
            parts.append(f"17{exp}")
    return "".join(parts)


def build_nptte_serial_with_gs1(*, product, national_serial: str) -> dict:
    """Return GS1 fields alongside national NPTTE serial."""
    gtin = getattr(product, "gtin", None) or getattr(product, "national_product_code", "") or ""
    gtin14 = _digits_only(gtin, 14).zfill(14) if gtin else "00000000000000"
    batch_no = ""
    element = build_gs1_element_string(gtin=gtin14, serial=national_serial, batch=batch_no)
    return {
        "gtin14": gtin14,
        "gs1_element_string": element,
        "gs1_digital_link_path": f"/01/{gtin14}/21/{national_serial}",
    }


def decode_gs1_scan(raw: str) -> Gs1DecodedScan:
    """
    Decode GS1 element string, NPTTE verify URL, or plain national serial.
    """
    text = (raw or "").strip()
    result = Gs1DecodedScan(raw=text)

    if not text:
        return result

    # NPTTE verify URL or path
    if "NG-NPTTE" in text.upper():
        m = re.search(r"(NG-NPTTE-[A-Z0-9-]+)", text.upper())
        if m:
            result.national_serial = m.group(1)
            result.serial = m.group(1)
            result.format_hint = "nptte_url"
            return result

    if text.upper().startswith("NG-NPTTE-"):
        result.national_serial = text.upper()
        result.serial = text.upper()
        result.format_hint = "nptte_serial"
        return result

    # GS1 digital link style /01/{gtin}/21/{serial}
    dl = re.search(r"/01/(\d{14})/21/([^/?\s]+)", text)
    if dl:
        result.gtin = dl.group(1)
        result.serial = dl.group(2)
        result.national_serial = dl.group(2)
        result.format_hint = "gs1_digital_link"
        return result

    # Parenthesized GS1 (human readable)
    for ai, key in (("01", "gtin"), ("21", "serial"), ("10", "batch"), ("17", "expiry")):
        m = re.search(rf"\({ai}\)([^()]+)", text)
        if m:
            setattr(result, key, m.group(1).strip())

    # Concatenated AIs without parentheses
    if not result.gtin:
        m = re.match(r"01(\d{14})", text)
        if m:
            result.gtin = m.group(1)
            rest = text[m.end() :]
            m21 = re.match(r"21([^10|17]+)", rest)
            if m21:
                result.serial = m21.group(1).strip()
                result.national_serial = result.serial

    if result.serial and not result.national_serial:
        result.national_serial = result.serial
    if result.gtin or result.serial:
        result.format_hint = "gs1_element"
    return result


def resolve_serial_from_scan(raw: str) -> str:
    """National registry lookup key from any supported scan format."""
    decoded = decode_gs1_scan(raw)
    return decoded.national_serial or decoded.serial or raw.strip()
