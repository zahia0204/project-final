# clients/resources.py
from import_export import resources, fields , widgets
from .models import Client
from django.contrib.auth.models import User


# ✅ Widget personnalisé pour les champs avec choix
class SimpleChoiceWidget(widgets.Widget):
    def __init__(self, choices):
        self.choices = dict(choices)
        self.mapping = {
            'Corporate Group': 'Corporate',
            'Group Residential': 'Residential',
            'VIP-AT': 'Corporate',  # Or whatever category fits
        }

    def clean(self, value, row=None, *args, **kwargs):
        if value in self.choices:
            return value
        if value in self.mapping:
            return self.mapping[value]
        raise ValueError(f"Valeur invalide '{value}'. Choix valides: {list(self.choices.keys())}")

    def render(self, value, obj=None):
        return self.choices.get(value, "")


class ClientResource(resources.ModelResource):
    client_id = fields.Field(attribute='client_id', column_name='CUST_CODE')
    name = fields.Field(attribute='name', column_name='FIRST_NAME')
    surname = fields.Field(attribute='surname', column_name='LAST_NAME')
    phone_number = fields.Field(attribute='phone_number', column_name='PRI_IDENTITY')
    
    client_type = fields.Field(
        attribute='client_type',
        column_name='CUST_LEV1_LIB_CA',
        widget=SimpleChoiceWidget(Client.CLIENT_TYPE_CHOICES)
    )
    
    region = fields.Field(
        attribute='region',
        column_name='ACTEL_CODE',
        widget=SimpleChoiceWidget(Client.REGION_CHOICES)
    )

    address = fields.Field(attribute='address', column_name='ADRESSE')

    class Meta:
        model = Client
        import_id_fields = ('client_id',)
        fields = (
            'client_id',
            'name',
            'surname',
            'phone_number',
            'client_type',
            'region',
            'address',
            'total_amount',
        )
