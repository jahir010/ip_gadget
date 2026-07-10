from fastapi import HTTPException, status, APIRouter, Depends, Form, UploadFile, File
from applications.shipping.models import Courier, City, SubCity, OrderSource, Comment
from app.auth import permission_required 
from app.utils.file_manager import save_file, update_file, delete_file
from applications.user.models import User


router = APIRouter(prefix="/shipping")



#-------------------------------- serialization ---------------------------------#


def _serialize_courier(courier: Courier):
    return {
        "id": str(courier.id),
        "name": courier.name,
        "image": courier.image,
        "status": courier.status,
        "is_default": courier.is_default,
        "created_at": courier.created_at.isoformat(),
        "updated_at": courier.updated_at.isoformat(),
    }

def _serialize_city(city: City):
    return {
        "id": str(city.id),
        "name": city.name,
        "delivery_charge": float(city.delivery_charge),
        "pathao_city_id": city.pathao_city_id,
        "carrybee_city_id": city.carrybee_city_id,
        "created_at": city.created_at.isoformat(),
        "updated_at": city.updated_at.isoformat(),
    }

def _serialize_subcity(subcity: SubCity):
    return {
        "id": str(subcity.id),
        "name": subcity.name,
        "city": _serialize_city(subcity.city),
        "pathao_subcity_id": subcity.pathao_subcity_id,
        "carrybee_subcity_id": subcity.carrybee_subcity_id,
        "created_at": subcity.created_at.isoformat(),
        "updated_at": subcity.updated_at.isoformat(),
    }

def _serialize_order_source(order_source: OrderSource):
    return {
        "id": str(order_source.id),
        "name": order_source.name,
        "status": order_source.status,
        "is_default": order_source.is_default,
        "created_at": order_source.created_at.isoformat(),
        "updated_at": order_source.updated_at.isoformat(),
    }

def _serialize_comment(comment: Comment):
    return {
        "id": str(comment.id),
        "comment": comment.comment,
        "status": comment.status,
        "created_at": comment.created_at.isoformat(),
        "updated_at": comment.updated_at.isoformat(),
    }   



#------------------------------- COURIER ENDPOINTS ---------------------------------#


@router.get("/couriers", tags=["couriers"])
async def get_couriers(user: User = Depends(permission_required("view_courier"))):
    couriers = await Courier.all()
    return [_serialize_courier(courier) for courier in couriers]

@router.post("/couriers", tags=["couriers"])
async def create_courier(
    name: str = Form(...),
    image: UploadFile = File(None),
    status: bool = Form(default=True),
    is_default: bool = Form(default=False),
    user: User = Depends(permission_required("add_courier"))
):
    # Check if a courier with the same name already exists
    existing_courier = await Courier.filter(name=name).first()
    if existing_courier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Courier with this name already exists."
        )

    # Save the uploaded image file
    if image is not None:
        image_path = await save_file(image, "couriers")
    else:
        image_path = None

    # Create a new courier instance
    courier = Courier(
        name=name,
        image=image_path,
        status=status,
        is_default=is_default
    )
    await courier.save()

    return _serialize_courier(courier)



@router.get("/couriers/{courier_id}", tags=["couriers"])
async def get_courier(courier_id: str, user: User = Depends(permission_required("view_courier"))):
    courier = await Courier.filter(id=courier_id).first()
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found."
        )
    return _serialize_courier(courier)


@router.patch("/couriers/{courier_id}", tags=["couriers"])
async def update_courier(
    courier_id: str,
    name: str = Form(...),
    image: UploadFile = File(None),
    status: bool = Form(None),
    is_default: bool = Form(None),
    user: User = Depends(permission_required("change_courier"))
):
    courier = await Courier.filter(id=courier_id).first()
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found."
        )

    # Check if a courier with the same name already exists (excluding the current courier)
    existing_courier = await Courier.filter(name=name).exclude(id=courier_id).first()
    if existing_courier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Courier with this name already exists."
        )

    # Update the courier's attributes
    courier.name = name
    if status is not None:
        courier.status = status
    if is_default is not None:
        courier.is_default = is_default

    
    if image is not None:
        image_path = await update_file(image, courier.image, "couriers")
        courier.image = image_path

    await courier.save()

    return _serialize_courier(courier)

@router.delete("/couriers/{courier_id}", tags=["couriers"])
async def delete_courier(courier_id: str, user: User = Depends(permission_required("delete_courier"))):
    courier = await Courier.filter(id=courier_id).first()
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found."
        )

    # Delete the courier's image file if it exists
    if courier.image:
        await delete_file(courier.image)

    await courier.delete()

    return {"detail": "Courier deleted successfully."}




