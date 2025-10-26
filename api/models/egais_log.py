from tortoise.models import Model
from tortoise import fields


class EgaisLog(Model):
    id = fields.IntField(pk=True)
    timestamp = fields.DatetimeField(auto_now_add=True)
    order_data = fields.JSONField(null=True)
    xml_data = fields.TextField(null=True)
    response_data = fields.TextField(null=True)
    qr_code = fields.TextField(null=True)
    sign = fields.TextField(null=True)  # Подпись из ответа ЕГАИС
    status = fields.CharField(max_length=20)
    error = fields.TextField(null=True)
    xml_file = fields.CharField(max_length=255, null=True)
    saved_file = fields.CharField(max_length=255, null=True)
    legacynum = fields.CharField(max_length=100, null=True)  # Order.num

    class Meta:
        table = "egais_logs"
