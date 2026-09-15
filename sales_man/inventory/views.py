from django.shortcuts import render, redirect
from .models import Inventory
from .serializers import InventorySerializer
from .forms import InventoryForm
from rest_framework import viewsets

def index(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = InventoryForm()

    inventory = Inventory.objects.all().order_by('-created_at')
    serializer = InventorySerializer(inventory, many=True)

    return render(request, 'inventory/index.html', {
        'inventory': serializer.data,
        'form': form,
    })

class InventoryListView(viewsets.ModelViewSet):
    queryset = Inventory.objects.all().order_by('created_at')
    serializer_class = InventorySerializer