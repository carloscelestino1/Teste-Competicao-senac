# main/templatetags/custom_tags.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def pluck(objects, attr_name):
    return [getattr(obj, attr_name) for obj in objects if hasattr(obj, attr_name)]
