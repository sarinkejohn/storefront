from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from product.models import Product
from .serializer import *
from .filter import OrderFilter
from rest_framework.pagination import PageNumberPagination


# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    filterset = OrderFilter(
        request.GET, queryset=Order.objects.all().order_by('id'))
    count = filterset.qs.count()

    # Paginator
    resPerPage = 1
    paginator = PageNumberPagination()
    paginator.page_size = resPerPage
    queryset = paginator.paginate_queryset(filterset.qs, request)

    serializers = OrderSerializer(queryset, many=True)
    return Response(
        {
            'count': count,
            'resPerPage': resPerPage,
            'orders': serializers.data
        }
    )


# single order
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order(request, pk):
    order = get_object_or_404(Order, id=pk)
    serializers = OrderSerializer(order, many=False)
    return Response({'orders': serializers.data})


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
