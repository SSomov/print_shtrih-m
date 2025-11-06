from tortoise.models import Model
from tortoise import fields


class Product(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    category = fields.ForeignKeyField('models.Category', related_name='products', on_delete=fields.CASCADE)
    
    # Основные поля товара
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    barcode = fields.CharField(max_length=50, null=True)  # EAN
    legacy_path = fields.CharField(max_length=120, null=True)  # Путь из старой системы
    unit = fields.CharField(max_length=20, default="шт")  # Единица измерения
    legacy_id = fields.CharField(max_length=100, null=True)  # ID из старой системы (1С)
    
    # Скидки и налоги
    max_discount = fields.DecimalField(max_digits=5, decimal_places=2, default=100)  # Максимальная скидка в %
    tax_rate = fields.DecimalField(max_digits=5, decimal_places=2, default=20)  # НДС в %
    
    # Алкогольные товары
    is_alcohol = fields.BooleanField(default=False)  # alco
    is_marked = fields.BooleanField(default=False)  # mark - маркированный товар
    is_draught = fields.BooleanField(default=False)  # draught - разливное
    is_bottled = fields.BooleanField(default=False)  # bottled - бутылочное
    
    # ЕГАИС поля
    alc_code = fields.CharField(max_length=100, null=True)  # Алкокод продукции
    egais_mark_code = fields.CharField(max_length=255, null=True)  # Код марки для ЕГАИС
    gtin = fields.CharField(max_length=50, null=True)  # GTIN для маркированных товаров
    
    # Статус
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "products"
