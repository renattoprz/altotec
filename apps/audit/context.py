"""Contexto de la petición actual (usuario e IP) para el registro de auditoría."""

from contextvars import ContextVar

current_actor: ContextVar[str] = ContextVar("current_actor", default="sistema")
current_ip: ContextVar[str | None] = ContextVar("current_ip", default=None)
