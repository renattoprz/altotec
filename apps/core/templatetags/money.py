from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def soles(value) -> str:
    """Formato peruano: 1,699.00"""
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return ""
    return f"{amount:,.2f}"
