"""Operational document upload with local storage abstraction."""
from __future__ import annotations

from django.core.files.uploadedfile import UploadedFile

from apps.operations.models import OperationalDocument
from apps.operations.services.workflow import record_workflow_event


def save_operational_document(
    *,
    organisation,
    document_type: str,
    title: str,
    uploaded_file: UploadedFile,
    uploaded_by=None,
) -> OperationalDocument:
    doc = OperationalDocument(
        organisation=organisation,
        document_type=document_type,
        title=title or uploaded_file.name,
        original_filename=uploaded_file.name,
        file_size=uploaded_file.size or 0,
        content_type=getattr(uploaded_file, "content_type", "") or "",
        uploaded_by=uploaded_by,
        created_by=uploaded_by,
    )
    doc.file.save(uploaded_file.name, uploaded_file, save=False)
    if not doc.storage_key:
        doc.storage_key = doc.file.name
    doc.save()

    record_workflow_event(
        workflow_type="document",
        title=f"Document uploaded: {doc.title}",
        summary=f"{document_type} — {doc.original_filename}",
        organisation=organisation,
        actor=uploaded_by,
        entity_type="operational_document",
        entity_id=doc.id,
        created_by=uploaded_by,
        record_feed=True,
    )
    return doc
