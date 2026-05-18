"""CSV and PDF export/report generation."""
from __future__ import annotations

import csv
import io

from django.utils import timezone

from apps.integrations.models import ExportJob
from apps.integrations.pdf.generator import generate_document_pdf, generate_recall_notice_pdf
from apps.integrations.storage.backends import save_integration_file
from apps.operations.models import RegulatorOperationalHistory, WorkflowTimelineEntry
from apps.traceability.models import BatchRecall


def create_export_job(
    *,
    report_type: str,
    export_format: str,
    organisation=None,
    requested_by=None,
) -> ExportJob:
    return ExportJob.objects.create(
        report_type=report_type,
        export_format=export_format,
        organisation=organisation,
        requested_by=requested_by,
        created_by=requested_by,
    )


def run_export_job(*, job: ExportJob) -> ExportJob:
    try:
        if job.export_format == ExportJob.EXPORT_CSV:
            content, count = _build_csv(job.report_type, job.organisation_id)
            ext = "csv"
        else:
            content, count = _build_pdf(job.report_type, job.organisation_id)
            ext = "pdf"
        key = save_integration_file(
            folder=f"exports/{job.report_type}",
            filename=f"{job.id}.{ext}",
            content=content,
            content_type="text/csv" if ext == "csv" else "application/pdf",
        )
        job.file_path = key
        job.storage_key = key
        job.row_count = count
        job.job_status = ExportJob.STATUS_COMPLETED
        job.save(update_fields=["file_path", "storage_key", "row_count", "job_status", "updated_at"])
    except Exception as exc:
        job.job_status = ExportJob.STATUS_FAILED
        job.error_message = str(exc)[:500]
        job.save(update_fields=["job_status", "error_message", "updated_at"])
    return job


def _build_csv(report_type: str, organisation_id) -> tuple[bytes, int]:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    count = 0
    if report_type == ExportJob.REPORT_AUDIT:
        writer.writerow(["action_type", "summary", "created_at"])
        qs = RegulatorOperationalHistory.objects.order_by("-created_at")
        if organisation_id:
            qs = qs.filter(organisation_id=organisation_id)
        for row in qs[:500]:
            writer.writerow([row.action_type, row.summary[:200], row.created_at.isoformat()])
            count += 1
    elif report_type == ExportJob.REPORT_TRACEABILITY:
        writer.writerow(["workflow_type", "title", "created_at"])
        qs = WorkflowTimelineEntry.objects.order_by("-created_at")
        if organisation_id:
            qs = qs.filter(organisation_id=organisation_id)
        for row in qs[:500]:
            writer.writerow([row.workflow_type, row.title, row.created_at.isoformat()])
            count += 1
    else:
        writer.writerow(["report", "generated_at"])
        writer.writerow([report_type, timezone.now().isoformat()])
        count = 1
    return buffer.getvalue().encode("utf-8"), count


def _build_pdf(report_type: str, organisation_id) -> tuple[bytes, int]:
    if report_type == ExportJob.REPORT_RECALL:
        recall = BatchRecall.objects.order_by("-effective_at").first()
        if recall:
            content = generate_recall_notice_pdf(recall_code=str(recall.id)[:8], reason=recall.recall_reason[:200])
            return content, 1
    lines = [f"Report: {report_type}", f"Generated: {timezone.now().isoformat()}"]
    if organisation_id:
        lines.append(f"Organisation: {organisation_id}")
    return generate_document_pdf(title=f"NPTTE {report_type.title()} Report", lines=lines), 1
