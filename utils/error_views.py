

from django.http import JsonResponse


def handle404(request, exception):
    massege = ('Route not Found..!')
    response = JsonResponse(data={'error': massege})
    response.status_code = 404
    return response


def handle500(request):
    massege = ('Internal Server Error..!')
    response = JsonResponse(data={'error': massege})
    response.status_code = 500
    return response
