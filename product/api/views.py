from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from ..models import *
from .serializer import ProductImageSerializer, ProductSerializer
from .filter import ProductsFilters
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.db.models import Avg


@api_view(['GET'])
def getRoutes(request):
    routes = [

        'GET /api/products',
        'GET /api/products/:id',
        'GET /api/product/:id/update/',
        'GET /api/product/:id/delete/',
        'POST /api/upload_images/',
        'POST /api/product/new/',
        'POST /api/register/',
        'POST /api/token/',
        'POST /api/me/',


    ]
    return Response(routes)


@api_view(['GET'])
def get_products(request):
    filterset = ProductsFilters(
        request.GET, queryset=Product.objects.all().order_by('id'))
    # counting the filterd data
    count = filterset.qs.count()
    # Pagination
    resPerPage = 10
    paginator = PageNumberPagination()
    paginator.page_size = resPerPage
    queryset = paginator.paginate_queryset(filterset.qs, request)
    # products = Product.objects.all()
    serializer = ProductSerializer(queryset, many=True)
    return Response({
        "count": count,
        "resPerPage": resPerPage,
        "products": serializer.data})


@api_view(['GET'])
def get_product(request, pk):
    # product = Product.objects.get(id=pk)
    product = get_object_or_404(Product, id=pk)
    serializer = ProductSerializer(product, many=False)

    return Response(serializer.data)
# Adds new product


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def new_product(request):
    data = request.data
    serializer = ProductSerializer(data=data)

    if serializer.is_valid():

        product = Product.objects.create(**data, user=request.user)

        res = ProductSerializer(product, many=False)

        return Response({'product': res.data})
    else:
        return Response(serializer.errors)

# handles product images uploading


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def upload_product_images(request):
    data = request.data
    files = request.FILES.getlist('images')

    images = []
    for f in files:
        image = ProductImages.objects.create(
            product=Product(data['product']), images=f)
        images.append(image)
    serializers = ProductImageSerializer(images, many=True)

    return Response(serializers.data)

# Product update


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_product(request, pk):
    product = get_object_or_404(Product, id=pk)

    # Check if the user is the same ----Todo
    if product.user != request.user:
        return Response({'Not authorized to update this product'}, status=status.HTTP_401_UNAUTHORIZED)

    product.name = request.data['name']
    product.description = request.data['description']
    product.price = request.data['price']
    product.brand = request.data['brand']
    product.category = request.data['category']
    product.ratings = request.data['ratings']
    product.stock = request.data['stock']

    product.save()
    serializer = ProductSerializer(product, many=False)

    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_product(request, pk):
    product = get_object_or_404(Product, id=pk)

    # Check if the user is the same ----Todo
    if product.user != request.user:
        return Response({'Not authorized to Delete this product'}, status=status.HTTP_401_UNAUTHORIZED)
    args = {'product': pk}
    images = ProductImages.objects.filter(**args)
    for i in images:
        i.delete()

    product.delete()

    return Response({'Details': 'product is deleted'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, pk):
    user = request.user
    data = request.data
    product = get_object_or_404(Product, id=pk)

    review = product.reviews.filter(user=user)

    if int(data['ratings']) <= 0 or int(data['ratings']) > 5:
        return Response({'error': 'Please select rating between 1-5'}, status=status.HTTP_400_BAD_REQUEST)
    elif review.exists():
        new_review = {'ratings': data['ratings'], 'comment': data['comment']}
        review.update(**new_review)

        rating = product.reviews.aggregate(avg_rating=Avg('ratings'))
        product.ratings = rating['avg_rating']
        product.save()
        return Response({'detail': 'Review updated'})
    else:
        Review.objects.create(
            user=user,
            product=product,
            ratings=data['ratings'],
            comment=data['comment']
        )
        rating = product.reviews.aggregate(avg_rating=Avg('ratings'))
        product.ratings = rating['avg_rating']
        product.save()
        return Response({'detail': 'Review Posted successful'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, pk):
    user = request.user
    data = request.data
    product = get_object_or_404(Product, id=pk)

    review = product.reviews.filter(user=user)
    if review.exists():
        review.delete()

        rating = product.reviews.aggregate(avg_rating=Avg('ratings'))
        # check if theire is reviews first
        if rating['avg_rating'] is None:
            rating['avg_rating'] = 0

        product.ratings = rating['avg_rating']
        product.save()
        return Response({'detail': 'Review Deleted successful'})

    else:
        return Response({'error': 'Review not Found'}, status=status.HTTP_404_NOT_FOUND)
