from urllib.parse import urlencode


def generate_pagination_headers(base_url, page, size, total_count):
    """
    Generates pagination headers similar to Spring Boot's HttpHeaders.
    """
    headers = {
        "x-total-count": str(total_count),
    }

    total_pages = (total_count + size - 1) // size  # Equivalent to math.ceil(total_count / size)
    link = []

    def generate_uri(page_number):
        return f"<{base_url}?{urlencode({'page': page_number, 'size': size})}>"

    # Next link
    if (page + 1) < total_pages:
        link.append(f'{generate_uri(page + 1)}; rel="next"')

    # Previous link
    if page > 0:
        link.append(f'{generate_uri(page - 1)}; rel="prev"')

    # Last and First links
    if total_pages > 0:
        link.append(f'{generate_uri(total_pages - 1)}; rel="last"')
    link.append(f'{generate_uri(0)}; rel="first"')

    headers["Link"] = ", ".join(link)

    return headers
