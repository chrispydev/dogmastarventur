from django.contrib import admin
from savings.models import Customer, Worker, Collection


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'next_of_kin', 'balance',
                    'account_number', 'joined', 'customer_image_tag')
    search_fields = ('name', 'next_of_kin', 'account_number')
    list_filter = ('joined', 'balance')
    readonly_fields = ('account_number',)
    ordering = ('-joined',)

    def customer_image_tag(self, obj):
        if obj.customer_image:
            return f'<img src="{obj.customer_image.url}" style="height:50px;width:50px;border-radius:50%;">'
        return 'No Image'
    customer_image_tag.short_description = 'Customer Image'
    customer_image_tag.allow_tags = True


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('user', 'number_of_customers')
    search_fields = ('user__username',)
    ordering = ('user',)

    def number_of_customers(self, obj):
        return obj.customer_set.count()
    number_of_customers.short_description = 'Assigned Customers'


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('worker', 'customer', 'amount', 'date',
                    'customer_balance_after_collection')
    search_fields = ('worker__user__username', 'customer__name')
    list_filter = ('date',)
    ordering = ('-date',)

    def customer_balance_after_collection(self, obj):
        return obj.customer.balance
    customer_balance_after_collection.short_description = 'Customer Balance'


# Register your models
admin.site.site_header = "Admin Dashboard"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to the Management System"
