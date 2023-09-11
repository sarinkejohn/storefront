from django.shortcuts import get_object_or_404, render
from ..models import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializer import ProductImageSerializer, ProductSerializer
from rest_framework.response import Response
from .filter import ProductsFilters
from rest_framework.pagination import PageNumberPagination
from rest_framework import status


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
@permission_classes([IsAuthenticated])
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
