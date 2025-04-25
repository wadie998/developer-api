def extract_base64_image_data(value):
    header_img, bare_img64 = value.split(",")
    if header_img == "data:image/png;base64":
        return bare_img64, "png", "image/png"
    else:
        return bare_img64, "jpg", "image/jpeg"
