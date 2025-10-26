from tortoise.models import Model
from tortoise import fields


class Category(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    description = fields.TextField(null=True)
    legacy_id = fields.CharField(max_length=100, null=True)  # ID из старой системы (1С)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "categories"
