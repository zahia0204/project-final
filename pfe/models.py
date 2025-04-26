from django.db import models
from django.contrib.auth.models import AbstractUser 
from simple_history.models import HistoricalRecords

class User(AbstractUser):
    ROLE_CHOICES = [
        (1, "Admin"),
        (2, "Responsable de Boufarik"),
        (3, "Responsable de Mouzaia"),
        (4, "Responsable de Larbaa"),
        (5, "Responsable de Oulad Yaich"),
        (6, "Responsable de El Wouroud"),
        (7, "Responsable de Bougara"),
        (8, "Responsable de Afroun"),
    ]
    phone_number = models.CharField(max_length=15)  
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES , default=2) 

    def __str__(self):
        return f"{self.get_role_display()}: {self.username}"

class Client(models.Model):
    CLIENT_TYPE_CHOICES = [
        ("Corporate", "Corporate"),
        ("Residential", "Residential"),
    ]
    STATUS_CHOICES = [
        ("Non Traité", "Non Traité"),
        ("Décédé", "Décédé"),
        ("Avocat", "Avocat"),
        ("Huissier", "Huissier"),
        ("Juridique", "Juridique"),
        ("En Cours", "En Cours"),
        ("Payment Réglé", "Payment Réglé"),
    ]
    REGION_CHOICES = [
        ("Boufarik", "Boufarik"),
        ("Mouzaia", "Mouzaia"),
        ("Larbaa", "Larbaa"),
        ("OuladYaich", "Oulad Yaich"),
        ("ElWouroud", "El Wouroud"),
        ("Bougara", "Bougara"),
        ("Afroun", "Afroun"),
    ]
    client_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, default="Unknown")
    surname = models.CharField(max_length=255, default="Unknown")
    phone_number = models.CharField(max_length=15)
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPE_CHOICES)
    region = models.CharField(max_length=50, choices=REGION_CHOICES)
    address = models.TextField(max_length=255, default="Unknown")
    observation = models.TextField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="clients")
    etat = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Non Traité")


    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if self.pk:  
            try:
                old_client = Client.objects.get(pk=self.pk)
                if old_client.etat != self.etat:
                    DateChange.objects.create(
                        client=self,
                        previous_etat=old_client.etat,
                        new_etat=self.etat,
                    )
            except Client.DoesNotExist:
                pass  
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name} {self.surname} - {self.etat}"

class Facture(models.Model):
    facture_id = models.CharField(max_length=50, unique=True)
    amount = models.FloatField(default=0)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="factures")

    def __str__(self):
        return f"Facture {self.facture_id} - {self.amount} DZD"

class DateChange(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="date_changes", default=1)
    previous_etat = models.CharField(max_length=20, choices=Client.STATUS_CHOICES, default="Non Traité")
    new_etat = models.CharField(max_length=20, choices=Client.STATUS_CHOICES , default="Non Traité")
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.name} {self.client.surname} | {self.previous_etat} ➝ {self.new_etat} on {self.changed_at}"
