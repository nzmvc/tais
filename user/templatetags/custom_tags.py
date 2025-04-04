from django import template
from django.core.cache import cache
from django.db.models import Q,Sum,Count
from decouple import config

import datetime
register = template.Library()

@register.filter
def tag_test():
    return True

@register.filter
def get_value(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_task_color(task):
   
    #TODO: setting den buffer time ayarlanabilsin datetime.timedelta(days=1)
    #TODO: settingsden renkler ayarlanabilsin
    
    bufferTime = datetime.timedelta(days=0)

    if task.closed_date and task.deadline:
        if task.deadline + bufferTime >= task.closed_date :
            return "bg-success"
        else:
            return "bg-danger"
    else:
        if task.deadline:
            if task.deadline + bufferTime < datetime.datetime.now() :
                return "bg-warning"
            else:
                return  "bg-primary"
            
        else:
            return "bg-primary"

@register.filter
def get_day_task_color(number):
    """
    0: görev tanımlanmamış 
    1:zamanında tamamlanmış 
    2:geçikmiş 
    3:tamamlanmamış 
    4: bekliyor
    5:birden fazla görev tanımlanmış
    """
    if number == 0:
        color= ""
    elif number == 1:
        color="bg-success"
    elif number == 2:
        color= "bg-warning"
    elif number == 3:
        color= "bg-danger"
    elif number == 4:
        color= "bg-light"
    elif number == 5:
        color= "bg-info"
    else:
        color= ""
    
    try:
        number = int(number)
        veri = ""
    except :
        veri = number
        
    return f"<td class=\"{color}\"> {veri}</td>"
  
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def multiply(value, arg):
    return float(value) * float(arg)


@register.simple_tag
def get_html_data():
    return config('HEADER', default='')
