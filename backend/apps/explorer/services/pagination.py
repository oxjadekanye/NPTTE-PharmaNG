"""Shared list pagination for explorer payloads."""


def paginate_list(items: list, *, page: int = 1, page_size: int = 25) -> dict:
    page = max(1, page)
    page_size = min(100, max(1, page_size))
    start = (page - 1) * page_size
    end = start + page_size
    slice_items = items[start:end]
    total = len(items)
    return {
        "items": slice_items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "has_more": end < total,
    }
