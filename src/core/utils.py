from core.models import *
import requests
import json
from pymongo import MongoClient
from django.conf import settings
import datetime
import openai
from collections import Counter
from django.db.models import F
from django.utils import timezone
from datetime import timedelta
from celery import current_app
import requests
import json
import time



    



def registrar_numero_de_qr(nombre, numero_telefono, encuesta):
    encuesta_obj = Encuesta.objects.get(sucursal=encuesta)
    numero_obj = NumeroEscaneoEncuesta.objects.create(
        encuesta=encuesta_obj,
        numero=numero_telefono,
        nombre=nombre
    )
    return numero_obj.pk

def enviar_encuesta_palumbo():
    numeros = NumeroEscaneoEncuesta.objects.filter(create_comanda=True, complete=False).order_by('-pk')
    token_ws = "EAANAlBvfOFcBO8XdUTRQmSxqBz2q28Vr7OF5ZCQK59P8J89KG0AQx0iKPU6Pkp8lLd0aZAjoUIEkJRym0Oj6D5z3oquwj30fj2LCibt5l2mvn2sHmznQ22HKeIbYku3uYxmfuDEdQufKLXltyj6MG2dmv1Svs6G9TbpR929uMqd5FLDl2Og7LLWbomXBdIBgZDZD"
    for x in numeros:
        try:
            url = "https://api-palumbo.safeware.cl/api/pos/get/datos/comanda"

            payload = json.dumps({
                "comanda": x.numero_comanda
            })
            headers = {
                'Authorization': 'Token 5c9f449a832edb88f4f4c5fba16c354791726543',
                'Content-Type': 'application/json',
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            print("Comanda", response.text)
            response = response.json()
            if response["status"] == 1:
                print(x.numero_comanda)
                print(response)
                x.complete=True
                x.servicios_meta = str(response["servicios"])
                x.cabecera_meta = str(response["cabecera"])
                x.nombre_estilista = response["servicios"][0]["nombre_prof"]
                x.cod_estilista = response["servicios"][0]["cod_prof"]
                x.save() 

                data_document = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": x.numero,
                    "type": "document",
                    "document": {
                        "link": "https://app.aurorachat.cl/comprobante/venta/palumbo?id=" + str(x.pk),
                        "filename": "{}.pdf".format(x.numero_comanda)
                    }
                }

                headers = {'Content-Type': 'application/json',
                        'Authorization': 'Bearer {}'.format(token_ws)}
                r = requests.post("https://graph.facebook.com/v16.0/{}/messages".format(
                    "387783354415355"
                ), data=json.dumps(data_document), headers=headers)       

                time.sleep(3)
                data_encuesta = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": x.numero,
                    "type": "text",
                    "text": {
                        "preview_url": False,
                        "body": "¡Por favor, tómate un momento para calificar nuestro servicio! 🌟 ¡Tu opinión es muy importante para nosotros! 🙌 https://app.aurorachat.cl/encuesta/palumbo?id="+str(x.pk)
                    }
                }

                headers = {'Content-Type': 'application/json',
                        'Authorization': 'Bearer {}'.format(token_ws)}
                r_2 = requests.post("https://graph.facebook.com/v16.0/{}/messages".format(
                    "387783354415355"
                ), data=json.dumps(data_encuesta), headers=headers)

                print("respuesta Facebook", r_2.text)
        except Exception as e:
            print(e)
            print("Falle, numero: ", x.numero)

           



def ticker_cannon():
    api_key = 'P20C7M6RqUOPIOz7Y0U'
    domain = 'cannonhome.freshdesk.com'
    password = 'x'
    base_url = f'https://{domain}/api/v2/'
    ticket_data = {
        'description': 'Prueba API Safeware',
        'subject': 'Pruebas Safeware',
        'email': 'empresa@safeware.cl',
        'priority': 1,
        'status':2,
    }
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(base_url + 'tickets', auth=(api_key, password), headers=headers, json=ticket_data)
    if response.status_code == 201:
        print('Ticket creado exitosamente.')
        print('ID del ticket:', response.json()['id'])
    else:
        print('Error al crear el ticket. Código de estado:', response.status_code)
        print('Mensaje de error:', response.text)