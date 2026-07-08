from tortoise import fields, models
import uuid




class ProductCategory(models.Model):
    id = fields.UUIDField(pk=True, editable=False, hidden=True)
    name = fields.CharField(max_length=100, null=True, unique=True)
    parent = fields.ForeignKeyField("models.ProductCategory", related_name="subcategories", on_delete=fields.CASCADE, null=True)
    status = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class Attribute(models.Model):
    id = fields.UUIDField(pk=True, editable=False, hidden=True)
    name = fields.CharField(max_length=100, null=True, unique=True)
    status = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class Variant(models.Model):
    id = fields.UUIDField(pk=True, editable=False, hidden=True)
    name = fields.CharField(max_length=100, null=True, unique=True)
    attribute = fields.ForeignKeyField("models.Attribute", related_name="variants", on_delete=fields.CASCADE)
    status = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Brand(models.Model):
    id = fields.UUIDField(pk=True, editable=False, hidden=True)
    name = fields.CharField(max_length=100, null=True, unique=True)
    status = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class Product(models.Model):
    id = fields.UUIDField(pk=True, editable=False, hidden=True)
    name = fields.CharField(max_length=100, null=True, unique=True)
    image = fields.JSONField(null=True)
    details = fields.TextField(null=True)
    category = fields.ForeignKeyField("models.ProductCategory", related_name="products", on_delete=fields.CASCADE)
    status = fields.BooleanField(default=True)
    brand = fields.ForeignKeyField("models.Brand", related_name="products", on_delete=fields.CASCADE, null=True)
    video_url = fields.CharField(max_length=200, null=True)
    stock = fields.IntField(default=0)
    price = fields.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = fields.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    attributes = fields.JSONField(null=True)
    variants = fields.JSONField(null=True)
    free_delivery = fields.BooleanField(default=False)
    meta = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)



    def sell_price(self) -> float:
        """Calculate the selling price after discount."""
        return float(self.price) - float(self.discount)

    def __str__(self):
        return self.name