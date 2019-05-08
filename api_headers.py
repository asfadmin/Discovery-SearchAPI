from werkzeug.datastructures import Headers


def base(mimetype, headers=Headers()):
    base_headers = {
        'Content-type': mimetype
    }

    headers = Headers()

    for name, value in base_headers.items():
        headers.add(name, value)

    return headers
