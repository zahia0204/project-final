from rest_framework import viewsets , status
from .models import User, Client, Facture, DateChange
from .serializers import (
    UserSerializer, ClientSerializer,
    FactureSerializer, DateChangeSerializer,
    MyTokenObtainPairSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from datetime import datetime
from django.shortcuts import get_object_or_404



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


