from django.urls import include, path
from . views import index, InventoryListView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'inventory', InventoryListView, basename='inventory')  

urlpatterns =[
    path('', index, name='index'),
    path('api/', include(router.urls)),
]
