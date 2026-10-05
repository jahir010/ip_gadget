# from tortoise import fields, models
# import uuid
# import enum



# class OrderStatus(enum.Enum):
#     NEW = "new"
#     INCOMPLETE = "incomplete"
#     PENDING = "pending"
#     ADMIN = "admin"
#     EXCHANGE = "exchange"
#     APPROVED = "approved"
#     WAITING_FOR_PACKAGING = "waiting_for_packaging"
#     PACKAGING = "packaging"
#     SHIPMENT = "shipment"
#     PARTIAL_DELIVERED = "partial_delivered"
#     DELIVERED = "delivered"
#     RETURNED = "returned"
#     RETURN_PENDING = "return_pending"
#     CANCELLED = "cancelled"



# class Order(models.Model): 
#     id = fields.UUIDField(pk=True, default=uuid.uuid4)
#     customer_name = fields.CharField(max_length=255)
#     customer_phone = fields.CharField(max_length=20)
#     customer_address = fields.TextField()
#     product = fields.JSONField()
#     city = fields.ForeignKeyField("models.City", related_name="orders")
#     subcity = fields.ForeignKeyField("models.SubCity", related_name="orders")
#     delivery_charge = fields.DecimalField(max_digits=10, decimal_places=2, default=0.0)
#     total_amount = fields.DecimalField(max_digits=10, decimal_places=2, )
#     discount = fields.DecimalField(max_digits=10, decimal_places=2, default=0.0)
#     total_sell_price = fields.DecimalField(max_digits=10, decimal_places=2, default=0.0)
#     paid_amount = fields.DecimalField(max_digits=10, decimal_places=2, default=0.0)
#     payment_method = fields.CharField(max_length=50, default="cash_on_delivery")
#     payment_status = fields.CharField(max_length=50, default="unpaid")
#     status = fields.CharEnumField(OrderStatus)
#     order_source = fields.CharField(max_length=100, default="website", null=True, blank=True)
#     note = fields.CharField(max_length=255, null=True, blank=True)
#     meta = fields.JSONField(null=True, blank=True)
#     created_at = fields.DatetimeField(auto_now_add=True)
#     updated_at = fields.DatetimeField(auto_now=True)

#     class Meta:
#         table = "orders"





from tortoise import fields, models
import enum
import uuid


# ==========================================================
# ORDER STATUS
# ==========================================================

class OrderStatus(str, enum.Enum):
    NEW = "new"
    INCOMPLETE = "incomplete"
    PENDING = "pending"
    ADMIN = "admin"
    EXCHANGE = "exchange"
    APPROVED = "approved"
    WAITING_FOR_PACKAGING = "waiting_for_packaging"
    PACKAGING = "packaging"
    SHIPMENT = "shipment"
    PARTIAL_DELIVERED = "partial_delivered"
    DELIVERED = "delivered"
    RETURNED = "returned"
    RETURN_PENDING = "return_pending"
    CANCELLED = "cancelled"


# ==========================================================
# PAYMENT
# ==========================================================

class PaymentMethod(str, enum.Enum):
    CASH_ON_DELIVERY = "cash_on_delivery"
    BKASH = "bkash"
    NAGAD = "nagad"
    ROCKET = "rocket"
    CARD = "card"
    BANK = "bank"


class PaymentStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"
    REFUNDED = "refunded"


# ==========================================================
# ORDER SOURCE
# ==========================================================

class OrderSource(str, enum.Enum):
    WEBSITE = "website"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    WHATSAPP = "whatsapp"
    PHONE = "phone"
    ADMIN = "admin"


# ==========================================================
# ORDER
# ==========================================================

class Order(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    invoice_no = fields.CharField(max_length=50,unique=True)
    merchant_order_id = fields.CharField(max_length=100,unique=True,null=True)
    customer_name = fields.CharField(max_length=255)
    customer_phone = fields.CharField(max_length=20)
    customer_address = fields.TextField()
    city = fields.ForeignKeyField("models.City",related_name="orders")
    subcity = fields.ForeignKeyField( "models.SubCity",related_name="orders")
    products = fields.JSONField()
    subtotal = fields.DecimalField(max_digits=10,decimal_places=2)
    discount_amount = fields.DecimalField(max_digits=10,decimal_places=2,default=0)
    delivery_charge = fields.DecimalField(max_digits=10,decimal_places=2,default=0)
    grand_total = fields.DecimalField(max_digits=10,decimal_places=2)
    paid_amount = fields.DecimalField(max_digits=10,decimal_places=2,default=0)
    due_amount = fields.DecimalField(max_digits=10,decimal_places=2)
    payment_method = fields.CharEnumField(PaymentMethod,default=PaymentMethod.CASH_ON_DELIVERY)
    payment_status = fields.CharEnumField(PaymentStatus,default=PaymentStatus.UNPAID)
    status = fields.CharEnumField(OrderStatus,default=OrderStatus.NEW)
    order_source = fields.CharEnumField(OrderSource,default=OrderSource.WEBSITE)
    note = fields.TextField(null=True)
    meta = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "orders"

    def __str__(self):
        return self.invoice_no




class OrderHistory(models.Model):
    id = fields.UUIDField(pk=True,default=uuid.uuid4)
    order = fields.ForeignKeyField("models.Order",related_name="history",on_delete=fields.CASCADE)
    previous_status = fields.CharEnumField(OrderStatus,null=True)
    current_status = fields.CharEnumField(OrderStatus)
    changed_by = fields.ForeignKeyField("models.User",related_name="order_histories",null=True,on_delete=fields.SET_NULL)
    note = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "order_history"
        ordering = ["-created_at"]