import pytest

from apps.audit.logging import redact
from apps.audit.models import AuditLog


@pytest.mark.django_db
def test_audit_log_is_immutable():
    entry = AuditLog.objects.create(actor="x", action="crear", entity="e", entity_id="1")
    entry.action = "otro"
    with pytest.raises(PermissionError):
        entry.save()
    with pytest.raises(PermissionError):
        entry.delete()
    with pytest.raises(PermissionError):
        AuditLog.objects.all().delete()


def test_logs_redact_personal_data():
    text = redact("cliente juan@mail.com dni 45678912 ruc 20123456789 cel 987654321")
    assert "juan@mail.com" not in text
    assert "45678912" not in text
    assert "20123456789" not in text
    assert "987654321" not in text
