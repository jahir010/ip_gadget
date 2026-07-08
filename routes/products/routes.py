from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from typing import List, Optional
from applications.user.models import User
from applications.products.models import Product, ProductCategory, Brand, Attribute, Variant
from app.auth import get_current_user, permission_required, role_required
from app.utils.file_manager import save_file, delete_file, update_file
from tortoise.expressions import Q



router = APIRouter(prefix="/v1")



async def _product_serializer(product: Product) -> dict:
    await product.fetch_related("category", "category__parent", "brand")

    return {
        "id": str(product.id),
        "name": product.name,
        "image": product.image,
        "details": product.details,
        "category": {
            "id": str(product.category.id),
            "name": product.category.name,
            "parent": {
                "id": str(product.category.parent.id),
                "name": product.category.parent.name,
            } if product.category.parent else None,
        },
        "brand": {
            "id": str(product.brand.id),
            "name": product.brand.name,
        } if product.brand else None,
        "price": float(product.price),
        "discount": float(product.discount),
        "stock": product.stock,
        "sell_price": product.sell_price(),
        "attributes": product.attributes,
        "variants": product.variants,
        "status": product.status,
        "video_url": product.video_url,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
    }


def _category_serializer(category: ProductCategory) -> dict:
    return {
        "id": str(category.id),
        "name": category.name,
        "parent_id": str(category.parent.id) if category.parent else None,
        "status": category.status,
        "created_at": category.created_at.isoformat() if category.created_at else None,
        "updated_at": category.updated_at.isoformat() if category.updated_at else None,
    }

def _brand_serializer(brand: Brand) -> dict:
    return {
        "id": str(brand.id),
        "name": brand.name,
        "status": brand.status,
        "created_at": brand.created_at.isoformat() if brand.created_at else None,
        "updated_at": brand.updated_at.isoformat() if brand.updated_at else None,
    }

def _attribute_serializer(attribute: Attribute) -> dict:
    return {
        "id": str(attribute.id),
        "name": attribute.name,
        "status": attribute.status,
        "created_at": attribute.created_at.isoformat() if attribute.created_at else None,
        "updated_at": attribute.updated_at.isoformat() if attribute.updated_at else None,
    }

async def _variant_serializer(variant: Variant) -> dict:
    await variant.fetch_related("attribute")
    return {
        "id": str(variant.id),
        "name": variant.name,
        "attribute": {
            "id": str(variant.attribute.id),
            "name": variant.attribute.name,
        } if variant.attribute else None,
        "status": variant.status,
        "created_at": variant.created_at.isoformat() if variant.created_at else None,
        "updated_at": variant.updated_at.isoformat() if variant.updated_at else None,
    }



#############################################################################
#    Endpoints for Products, Categories, Brands, Attributes, and Variants
#############################################################################


@router.get("/categories", tags=["Categories"])
async def get_categories(user: User = Depends(permission_required("view_productcategory"))):
    categories = await ProductCategory.all()
    return [_category_serializer(category) for category in categories]

