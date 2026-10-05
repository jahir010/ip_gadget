from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile
from tortoise.transactions import in_transaction
from applications.order.models import OrderStatus, OrderSource, PaymentMethod, PaymentStatus, Order, OrderHistory
from typing import Optional, Any, List
from decimal import Decimal
import datetime
import json
from applications.products.models import Product
from applications.user.models import User
from app.auth import permission_required, get_current_user



router = APIRouter(prefix="/v1")


#--------------------Serializers----------------------#

async def _serialize_order(order: Order) -> dict:
    await order.fetch_related("city", "subcity")
    return {
        "id": str(order.id),
        "invoice_no": order.invoice_no,
        "merchant_order_id": order.merchant_order_id,
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "customer_address": order.customer_address,
        "city": {
            "id": str(order.city.id),
            "name": order.city.name,
        } if order.city else None,
        "subcity": {
            "id": str(order.subcity.id),
            "name": order.subcity.name,
        } if order.subcity else None,
        "products": order.products,
        "subtotal": float(order.subtotal),
        "discount_amount": float(order.discount_amount),
        "delivery_charge": float(order.delivery_charge),
        "grand_total": float(order.grand_total),
        "paid_amount": float(order.paid_amount),
        "due_amount": float(order.due_amount),
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "status": order.status,
        "order_source": order.order_source,
        "note": order.note,
        "meta": order.meta,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
    }


async def _serialize_order_history(order_history: OrderHistory) -> dict:
    await order_history.fetch_related("changed_by")
    return {
        "id": str(order_history.id),
        "order_id": str(order_history.order_id),
        "previous_status": order_history.previous_status,
        "current_status": order_history.current_status,
        "changed_by": {
            "id": str(order_history.changed_by.id),
            "name": getattr(order_history.changed_by, "name", None),
        } if order_history.changed_by else None,
        "note": order_history.note,
        "created_at": order_history.created_at.isoformat() if order_history.created_at else None,
    }



def generate_invoice_number() -> str:
    now = datetime.datetime.now()
    return f"INV-{now.strftime('%Y%m%d%H%M%S')}"




#-----------------------Order Endpoints----------------------------

@router.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint is working!"}


# @router.get("/orders", tags=["Orders"])
# async def order_list(
#     query: str = Form(None),
#     status: Optional[OrderStatus] = Form(None),
#     to_date: datetime = Form(None),
#     from_date: datetime = Form(None),
#     creator: str =Form(None),
#     user: User = Depends(permission_required("view_order"))
# ):
#     query = await Order.all()
#     return [await _serialize_order(order) for order in query]




# @router.post("/orders", tags=["Orders"])
# async def create_cutomer_order(
#     phone: str = Form(...),
#     name: str = Form(None),
#     address: str = Form(None),
#     # product: List[str] = Form(...),
#     sub_total: str = Form(...),
#     discount: float = Form(None),
#     delivery_charge: float = Form(default=0.0),
#     grand_total: float = Form(...),
# ):
#     order = Order.create(
#         customer_phone = phone,
#         cutomer_name = name,
#         customer_address = address,
#         # products = product,
#         subtotal = sub_total, 
#         discount = discount,
#         delivery_charge = delivery_charge,
#         grand_total = grand_total     
#     )

#     User.create(phone=phone, name=name)

#     return await _serialize_order(order)


@router.post("/orders/customers", tags=["Orders"])
async def create_customer_order(
    phone: str = Form(...),
    name: str | None = Form(None),
    address: str | None = Form(None),
    city_id: str = Form(...),
    subcity_id: str = Form(...),
    product: str = Form(...),
    sub_total: Decimal = Form(...),
    discount: Decimal = Form(Decimal("0")),
    delivery_charge: Decimal = Form(Decimal("0")),
    grand_total: Decimal = Form(...),
):
    try:
        products: list[dict[str, Any]] = json.loads(product)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Invalid product JSON")

    async with in_transaction():
        order = await Order.create(
            invoice_no=generate_invoice_number(),
            customer_phone=phone,
            customer_name=name or "",
            customer_address=address or "",
            city_id=city_id,
            subcity_id=subcity_id,
            products=products,
            subtotal=sub_total,
            discount_amount=discount,
            delivery_charge=delivery_charge,
            grand_total=grand_total,
            due_amount=grand_total,
        )
        await User.get_or_create(phone=phone, defaults={"name": name})

    return await _serialize_order(order)



@router.post("/orders/admin", tags=["Orders"])
async def create_admin_order(
    phone: str = Form(...),
    name: str | None = Form(None),
    address: str | None = Form(None),
    city_id: str = Form(...),
    subcity_id: str = Form(...),
    product: str = Form(...),
    sub_total: Decimal = Form(...),
    discount: Decimal = Form(Decimal("0")),
    delivery_charge: Decimal = Form(Decimal("0")),
    grand_total: Decimal = Form(...),
):
    try:
        products: list[dict[str, Any]] = json.loads(product)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Invalid product JSON")

    async with in_transaction():
        order = await Order.create(
            invoice_no=generate_invoice_number(),
            customer_phone=phone,
            customer_name=name or "",
            customer_address=address or "",
            city_id=city_id,
            subcity_id=subcity_id,
            products=products,
            subtotal=sub_total,
            discount_amount=discount,
            delivery_charge=delivery_charge,
            grand_total=grand_total,
            due_amount=grand_total,
        )
        await User.get_or_create(phone=phone, defaults={"name": name})

    return await _serialize_order(order)