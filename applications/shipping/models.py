from tortoise import fields, models
import uuid


class Courier(models.Model):
    id = fields.UUIDField(pk=True, editable=False, hidden=True)
    name = fields.CharField(max_length=100, null=True, unique=True)
    image = fields.CharField(max_length=400, null=True)
    status = fields.BooleanField(default=True)
    is_default = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class City(models.Model):
    id = fields.UUIDField(pk=True, editable=False, hidden=True)
    name = fields.CharField(max_length=100, null=True, unique=True)
    delivery_charge = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    pathao_city_id = fields.CharField(max_length=100, null=True, unique=True)
    carrybee_city_id = fields.CharField(max_length=100, null=True, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class SubCity(models.Model):
    id = fields.UUIDField(pk=True, editable=False, hidden=True)
    name = fields.CharField(max_length=100, null=True, unique=True)
    city = fields.ForeignKeyField("models.City", related_name="subcities", on_delete=fields.CASCADE)
    pathao_subcity_id = fields.CharField(max_length=100, null=True, unique=True)
    carrybee_subcity_id = fields.CharField(max_length=100, null=True, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class OrderSource(models.Model):
    id = fields.UUIDField(pk=True, editable=False, hidden=True)
    name = fields.CharField(max_length=100, null=True, unique=True)
    status = fields.BooleanField(default=True)
    is_default = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name
    


class Comment(models.Model):
    id = fields.UUIDField(pk=True, editable=False, hidden=True)
    comment = fields.TextField(null=True)
    status = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.comment