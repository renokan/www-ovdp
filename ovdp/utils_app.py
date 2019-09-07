
def convert_to_int(string):
    if string.isdigit():
        return int(string)


def paginate(item_all, item_qty, page=1):
    if not item_all:
        raise ConnectionError

    pages = len(item_all[::item_qty])
    if page < 1 or page > pages:
        raise ValueError

    page_prev = None
    page_next = None
    slice_start = None
    slice_end = None
    if pages != 1:
        if page == 1:
            page_next = page + 1
            slice_end = page * item_qty
        elif page == pages:
            page_prev = page - 1
            slice_start = ((page - 1) * item_qty)
        else:
            page_prev = page - 1
            page_next = page + 1
            slice_start = ((page - 1) * item_qty)
            slice_end = (page * item_qty)
    data = item_all[slice_start:slice_end]

    output = {'page': page, 'pages': pages,
              'previous': page_prev, 'next': page_next,
              'data': data}

    return output
