from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from product.models import Product
from .serializer import *


# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_order(request):
    user = request.user
    data = request.data

    order_items = data['orderItems']

    if order_items and len(order_items) == 0:
        return Response({'error': 'No order item :Please add one product'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        # create order
        total_amount = sum(item['price'] * item['quantity']
                           for item in order_items)
        order = Order.objects.create(
            user=user,
            city=data['city'],
            street=data['street'],
            state=data['state'],
            zip_code=data['zip_code'],
            country=data['country'],
            phone_no=data['phone_no'],
            total_amount=total_amount
        )
        # creating order items and set order to order items
        for i in order_items:
            product = Product.objects.get(id=i['product'])
            item = OrderItem.objects.create(
                product=product,
                order=order,
                name=product.name,
                quantity=i['quantity'],
                price=i['price']
            )
            # update product stock
            product.stock -= item.quantity
            product.save()

    serializer = OrderSerializer(order, many=False)
    return Response(serializer.data)
