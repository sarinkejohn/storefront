from django.shortcuts import get_object_or_404, render
from ..models import Product
from rest_framework.decorators import api_view
from .serializer import ProductSerializer
from rest_framework.response import Response
from .filter import ProductsFilters
from rest_framework.pagination import PageNumberPagination


@api_view(['GET'])
def getRoutes(request):
    routes = [

        'GET /api/products',
        'GET /api/products/:id'

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
