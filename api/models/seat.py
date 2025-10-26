from tortoise.models import Model
from tortoise import fields


class Seat(Model):
    """Места размещения (столики, места под деревом и т.д.)"""
    id = fields.IntField(pk=True)
    number = fields.CharField(max_length=20)  # Номер места
    area = fields.ForeignKeyField('models.Area', related_name='seats', on_delete=fields.CASCADE)
    capacity = fields.IntField(default=4)  # Вместимость места
    description = fields.TextField(null=True)
    is_active = fields.BooleanField(default=True)
    is_occupied = fields.BooleanField(default=False)  # Занято ли
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "seats"
