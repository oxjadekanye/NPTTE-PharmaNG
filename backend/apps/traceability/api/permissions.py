from apps.core.permissions import IsOrganisationMember, IsRegulatorUser


class CanRecordTransaction(IsOrganisationMember):
    message = "Supply chain actor membership required to record transactions."


class CanViewNationalTraceability(IsRegulatorUser):
    message = "Regulator access required for national traceability views."
