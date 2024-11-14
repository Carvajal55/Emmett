from main.celery import app
from core.models import *
from celery import shared_task
from celery import shared_task
from django.core.mail import send_mail
from .models import Products
import requests
import time

BSALE_API_URL = 'https://api.bsale.io/v1'
BSALE_TOKEN = '1b7908fa44b56ba04a3459db5bb6e9b12bb9fadc'

@shared_task
def comparar_stock_bsale():
    # Configuración inicial
    bsale_url = f'{BSALE_API_URL}/stocks.json'
    headers = {'access_token': BSALE_TOKEN}
    productos_locales = Products.objects.values('sku', 'iderp', 'currentstock')
    productos_local_dict = {producto['iderp']: producto for producto in productos_locales}
    diferencias = []

    next_url = bsale_url
    while next_url:
        response = requests.get(next_url, headers=headers)
        if response.status_code != 200:
            print(f"Error al obtener datos de Bsale: {response.status_code} - {response.text}")
            return
        
        data = response.json()
        items = data.get('items', [])
        
        for item in items:
            bsale_stock = item['quantity']
            iderp = item['variant']['id']
            producto_local = productos_local_dict.get(iderp)
            
            if producto_local:
                resultado = {
                    "sku": producto_local['sku'],
                    "iderp": iderp,
                    "stock_local": producto_local['currentstock'],
                    "stock_bsale": bsale_stock,
                    "diferencia": bsale_stock - producto_local['currentstock']
                }
            else:
                resultado = {
                    "sku": "0",
                    "iderp": iderp,
                    "stock_local": 0,
                    "stock_bsale": bsale_stock,
                    "diferencia": None
                }

            diferencias.append(resultado)
            time.sleep(0.1)  # Simulación de procesamiento

        next_url = data.get('next')

    # Convertir el resultado a un formato de texto
    detalle = "\n".join(
        [f"SKU: {res['sku']}, IDERP: {res['iderp']}, Stock Local: {res['stock_local']}, "
         f"Stock Bsale: {res['stock_bsale']}, Diferencia: {res['diferencia']}"
         for res in diferencias]
    )

    # Enviar correo con el detalle
    send_mail(
        'Resultado de Comparación de Stock en Bsale',
        f'Resultados:\n\n{detalle}',
        'web@emmett.cl',
        ['carvajal.emmett@gmail.com'],
        fail_silently=False,
    )
# @app.task(bind=True, name='tasks.core.test_task')
# def test_task(self):
#     print("HOLA")
#     return True

# @app.task(bind=True, name='tasks.core.recordatorio_templates')
# def recordatorio_templates_celery(self, suscripcion_whatsapp_id, recordatorio_id):
#     recordatorio_templates(suscripcion_whatsapp_id, recordatorio_id)
#     return True

# @app.task(bind=True, name='tasks.core.enviar_encuesta_palumbo_celery')
# def enviar_encuesta_palumbo_celery(self):
#     enviar_encuesta_palumbo()
#     return True
