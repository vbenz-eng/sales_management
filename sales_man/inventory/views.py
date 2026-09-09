
from django.shortcuts import render
from . models import Inventory
from . serializers import InventorySerializer
from rest_framework import viewsets

# Create your views here.
def index(request):
    inventory = Inventory.objects.all()
    serializer = InventorySerializer(inventory, many=True)
    return render(request, 'inventory/index.html', {'inventory': serializer.data})

class InventoryListView(viewsets.ModelViewSet):
    queryset = Inventory.objects.all().order_by('created_at')
    serializer_class = InventorySerializer
    