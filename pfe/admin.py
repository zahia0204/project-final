from django.contrib import admin
from .models import User, Client, Facture, DateChange

admin.site.register(User)
admin.site.register(Client)
admin.site.register(Facture)
admin.site.register(DateChange)

