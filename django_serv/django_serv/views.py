from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view

payment = settings.PAYMENT


@api_view(['GET', 'POST'])
@payment.required(3675)
def index(request):
    if request.method == 'GET':
        return JsonResponse({'status': 'paid'})

    raw_values = request.data.get('values')
    values = []
    for value in raw_values:
        values.append('got {}'.format(value))
    return JsonResponse({'values': values}, status=200)
