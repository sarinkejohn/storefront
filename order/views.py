import os
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from product.models import Product
from .serializer import *
from .filter import OrderFilter
from rest_framework.pagination import PageNumberPagination
import stripe

from utils.helper import get_current_host, get_current_endpoints

# Create your views here.


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    filterset = OrderFilter(
        request.GET, queryset=Order.objects.all().order_by('id'))
    count = filterset.qs.count()

    # Paginator
    resPerPage = 5
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
# update order status ---the same as udating all order info which can be done on a new route


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def processing_order(request, pk):
    order = get_object_or_404(Order, id=pk)
    order.order_status = request.data['order_status']
    order.save()
    serializers = OrderSerializer(order, many=False)
    return Response({'orders': serializers.data})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_order(request, pk):
    order = get_object_or_404(Order, id=pk)
    order.delete()
    return Response({'details': 'Order deleted sucessful!!!'})


# stripe payment--sarinke--john--sarijore--+255748048065 whatsapp
stripe.api_key = os.environ.get('STRIPE_PRIVATE_KEY')
# YOUR_DOMAIN = get_current_host()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    YOUR_DOMAIN = get_current_endpoints(request)

    user = request.user
    data = request.data

    order_items = data['orderItems']

    shipping_details = {
        'street': data['street'],
        'city': data['city'],
        'state': data['state'],
        'country': data['country'],
        'zip_code': data['zip_code'],
        'phone_no': data['phone_no'],
        'user': user.id
    }
    # adding the above detail to stripe checkout
    checkout_order_items = []
    for item in order_items:
        checkout_order_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item['name'],
                    'images': [item['images']],
                    'metadata': {'product_id': item['product']}

                },
                'unit_amount': item['price'] * 100
            },
            'quantity': item['quantity']

        })
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            metadata=shipping_details,
            line_items=checkout_order_items,
            customer_email=user.email,
            mode='payment',
            success_url=YOUR_DOMAIN,
            cancel_url=YOUR_DOMAIN
        )
        return Response({'session': session})


@api_view(['POST'])
def stripe_webhook(request):
    webhook_seceret = os.environ.get('STRIPE_WEBHOOK')
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_seceret
        )

    except ValueError as e:
        return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError as e:
        return Response({'error': 'Invalid Signature'}, status=status.HTTP_400_BAD_REQUEST)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # print('session', session)

        line_items = stripe.checkout.Session.list_line_items(session['id'])
        price = session['amount_total'] / 100

        order = Order.objects.create(
            user=User(session.metadata.user),
            street=session.metadata.street,
            city=session.metadata.city,
            state=session.metadata.state,
            country=session.metadata.country,
            zip_code=session.metadata.zip_code,
            phone_no=session.metadata.phone_no,
            total_amount=price,
            payment_method='Card',
            payment_status='PAID'

        )
        for item in line_items['data']:
            print('item', item)
            line_product = stripe.Product.retrieve(item.price.product)
            product_id = line_product.metadata.product_id

            product = Product.objects.get(id=product_id)
            item = OrderItem.objects.create(
                product=product,
                order=order,
                name=product.name,
                quantity=item.quantity,
                price=item.price.unit_amount / 100,
                images=line_product.images[0]
            )
            product.stock -= item.quantity
            product.save()

        return Response({'details': 'payment successful '})
