from django import template
from datetime import date, timedelta
import datetime

register = template.Library()

@register.filter(name='addOneDay')
def addOneDay(value):
    return value+datetime.timedelta(days=1)