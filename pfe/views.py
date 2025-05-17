from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from .resources import ClientResource
from tablib import Dataset
from import_export.formats.base_formats import XLSX
from weasyprint import HTML
from datetime import datetime
from django.db.models.functions import TruncMonth
from django.db.models import Count
from collections import defaultdict
import calendar

from .models import User, Client, Facture, DateChange
from .serializers import (
    UserSerializer, ClientSerializer,
    FactureSerializer, DateChangeSerializer,
    MyTokenObtainPairSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView

def generate_pdf(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    logo_url = request.build_absolute_uri('/static/images/pix.png')

    html_content = render_to_string("pdf_template.html", {
        "name": client.name,
        "surname": client.surname,
        "address": client.address,
        "client_id": client.client_id,
        "total": client.total_amount,
        "phone": client.phone_number,
        "today_date": datetime.today().strftime('%Y-%m-%d'),
        "ref_number": "05",
        "year": "2024",
        'logo_url': logo_url
    })

    pdf_file = HTML(string=html_content).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="client_warning.pdf"'
    return response


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'], url_path='by-username/(?P<username>[^/.]+)')
    def get_by_username(self, request, username=None):
        try:
            user = User.objects.get(username=username)
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class FactureViewSet(viewsets.ModelViewSet):
    queryset = Facture.objects.all()
    serializer_class = FactureSerializer

class DateChangeViewSet(viewsets.ModelViewSet):
    queryset = DateChange.objects.all()
    serializer_class = DateChangeSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['GET'])
def client_history(request, pk):
    try:
        client = Client.objects.get(pk=pk)
    except Client.DoesNotExist:
        return Response({"error": "Client not found"}, status=404)

    changes = client.date_changes.all().order_by('-changed_at')
    history_list = []

    for change in changes:
        history_list.append({
            "date": change.changed_at.strftime("%Y-%m-%d"),
            "previous_etat": change.previous_etat,
            "new_etat": change.new_etat,
        })

    return Response(history_list)




@api_view(['GET'])
def client_stats(request):
    total_clients = Client.objects.count()
    clients_regle = Client.objects.filter(etat="Payment Réglé").count()
    clients_en_cours = Client.objects.filter(etat="Paiement en cours").count()
    clients_juridique = Client.objects.filter(etat="Juridique").count()
    clients_huissier = Client.objects.filter(etat="Huissier").count()
    clients_avocat = Client.objects.filter(etat="Avocat").count()
    clients_non_traite = Client.objects.filter(etat="Non Traité").count()
    clients_decede = Client.objects.filter(etat="Décédé").count()

    clients_by_status = {
        "Payment Réglé": clients_regle,
        "Paiement en cours": clients_en_cours,
        "Non Traité": clients_non_traite,
        "Juridique": clients_juridique,
        "Huissier": clients_huissier,
        "Avocat": clients_avocat,
        "Décédé": clients_decede
    }

    # Monthly stats
    changes = DateChange.objects.all()
    regle_changes = changes.filter(new_etat="Payment Réglé").annotate(month=TruncMonth("changed_at")).values("month").annotate(count=Count("id"))
    en_cours_changes = changes.filter(new_etat__in=["Paiement en cours", "En Cours"]).annotate(month=TruncMonth("changed_at")).values("month").annotate(count=Count("id"))

    month_order = list(calendar.month_abbr)[1:]  # Jan, Feb, ...
    regle_counts = [0] * 12
    en_cours_counts = [0] * 12

    for item in regle_changes:
        month_index = item["month"].month - 1
        if 0 <= month_index < 12:
            regle_counts[month_index] = item["count"]

    for item in en_cours_changes:
        month_index = item["month"].month - 1
        if 0 <= month_index < 12:
            en_cours_counts[month_index] = item["count"]

    return Response({
        "total_clients": total_clients,
        "clients_regle": clients_regle,
        "clients_en_cours": clients_en_cours,
        "clients_by_status": clients_by_status,
        "monthly_data": {
            "months": month_order,
            "regle": regle_counts,
            "en_cours": en_cours_counts
        }
    })


class ClientImportView(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')

        if not file:
            return Response({'error': 'Aucun fichier reçu.'}, status=status.HTTP_400_BAD_REQUEST)

        # Lecture du fichier binaire
        dataset = Dataset()
        xlsx_format = XLSX()
        data = file.read()

        try:
            # Charger le contenu du fichier dans un dataset
            dataset.load(data, format='xlsx')

            # Importer avec la resource
            resource = ClientResource()
            result = resource.import_data(dataset, dry_run=False, raise_errors=True)
            return Response({'success': True, 'imported': len(result.rows)}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ClientExportView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            resource = ClientResource()
            dataset = resource.export()
            xlsx_format = XLSX()
            export_data = xlsx_format.export_data(dataset)

            response = HttpResponse(
                export_data,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
            response['Content-Disposition'] = 'attachment; filename="clients_export.xlsx"'
            return response

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
