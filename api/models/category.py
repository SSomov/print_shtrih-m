from tortoise.models import Model
from tortoise import fields


class Category(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    description = fields.TextField(null=True)
    legacy_id = fields.CharField(max_length=100, null=True)  # ID из старой системы (1С)
    parent = fields.ForeignKeyField('models.Category', related_name='children', null=True, on_delete=fields.SET_NULL)  # Родительская категория
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "categories"
