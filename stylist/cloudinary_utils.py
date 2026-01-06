import cloudinary.uploader


def upload_image_to_cloudinary(file_obj, folder="wardrobe"):
    result = cloudinary.uploader.upload(
        file_obj,
        folder=folder,
        resource_type="image",
        overwrite=True,
    )
    return {
        "url": result.get("secure_url"),
        "public_id": result.get("public_id"),
        "width": result.get("width"),
        "height": result.get("height"),
        "format": result.get("format"),
    }
