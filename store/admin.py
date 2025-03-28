from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Count
from django.utils.html import format_html, urlencode 
from django.urls import reverse
from . import models

# Register your models here.
#admin.site.register(models.Product)

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    search_fields=['title']
    list_display = ['title', 'products_count']
    
    
    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url= (reverse('admin:store_product_changelist')
              + '?'
              + urlencode({
                  'collection__id':str(collection.id)
              }
              ))
        return format_html('<a href= "{}">{}</a>', url, collection.products_count)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count = Count('product')
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership']
    list_editable = ['membership']
    list_per_page = 10
    ordering= ['first_name', 'last_name']
    search_fields= ['first_name__istartswith', 'last_name__istartswith']

class InventoryFilter(admin.SimpleListFilter):
    title= 'inventory'
    parameter_name= 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'low')
        ]
    
    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)
        


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields=['collection']
    prepopulated_fields= {
        'slug':['title']
    }
    search_fields= ['title']
    actions= ['clear_inventory']
    list_display = ['title','unit_price','inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_select_related = ['collection']
    list_per_page= 10
    list_filter= ['collection', 'last_update', InventoryFilter ]
    

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering= 'inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'
    

    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        updated_count= queryset.update(inventory= 0)
        self.message_user(
            request,
            f'{updated_count} updated successfully',
            messages.ERROR
            )

class OrderItemInline(admin.TabularInline):
    autocomplete_fields= ['product']
    model = models.OrderItem
    extra= 0

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display=[ 'id','placed_at','customer']
    inlines= [OrderItemInline]
