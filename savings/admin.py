from django.contrib import admin
from .models import Customer, Worker, Collection, Deduction

admin.site.register(Customer)
admin.site.register(Worker)
admin.site.register(Collection)
admin.site.register(Deduction)
