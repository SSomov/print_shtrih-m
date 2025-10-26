from tortoise.models import Model
from tortoise import fields


class Area(Model):
    """Области размещения (залы, помещения, территории)"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    description = fields.TextField(null=True)
    capacity = fields.IntField(null=True)  # Вместимость
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "areas"