#------------------------------- CITY ENDPOINTS ---------------------------------#

@router.get("/cities", tags=["cities"])
async def get_cities(user: User = Depends(permission_required("view_city"))):
    cities = await City.all()
    return [_serialize_city(city) for city in cities]

@router.post("/cities", tags=["cities"])
async def create_city(
    name: str = Form(...),
    delivery_charge: float = Form(default=0),
    pathao_city_id: str = Form(None),
    carrybee_city_id: str = Form(None),
    user: User = Depends(permission_required("add_city"))
):
    # Check if a city with the same name already exists
    existing_city = await City.filter(name=name).first()
    if existing_city:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City with this name already exists."
        )

    # Create a new city instance
    city = City(
        name=name,
        delivery_charge=delivery_charge,
        pathao_city_id=pathao_city_id,
        carrybee_city_id=carrybee_city_id
    )
    await city.save()

    return _serialize_city(city)


@router.get("/cities/{city_id}", tags=["cities"])
async def get_city(city_id: str, user: User = Depends(permission_required("view_city"))):
    city = await City.filter(id=city_id).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found."
        )
    return _serialize_city(city)

@router.patch("/cities/{city_id}", tags=["cities"])
async def update_city(
    city_id: str,
    name: str = Form(None),
    delivery_charge: float = Form(default=0),
    pathao_city_id: str = Form(None),
    carrybee_city_id: str = Form(None),
    user: User = Depends(permission_required("change_city"))
):
    city = await City.filter(id=city_id).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found."
        )

    # Check if a city with the same name already exists (excluding the current city)
    existing_city = await City.filter(name=name).exclude(id=city_id).first()
    if existing_city:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City with this name already exists."
        )

    # Update the city's attributes
    if name is not None:
        city.name = name
    if delivery_charge is not None:
        city.delivery_charge = delivery_charge
    if pathao_city_id is not None:
        city.pathao_city_id = pathao_city_id
    if carrybee_city_id is not None:
        city.carrybee_city_id = carrybee_city_id

    await city.save()

    return _serialize_city(city)


@router.delete("/cities/{city_id}", tags=["cities"])
async def delete_city(city_id: str, user: User = Depends(permission_required("delete_city"))):
    city = await City.filter(id=city_id).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found."
        )

    await city.delete()

    return {"detail": "City deleted successfully."}


#------------------------------- SUBCITY ENDPOINTS ---------------------------------#

@router.get("/subcities", tags=["subcities"])
async def get_subcities(user: User = Depends(permission_required("view_subcity"))):
    subcities = await SubCity.all().prefetch_related("city")
    return [_serialize_subcity(subcity) for subcity in subcities]

@router.post("/subcities", tags=["subcities"])
async def create_subcity(
    name: str = Form(...),
    city_id: str = Form(...),
    pathao_subcity_id: str = Form(None),
    carrybee_subcity_id: str = Form(None),
    user: User = Depends(permission_required("add_subcity"))
):
    # Check if a subcity with the same name already exists
    existing_subcity = await SubCity.filter(name=name).first()
    if existing_subcity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SubCity with this name already exists."
        )

    # Check if the city exists
    city = await City.filter(id=city_id).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found."
        )

    # Create a new subcity instance
    subcity = SubCity(
        name=name,
        city=city,
        pathao_subcity_id=pathao_subcity_id,
        carrybee_subcity_id=carrybee_subcity_id
    )
    await subcity.save()

    return _serialize_subcity(subcity)


@router.get("/subcities/{subcity_id}", tags=["subcities"])
async def get_subcity(subcity_id: str, user: User = Depends(permission_required("   view_subcity"))):
    subcity = await SubCity.filter(id=subcity_id).first().select_related("city")
    if not subcity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SubCity not found."
        )
    return _serialize_subcity(subcity)


@router.patch("/subcities/{subcity_id}", tags=["subcities"])
async def update_subcity(
    subcity_id: str,
    name: str = Form(None),
    city_id: str = Form(None),
    pathao_subcity_id: str = Form(None),
    carrybee_subcity_id: str = Form(None),
    user: User = Depends(permission_required("change_subcity"))
):
    subcity = await SubCity.filter(id=subcity_id).first()
    if not subcity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SubCity not found."
        )

    # Check if a subcity with the same name already exists (excluding the current subcity)
    existing_subcity = await SubCity.filter(name=name).exclude(id=subcity_id).first()
    if existing_subcity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SubCity with this name already exists."
        )

    # Check if the city exists
    city = await City.filter(id=city_id).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found."
        )

    # Update the subcity's attributes
    if name is not None:
        subcity.name = name
    if city_id is not None:
        subcity.city = city
    if pathao_subcity_id is not None:
        subcity.pathao_subcity_id = pathao_subcity_id
    if carrybee_subcity_id is not None:
        subcity.carrybee_subcity_id = carrybee_subcity_id

    await subcity.save()

    return _serialize_subcity(subcity)