@router.post("/categories", tags=["Categories"])
async def create_category(
    name: str = Form(...),
    parent_id: str = Form(None),
    user: User = Depends(permission_required("add_productcategory")),
):
    parent = None
    if parent_id:
        parent = await ProductCategory.get_or_none(id=parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent category not found")

    category = await ProductCategory.create(name=name, parent=parent)
    return _category_serializer(category)

@router.get("/categories/{category_id}", tags=["Categories"])
async def get_category(category_id: str, user: User = Depends(permission_required("view_productcategory"))):
    category = await ProductCategory.get_or_none(id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return _category_serializer(category)

@router.patch("/categories/{category_id}", tags=["Categories"])
async def update_category(
    category_id: str,
    name: str = Form(None),
    parent_id: str = Form(None),
    status: bool = Form(None),
    user: User = Depends(permission_required("update_productcategory")),
):
    category = await ProductCategory.get_or_none(id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if name is not None:
        category.name = name

    if parent_id is not None:
        if parent_id == "":
            category.parent = None
        else:
            parent = await ProductCategory.get_or_none(id=parent_id)
            if not parent:
                raise HTTPException(status_code=404, detail="Parent category not found")
            category.parent = parent

    if status is not None:
        category.status = status

    await category.save()
    return _category_serializer(category)


@router.delete("/categories/{category_id}", tags=["Categories"])
async def delete_category(category_id: str, user: User = Depends(permission_required("delete_productcategory"))):
    category = await ProductCategory.get_or_none(id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await category.delete()
    return {"message": "Category deleted successfully"}



# ------------------------
# Brands Endpoints
# ------------------------

@router.get("/brands", tags=["Brands"])
async def get_brands(user: User = Depends(permission_required("view_brand"))):
    brands = await Brand.all()
    return [_brand_serializer(brand) for brand in brands]

@router.post("/brands", tags=["Brands"])
async def create_brand(
    name: str = Form(...),
    user: User = Depends(permission_required("add_brand")),
):
    brand = await Brand.create(name=name)
    return _brand_serializer(brand)

@router.get("/brands/{brand_id}", tags=["Brands"])
async def get_brand(brand_id: str, user: User = Depends(permission_required("view_brand"))):
    brand = await Brand.get_or_none(id=brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return _brand_serializer(brand)

@router.patch("/brands/{brand_id}", tags=["Brands"])
async def update_brand(
    brand_id: str,
    name: str = Form(None),
    status: bool = Form(None),
    user: User = Depends(permission_required("update_brand")),
):
    brand = await Brand.get_or_none(id=brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    if name is not None:
        brand.name = name

    if status is not None:
        brand.status = status

    await brand.save()
    return _brand_serializer(brand)


@router.delete("/brands/{brand_id}", tags=["Brands"])
async def delete_brand(brand_id: str, user: User = Depends(permission_required("delete_brand"))):
    brand = await Brand.get_or_none(id=brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    await brand.delete()
    return {"message": "Brand deleted successfully"}


#------------------------
# Attributes Endpoints
#------------------------

@router.get("/attributes", tags=["Attributes"])
async def get_attributes(user: User = Depends(permission_required("view_attribute"))):
    attributes = await Attribute.all()
    return [_attribute_serializer(attribute) for attribute in attributes]

@router.post("/attributes", tags=["Attributes"])
async def create_attribute(
    name: str = Form(...),
    user: User = Depends(permission_required("add_attribute")),
):
    attribute = await Attribute.create(name=name)
    return _attribute_serializer(attribute)

@router.get("/attributes/{attribute_id}", tags=["Attributes"])
async def get_attribute(attribute_id: str, user: User = Depends(permission_required("view_attribute"))):
    attribute = await Attribute.get_or_none(id=attribute_id)
    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return _attribute_serializer(attribute)

@router.patch("/attributes/{attribute_id}", tags=["Attributes"])
async def update_attribute(
    attribute_id: str,
    name: str = Form(None),
    status: bool = Form(None),
    user: User = Depends(permission_required("update_attribute")),
):
    attribute = await Attribute.get_or_none(id=attribute_id)
    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")

    if name is not None:
        attribute.name = name

    if status is not None:
        attribute.status = status

    await attribute.save()
    return _attribute_serializer(attribute)


@router.delete("/attributes/{attribute_id}", tags=["Attributes"])
async def delete_attribute(attribute_id: str, user: User = Depends(permission_required("delete_attribute"))):
    attribute = await Attribute.get_or_none(id=attribute_id)
    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")
    await attribute.delete()
    return {"message": "Attribute deleted successfully"}


#--------------------------
# Variants Endpoints
#--------------------------

@router.get("/variants", tags=["Variants"])
async def get_variants(user: User = Depends(permission_required("view_variant"))):
    variants = await Variant.all()
    return [await _variant_serializer(variant) for variant in variants]

@router.post("/variants", tags=["Variants"])
async def create_variant(
    name: str = Form(...),
    attribute_id: str = Form(...),
    user: User = Depends(permission_required("add_variant")),
):
    attribute = await Attribute.get_or_none(id=attribute_id)
    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")

    variant = await Variant.create(name=name, attribute=attribute)
    return _variant_serializer(variant)


@router.get("/variants/{variant_id}", tags=["Variants"])
async def get_variant(variant_id: str, user: User = Depends(permission_required("view_variant"))):
    variant = await Variant.get_or_none(id=variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return await _variant_serializer(variant)

@router.patch("/variants/{variant_id}", tags=["Variants"])
async def update_variant(
    variant_id: str,
    name: str = Form(None),
    attribute_id: str = Form(None),
    status: bool = Form(None),
    user: User = Depends(permission_required("update_variant")),
):
    variant = await Variant.get_or_none(id=variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    if name is not None:
        variant.name = name

    if attribute_id is not None:
        if attribute_id == "":
            variant.attribute = None
        else:
            attribute = await Attribute.get_or_none(id=attribute_id)
            if not attribute:
                raise HTTPException(status_code=404, detail="Attribute not found")
            variant.attribute = attribute

    if status is not None:
        variant.status = status

    await variant.save()
    return await _variant_serializer(variant)


@router.delete("/variants/{variant_id}", tags=["Variants"])
async def delete_variant(variant_id: str, user: User = Depends(permission_required("delete_variant"))):
    variant = await Variant.get_or_none(id=variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    await variant.delete()
    return {"message": "Variant deleted successfully"}



#-----------------------------------
# Products Endpoints
#-----------------------------------

@router.get("/products", tags=["Product"])
async def get_products(
    search_query: str = None,
    category_id: str = None,
    brand_id: str = None,
    max_price: float = None,
    min_price: float = None,
    status: bool = None,
    offset: int = 0,
    limit: int = 10,
    user: User = Depends(permission_required("view_product"))
):
    query = Product.all()

    if search_query:
        query = query.filter(
        Q(name__icontains=search_query) | Q(details__icontains=search_query)
        )
    if category_id:
        query = query.filter(category_id=category_id)

    if brand_id:
        query = query.filter(brand_id=brand_id)

    if max_price is not None:
        query = query.filter(price__lte=max_price)

    if min_price is not None:
        query = query.filter(price__gte=min_price)

    if status is not None:
        query = query.filter(status=status)

    total = await query.count()

    products = (
        await query
        .select_related("category", "category__parent", "brand")
        .offset(offset)
        .limit(limit)
        .order_by("-created_at")
    )

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": [await _product_serializer(product) for product in products],
    }


@router.post("/products", tags=["Product"])
async def create_product(
    name: str = Form(...),
    image_files: Optional[List[UploadFile]] = File(None),
    details: str = Form(None),
    category_id: str = Form(...),
    brand_id: str = Form(None),
    price: float = Form(...),
    discount: float = Form(0.0),
    stock: int = Form(0),
    status: bool = Form(True),
    video: Optional[UploadFile] = File(None),
    attributes: str = Form(None),  # JSON string
    variants: str = Form(None),  # JSON string
    user: User = Depends(permission_required("add_product")),
):
    category = await ProductCategory.get_or_none(id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    brand = None
    if brand_id:
        brand = await Brand.get_or_none(id=brand_id)
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")

    image_urls = []
    if image_files:
        for image_file in image_files:
            image_url = await save_file(image_file, "product_images")
            image_urls.append(image_url)

    video_url = None
    if video:
        # Handle video upload and get the URL
        video_url = await save_file(video, "product_videos")

    product = await Product.create(
        name=name,
        image=image_urls,
        details=details,
        category=category,
        brand=brand,
        price=price,
        discount=discount,
        stock=stock,
        status=status,
        video_url=video_url,
        attributes=attributes,
        variants=variants,
    )

    return await _product_serializer(product)


@router.get("/products/{product_id}", tags=["Product"])
async def get_product(product_id: str, user: User = Depends(permission_required("view_product"))):
    product = await Product.get_or_none(id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return await _product_serializer(product)

@router.patch("/products/{product_id}", tags=["Product"])
async def update_product(
    product_id: str,
    name: str = Form(None),
    image_files: Optional[List[UploadFile]] = File(None),
    details: str = Form(None),
    category_id: str = Form(None),
    brand_id: str = Form(None),
    price: float = Form(None),
    discount: float = Form(None),
    stock: int = Form(None),
    status: bool = Form(None),
    video: Optional[UploadFile] = File(None),
    attributes: str = Form(None),  # JSON string
    variants: str = Form(None),  # JSON string
    delete_image_urls: Optional[List[str]] = Form(None),  # URLs of images to delete
    user: User = Depends(permission_required("update_product")),
):
    product = await Product.get_or_none(id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if name is not None:
        product.name = name

    if details is not None:
        product.details = details

    if category_id is not None:
        category = await ProductCategory.get_or_none(id=category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        product.category = category

    if brand_id is not None:
        if brand_id == "":
            product.brand = None
        else:
            brand = await Brand.get_or_none(id=brand_id)
            if not brand:
                raise HTTPException(status_code=404, detail="Brand not found")
            product.brand = brand

    if price is not None:
        product.price = price

    if discount is not None:
        product.discount = discount

    if stock is not None:
        product.stock = stock

    if status is not None:
        product.status = status

    if attributes is not None:
        product.attributes = attributes

    if variants is not None:
        product.variants = variants

    if delete_image_urls:
        for url in delete_image_urls:
            if url in product.image:
                await delete_file(url)
                product.image.remove(url)

    if image_files:
        for image_file in image_files:
            image_url = await save_file(image_file, "product_images")
            product.image.append(image_url)

    if video:
        if product.video_url:
            product.video_url =await update_file(video, product.video_url, "product_videos")
        else:
            product.video_url = await save_file(video, "product_videos")

    await product.save()
    return await _product_serializer(product)


@router.delete("/products/{product_id}", tags=["Product"])
async def delete_product(product_id: str, user: User = Depends(permission_required("delete_product"))):
    product = await Product.get_or_none(id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Delete associated images
    if product.image:
        for image_url in product.image:
            await delete_file(image_url)

    # Delete associated video
    if product.video_url:
        await delete_file(product.video_url)

    await product.delete()
    return {"message": "Product deleted successfully"}




