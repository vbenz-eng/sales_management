from decimal import Decimal

from django.shortcuts import render, redirect
from .models import Inventory, Sale, SaleItem
from .serializers import InventorySerializer
from .forms import InventoryForm, DeleteStockForm, SellItemForm
from rest_framework import viewsets


def _get_cart(request):
    """Cart is stored in the session as {inventory_id (str): quantity (int)}."""
    return request.session.setdefault('cart', {})


def _cart_lines(cart):
    """Resolve the raw session cart into display-ready rows, dropping any
    entries whose inventory item no longer exists."""
    lines = []
    total = Decimal('0')
    valid_cart = {}

    for item_id, quantity in cart.items():
        try:
            item = Inventory.objects.get(pk=item_id)
        except Inventory.DoesNotExist:
            continue
        subtotal = item.price * quantity
        lines.append({'item': item, 'quantity': quantity, 'subtotal': subtotal})
        total += subtotal
        valid_cart[item_id] = quantity

    return lines, total, valid_cart


def index(request):
    add_form = InventoryForm()
    delete_form = DeleteStockForm()
    sell_form = SellItemForm()

    cart = _get_cart(request)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'add':
            add_form = InventoryForm(request.POST)
            if add_form.is_valid():
                add_form.save()
                return redirect('index')

        elif form_type == 'delete':
            delete_form = DeleteStockForm(request.POST)
            if delete_form.is_valid():
                item = delete_form.cleaned_data['item']
                quantity = delete_form.cleaned_data['quantity']

                if quantity >= item.quantity:
                    item.delete()
                else:
                    item.quantity -= quantity
                    item.save()

                return redirect('index')

        elif form_type == 'sell_add':
            sell_form = SellItemForm(request.POST)
            if sell_form.is_valid():
                item = sell_form.cleaned_data['item']
                quantity = sell_form.cleaned_data['quantity']

                already_in_cart = cart.get(str(item.pk), 0)
                if already_in_cart + quantity > item.quantity:
                    sell_form.add_error(
                        'quantity',
                        f'Only {item.quantity - already_in_cart} more "{item.name}" '
                        f'available (some is already in this sale).',
                    )
                else:
                    cart[str(item.pk)] = already_in_cart + quantity
                    request.session.modified = True
                    return redirect('index')

        elif form_type == 'sell_remove':
            item_id = request.POST.get('item_id')
            if item_id in cart:
                del cart[item_id]
                request.session.modified = True
            return redirect('index')

        elif form_type == 'sell_checkout':
            lines, total, valid_cart = _cart_lines(cart)
            if lines:
                sale = Sale.objects.create()
                for line in lines:
                    item = line['item']
                    quantity = line['quantity']

                    if quantity > item.quantity:
                        # Stock changed since it was added to the cart.
                        quantity = item.quantity
                    if quantity <= 0:
                        continue

                    SaleItem.objects.create(
                        sale=sale,
                        inventory_item=item,
                        quantity=quantity,
                        unit_price=item.price,
                    )
                    item.quantity -= quantity
                    item.save()

                request.session['cart'] = {}
                request.session.modified = True
            return redirect('index')

    cart_lines, cart_total, valid_cart = _cart_lines(cart)
    if valid_cart != cart:
        request.session['cart'] = valid_cart
        request.session.modified = True

    inventory = Inventory.objects.all().order_by('-created_at')
    serializer = InventorySerializer(inventory, many=True)

    sales_history = (
        Sale.objects
        .all()
        .order_by('-created_at')
        .prefetch_related('items', 'items__inventory_item')
    )

    return render(request, 'inventory/index.html', {
        'inventory': serializer.data,
        'form': add_form,
        'delete_form': delete_form,
        'sell_form': sell_form,
        'cart_lines': cart_lines,
        'cart_total': cart_total,
        'sales_history': sales_history,
    })


class InventoryListView(viewsets.ModelViewSet):
    queryset = Inventory.objects.all().order_by('created_at')
    serializer_class = InventorySerializer