@router.delete("/subcities/{subcity_id}", tags=["subcities"])
async def delete_subcity(subcity_id: str, user: User = Depends(permission_required("delete_subcity"))):
    subcity = await SubCity.filter(id=subcity_id).first()
    if not subcity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SubCity not found."
        )

    await subcity.delete()

    return {"detail": "SubCity deleted successfully."}



#------------------------------- ORDER SOURCE ENDPOINTS ---------------------------------#

@router.get("/order-sources", tags=["order_sources"])
async def get_order_sources(user: User = Depends(permission_required("view_order_source"))):
    order_sources = await OrderSource.all()
    return [_serialize_order_source(order_source) for order_source in order_sources]

@router.post("/order-sources", tags=["order_sources"])
async def create_order_source(
    name: str = Form(...),
    status: bool = Form(default=True),
    is_default: bool = Form(default=False),
    user: User = Depends(permission_required("add_order_source"))
):
    # Check if an order source with the same name already exists
    existing_order_source = await OrderSource.filter(name=name).first()
    if existing_order_source:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order Source with this name already exists."
        )

    # Create a new order source instance
    order_source = OrderSource(
        name=name,
        status=status,
        is_default=is_default
    )
    await order_source.save()

    return _serialize_order_source(order_source)


@router.get("/order-sources/{order_source_id}", tags=["order_sources"])
async def get_order_source(order_source_id: str, user: User = Depends(permission_required("view_order_source"))):
    order_source = await OrderSource.filter(id=order_source_id).first()
    if not order_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order Source not found."
        )
    return _serialize_order_source(order_source)


@router.patch("/order-sources/{order_source_id}", tags=["order_sources"])
async def update_order_source(
    order_source_id: str,
    name: str = Form(None),
    status: bool = Form(default=True),
    is_default: bool = Form(default=False),
    user: User = Depends(permission_required("change_order_source"))
):
    order_source = await OrderSource.filter(id=order_source_id).first()
    if not order_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order Source not found."
        )

    # Check if an order source with the same name already exists (excluding the current order source)
    existing_order_source = await OrderSource.filter(name=name).exclude(id=order_source_id).first()
    if existing_order_source:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order Source with this name already exists."
        )

    # Update the order source's attributes
    if name is not None:
        order_source.name = name
    if status is not None:
        order_source.status = status
    if is_default is not None:
        order_source.is_default = is_default

    await order_source.save()

    return _serialize_order_source(order_source)


@router.delete("/order-sources/{order_source_id}", tags=["order_sources"])
async def delete_order_source(order_source_id: str, user: User = Depends(permission_required("delete_order_source"))):
    order_source = await OrderSource.filter(id=order_source_id).first()
    if not order_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order Source not found."
        )

    await order_source.delete()

    return {"detail": "Order Source deleted successfully."}



#------------------------------- COMMENT ENDPOINTS ---------------------------------#

@router.get("/comments", tags=["comments"])
async def get_comments(user: User = Depends(permission_required("view_comment"))):
    comments = await Comment.all()
    return [_serialize_comment(comment) for comment in comments]

@router.post("/comments", tags=["comments"])
async def create_comment(
    comment: str = Form(...),
    status: bool = Form(default=True),
    user: User = Depends(permission_required("add_comment"))
):
    # Create a new comment instance
    new_comment = Comment(
        comment=comment,
        status=status
    )
    await new_comment.save()

    return _serialize_comment(new_comment)


@router.get("/comments/{comment_id}", tags=["comments"])
async def get_comment(comment_id: str, user: User = Depends(permission_required("view_comment"))):
    comment = await Comment.filter(id=comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found."
        )
    return _serialize_comment(comment)


@router.patch("/comments/{comment_id}", tags=["comments"])
async def update_comment(
    comment_id: str,
    comment: str = Form(None),
    status: bool = Form(None),
    user: User = Depends(permission_required("change_comment"))
):
    existing_comment = await Comment.filter(id=comment_id).first()
    if not existing_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found."
        )

    # Update the comment's attributes
    if comment is not None:
        existing_comment.comment = comment
    if status is not None:
        existing_comment.status = status

    await existing_comment.save()

    return _serialize_comment(existing_comment)


@router.delete("/comments/{comment_id}", tags=["comments"])
async def delete_comment(comment_id: str, user: User = Depends(permission_required("delete_comment"))):
    comment = await Comment.filter(id=comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found."
        )

    await comment.delete()

    return {"detail": "Comment deleted successfully."}