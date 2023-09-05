

from django.http import JsonResponse


def handle404(request, exception):
    massege = ('Route not Found..!')
    response = JsonResponse(data={'error': massege})
    response.status_code = 404
    return response
