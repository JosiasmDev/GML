# gestion/templatetags/chat_tags.py
from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    return dictionary.get(key)

@register.filter
def exclude(queryset, exclude_list):
    return queryset.exclude(id__in=[item.id for item in exclude_list])