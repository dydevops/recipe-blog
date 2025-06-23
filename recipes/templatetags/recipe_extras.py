from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Custom template filter to access dictionary items by key.
    
    Args:
        dictionary (dict): The dictionary to access
        key (str): The key to retrieve
    
    Returns:
        The value associated with the key, or None if not found
    """
    return dictionary.get(key, 0)

@register.filter
def multiply(value, arg):
    """
    Multiplies the value by the given argument.
    
    Args:
        value (float): The value to multiply
        arg (float): The multiplier
    
    Returns:
        float: The result of multiplication
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """
    Divides the value by the given argument.
    
    Args:
        value (float): The value to divide
        arg (float): The divisor
    
    Returns:
        float: The result of division, or 0 if division by zero
    """
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
