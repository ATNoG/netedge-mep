import validators
from validators import ValidationFailure


def validate_uri(href: str) -> str:
    href = validators.url(href)
    if isinstance(href, ValidationFailure):
        raise TypeError
    return href
