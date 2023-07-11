def get_class_identifier(clas: type) -> str:
    return clas.__module__ + clas.__qualname__
