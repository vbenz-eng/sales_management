from django import forms
from .models import Inventory


class SellItemForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=Inventory.objects.filter(quantity__gt=0).order_by('name'),
        label='Item',
        empty_label='Select an item…',
    )
    quantity = forms.IntegerField(
        label='Quantity',
        min_value=1,
    )

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        quantity = cleaned_data.get('quantity')

        if item is not None and quantity is not None and quantity > item.quantity:
            raise forms.ValidationError(
                f'Only {item.quantity} in stock for "{item.name}" — cannot sell {quantity}.'
            )

        return cleaned_data

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['name', 'description', 'quantity', 'price']


class DeleteStockForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=Inventory.objects.all().order_by('name'),
        label='Item',
        empty_label='Select an item…',
    )
    quantity = forms.IntegerField(
        label='Quantity to remove',
        min_value=1,
    )

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        quantity = cleaned_data.get('quantity')

        if item is not None and quantity is not None and quantity > item.quantity:
            raise forms.ValidationError(
                f'Only {item.quantity} in stock for "{item.name}" — cannot remove {quantity}.'
            )

        return cleaned_data
