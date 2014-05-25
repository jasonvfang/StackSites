import re
from string import ascii_lowercase, digits


def has_upper(s, field_name):
    msg = 'The {0} you entered cannot have uppercase letters.'.format(field_name)
    if any([char.isupper() for char in s]):
        return True, msg
    return False, None


def has_nonalpha(s, field_name):
    msg = 'The {0} you entered can only have alphanumeric characters.'.format(field_name)
    if not all([(char in ascii_lowercase or char in digits) for char in s.lower()]):
        return True, msg
    return False, None


def has_upper_nonalpha(s, field_name):
    upper_results = has_upper(s, field_name)
    alpha_results = has_nonalpha(s, field_name)
    return [msg for msg in (upper_results[1], alpha_results[1]) if msg is not None]
