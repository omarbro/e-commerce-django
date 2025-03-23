from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from store.models import Product, Customer, Collection, Order, OrderItem
from django.db import connection
from tags.models import TaggedItem


def say_hello(request):
    with connection.cursor() as cursor:
        cursor.callproc('get_customers',[1,2,3])
    return render(request, 'hello.html', {'name': 'Mosh'})
    