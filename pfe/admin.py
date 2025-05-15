from django.contrib import admin
from .models import User, Client, Facture, DateChange
from import_export.admin import ImportExportModelAdmin
from .resources import ClientResource

admin.site.register(User)
admin.site.register(Facture)
admin.site.register(DateChange)

@admin.register(Client)
class ClientAdmin(ImportExportModelAdmin):
    resource_class = ClientResource
    list_display = ('client_id', 'name', 'surname', 'phone_number', 'client_type', 'region', 'etat')