from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view

payment = settings.PAYMENT


@api_view(['GET', 'POST'])
@payment.required(5000)
def index(request):
    if request.method == 'GET':
        return JsonResponse({'status': 'paid'})

    bytes = 0
    file = request.data.get('file')
    if file:
        content = file.read()
        with open('uploaded.txt', 'wb') as f:
            bytes = f.write(content)

    raw_values = request.data.get('values', [])
    values = []
    for value in raw_values:
        values.append('got {}'.format(value))

    return JsonResponse({'values': values, 'bytes': bytes}, status=200)


@api_view(['GET'])
def balance(request):
    settings.WALLET.sync_accounts()
    total = settings.WALLET.balances['total']
    confirmed = settings.WALLET.balances['confirmed']
    context = {
        'total': total,
        'confirmed': confirmed,
        'total - confirmed': total - confirmed,
    }
    return JsonResponse(context, status=200)
