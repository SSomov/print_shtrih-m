from tortoise.models import Model
from tortoise import fields


class CheckLog(Model):
    id = fields.IntField(pk=True)
    timestamp = fields.DatetimeField(auto_now_add=True)
    status = fields.CharField(max_length=20)
    message = fields.TextField(null=True)
    error = fields.TextField(null=True)
    order_data = fields.JSONField(null=True)
    result_code = fields.CharField(max_length=10, null=True)
    result_description = fields.TextField(null=True)
    filename = fields.CharField(max_length=255, null=True)
    document_number = fields.CharField(max_length=50, null=True)  # Номер чека
    fiscal_sign = fields.CharField(max_length=50, null=True)  # Фискальный признак
    legacynum = fields.CharField(max_length=100, null=True)  # Order.num

    class Meta:
        table = "check_logs"
