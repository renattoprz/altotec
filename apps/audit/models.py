from django.db import models

from .context import current_actor, current_ip


class AuditLogQuerySet(models.QuerySet):
    def update(self, **kwargs):  # pragma: no cover - protección
        raise PermissionError("El registro de auditoría es inmutable.")

    def delete(self):  # pragma: no cover - protección
        raise PermissionError("El registro de auditoría es inmutable.")


class AuditLog(models.Model):
    """Registro inmutable de cambios sensibles (ISO 27001 A.8.15, SOC 2 CC7.2)."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    actor = models.CharField(max_length=150)
    ip = models.GenericIPAddressField(null=True, blank=True)
    action = models.CharField(max_length=60)
    entity = models.CharField(max_length=60)
    entity_id = models.CharField(max_length=64)
    changes = models.JSONField(default=dict, blank=True)

    objects = AuditLogQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "registro de auditoría"
        verbose_name_plural = "registro de auditoría"

    def __str__(self):
        return (
            f"{self.created_at:%Y-%m-%d %H:%M} {self.actor} {self.action} "
            f"{self.entity}#{self.entity_id}"
        )

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise PermissionError("El registro de auditoría es inmutable.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("El registro de auditoría es inmutable.")

    @classmethod
    def record(cls, *, action: str, instance: models.Model, changes: dict | None = None):
        return cls.objects.create(
            actor=current_actor.get(),
            ip=current_ip.get(),
            action=action,
            entity=instance._meta.label,
            entity_id=str(instance.pk),
            changes=changes or {},
        )


class AuditedModel(models.Model):
    """Modelo base: registra en AuditLog los cambios de los campos listados en AUDIT_FIELDS."""

    AUDIT_FIELDS: tuple[str, ...] = ()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        changes = {}
        is_new = self.pk is None
        if not is_new and self.AUDIT_FIELDS:
            previous = type(self).objects.filter(pk=self.pk).values(*self.AUDIT_FIELDS).first()
            if previous:
                for field in self.AUDIT_FIELDS:
                    old, new = previous[field], getattr(self, field)
                    if old != new:
                        changes[field] = [str(old), str(new)]
        super().save(*args, **kwargs)
        if is_new:
            AuditLog.record(action="crear", instance=self)
        elif changes:
            AuditLog.record(action="modificar", instance=self, changes=changes)
