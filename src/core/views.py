from django.shortcuts import render, redirect
from core.models import *
from django.contrib.auth import login as login_f
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate
from django.conf import settings
from pymongo import MongoClient
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import etag
from django.template.loader import get_template
from django.template import Context
import os
from django.views.decorators.csrf import csrf_exempt
from openpyxl import Workbook
import zipfile
from django.http import HttpResponse
from io import BytesIO
import zipfile
from django.http import HttpResponse
from openpyxl import Workbook
import json
from django.contrib import messages
import requests
from weasyprint import HTML
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.mail import send_mail
from django.utils import timezone  # Para obtener la fecha y hora actual
from django.views.decorators.http import require_GET
from django.db import transaction
from django.views.decorators.http import require_POST
from reportlab.pdfgen import canvas
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import mm
from reportlab.graphics.barcode import code128
import random
import string
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
import qrcode
import io
from dotenv import load_dotenv
import datetime
from datetime import timedelta



# Carga el archivo .env
load_dotenv()

# Obtiene el token desde las variables de entorno
BSALE_API_TOKEN = os.getenv('BSALE_API_TOKEN')
BSALE_API_URL = "https://api.bsale.cl/v1"  # URL base de Bsale






@login_required(login_url='login_view')
def delete_user(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    usuario.delete()
    return JsonResponse({'message': 'Usuario eliminado exitosamente.'}, status=204)

@login_required(login_url='login_view')
def recepciones_aceptadas(request):
    return render(request, 'recepciones_aceptadas.html')

@login_required(login_url='login_view')
def crear_sector(request):
    return render(request, 'crear_sector.html')

@login_required(login_url='login_view')
def recepciones_aceptadas(request):
    return render(request, 'recepciones_aceptadas.html')

@login_required(login_url='login_view')
def crear_usuario_view(request):
    return render(request, 'crear_usuarios.html')

@login_required(login_url='login_view')
def buscar_productos(request):
    return render(request, 'buscar_productos.html')

@login_required(login_url='login_view')
def recepciones_pendientes(request):
    return render(request, 'recepciones_pendientes.html')

@login_required(login_url='login_view')
def factura_aprobar_view(request, id):
    return render(request, 'factura_aprobar.html', {'factura_id': id})

@login_required(login_url='login_view')
def ingresar_documentos(request):
    return render(request, 'ingresar_documentos.html')

@login_required(login_url='login_view')
def anadir_psector(request):
    # Asegurarse de que el usuario tiene un objeto `usuario` con un rol
    
    return render(request, 'anadir_psector.html')

@login_required(login_url='login_view')
def cuadrar_sector_view(request):
    return render(request, 'cuadrar_sector.html')

@login_required(login_url='login_view')
def despacho(request):
    return render(request, 'despacho.html')

@login_required(login_url='login_view')
def editar_productos(request):
    return render(request, 'editar_productos.html')


""" 
APIS  """

def login_view(request):
    template_name = "login.html"
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Autenticación para superusuarios (Django `User`)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login_f(request, user)
            return redirect("index")
        else:
            # Si no es superusuario, verifica en el modelo `Usuario`
            try:
                usuario_model = Usuario.objects.get(correo=username)
                if usuario_model.clave == password:
                    # Verifica rol y otras validaciones si es necesario
                    if usuario_model.rol == 'SADMIN':
                        # Almacena al usuario en sesión para validar permisos
                        request.session['usuario_id'] = usuario_model.id
                        request.session['usuario_rol'] = usuario_model.rol
                        return redirect("index")
                    else:
                        context['error_message'] = 'No tienes permisos de SuperAdmin.'
                else:
                    context['error_message'] = 'La contraseña es incorrecta.'
            except Usuario.DoesNotExist:
                context['error_message'] = 'El usuario no existe.'

    return render(request, template_name, context)



@login_required(login_url='login_view')
def index(request):
    template_name = "index.html"
    context = {}
   
    return render(request, template_name, context)

# Crear usuario
@csrf_exempt
@login_required(login_url='login_view')
def create_user(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # Obtener los datos del nuevo usuario
        correo = data.get('correo')
        clave = data.get('clave', '40emmett90')  # Clave por defecto
        nombres_apellidos = data.get('nombres_apellidos', '')
        rut = data.get('rut', '')
        telefono = data.get('telefono', '')
        rol = data.get('rol', 'VENTAS')  # Rol por defecto en caso de no proporcionarse

        # Validar campo de correo
        if not correo:
            return JsonResponse({'error': 'El campo correo es obligatorio.'}, status=400)

        # Crear el usuario en el modelo User de Django
        try:
            django_user = User.objects.create_user(
                username=correo,  # Usa el correo como nombre de usuario
                email=correo,
                password=clave  # La contraseña será encriptada automáticamente
            )
            django_user.save()
        except Exception as e:
            return JsonResponse({'error': f'Error al crear el usuario de Django: {str(e)}'}, status=400)

        # Crear el usuario en el modelo Usuario y asociarlo al usuario de Django
        usuario = Usuario.objects.create(
            user=django_user,  # Relación con el usuario de Django
            correo=correo,
            clave=clave,
            nombres_apellidos=nombres_apellidos,
            rut=rut,
            telefono=telefono,
            rol=rol
        )

        return JsonResponse({'message': 'Usuario creado exitosamente.'}, status=201)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# Listar usuarios
@login_required(login_url='login_view')
def list_users(request):
    print("Petición recibida en list_users")  # Imprimir cuando se reciba la petición

    # Obtener los usuarios
    usuarios = Usuario.objects.all()

    # Imprimir los usuarios obtenidos
    print(f"Usuarios encontrados: {usuarios}")

    # Formatear los datos de los usuarios
    usuarios_data = [{
        'id': usuario.id,
        'correo': usuario.correo,
        'nombres_apellidos': usuario.nombres_apellidos,
        'rut': usuario.rut,
        'telefono': usuario.telefono,
    } for usuario in usuarios]

    # Imprimir los datos formateados
    print(f"Datos formateados para respuesta: {usuarios_data}")

    # Devolver los datos como JSON
    return JsonResponse(usuarios_data, safe=False)


# Editar usuario
@csrf_exempt
@login_required(login_url='login_view')  # Verificación de login
def update_user(request, user_id):
    if request.method == 'PUT':
        try:
            usuario = get_object_or_404(Usuario, id=user_id)
            data = json.loads(request.body)

            # Actualizar los datos del usuario
            usuario.correo = data.get('correo', usuario.correo)
            usuario.clave = data.get('clave', usuario.clave)  # Asegúrate de manejar bien las contraseñas
            usuario.nombres_apellidos = data.get('nombres_apellidos', usuario.nombres_apellidos)
            usuario.rut = data.get('rut', usuario.rut)
            usuario.telefono = data.get('telefono', usuario.telefono)

            usuario.save()

            return JsonResponse({'message': 'Usuario actualizado exitosamente.'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)








""" BUSCAR PRODUCTOS """

def listar_bodegas(request):
    # Filtrar solo las bodegas con los IDs especificados
    bodega_ids_included = [1, 2, 4, 6, 9, 10]
    bodegas = Bodega.objects.filter(idoffice__in=bodega_ids_included)
    
    # Preparar la respuesta solo con las bodegas seleccionadas
    bodegas_data = [
        {
            'id': bodega.idoffice,
            'name': bodega.name
        }
        for bodega in bodegas
    ]
    
    return JsonResponse({'bodegas': bodegas_data})


def buscar_productosAPI(request):
    query = request.GET.get('q', '').strip()
    page = int(request.GET.get('page', 1))

    if not query:
        return JsonResponse({
            'products': [],
            'total_pages': 1,
            'current_page': 1
        }, status=200)

    # Filtrar productos por SKU, nombre o prefijo
    productos = Products.objects.filter(
        Q(sku__icontains=query) | Q(nameproduct__icontains=query) | Q(prefixed__icontains=query)
    ).prefetch_related(
        'unique_products'
    )

    # Obtener los sectores válidos directamente
    valid_sectores = Sectoroffice.objects.filter(
        idoffice__in=[10, 9, 7, 6, 5, 4, 2, 1]
    ).exclude(
        namesector__in=['XT99-99', 'NRN1-1']
    )
    valid_sector_map = {sector.idsectoroffice: sector.namesector for sector in valid_sectores}

    # Paginación
    paginator = Paginator(productos, 10)
    try:
        productos_page = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        productos_page = paginator.page(1)

    # Serializar productos
    productos_data = []
    for producto in productos_page:
        unique_products = producto.unique_products.filter(state=0)

        # Procesar stock y ubicaciones válidas
        stock_total = 0
        unique_products_data = []
        for up in unique_products:
            sector_name = valid_sector_map.get(up.location)
            if sector_name:
                stock_total += 1
                unique_products_data.append({
                    'superid': up.superid,
                    'locationname': sector_name,
                })

        # Serializar producto principal
        productos_data.append({
            'id': producto.id,
            'sku': producto.sku,
            'name': producto.nameproduct,
            'price': producto.lastprice or 0,
            'stock_total': stock_total,
            'unique_products': unique_products_data,
            'prefixed': producto.prefixed or '',
            'brands': producto.brands or '',
            'iderp': producto.iderp or '',
            'alto': producto.alto or 0,
            'largo': producto.largo or 0,
            'profundidad': producto.profundidad or 0,
            'peso': producto.peso or 0,
        })

    # Respuesta JSON
    return JsonResponse({
        'products': productos_data,
        'total_pages': paginator.num_pages,
        'current_page': productos_page.number,
    }, safe=False)




def producto_detalles(request, product_id):
    try:
        producto = Products.objects.prefetch_related('unique_products').get(id=product_id)

        bodega_ids_included = [1, 2, 4, 6, 9, 10]
        bodegas = Bodega.objects.filter(idoffice__in=bodega_ids_included)
        bodega_mapping = {bodega.idoffice: bodega.name for bodega in bodegas}

        sectores = Sectoroffice.objects.all()
        sector_mapping = {sector.idsectoroffice: sector for sector in sectores}

        excluded_sectors = Sectoroffice.objects.filter(namesector="XT99-99") | Sectoroffice.objects.filter(zone="NARN") | Sectoroffice.objects.filter(zone="NRN") 
        unique_products = producto.unique_products.exclude(location__in=excluded_sectors.values_list('idsectoroffice', flat=True))

        bodegas_stock = {bodega.idoffice: 0 for bodega in bodegas}

        unique_products_data = []
        for unique_product in unique_products:
            sector = sector_mapping.get(unique_product.location)
            if sector and isinstance(sector, Sectoroffice):
                bodega_name = bodega_mapping.get(sector.idoffice, 'Bodega desconocida')
                if sector.idoffice in bodegas_stock:
                    bodegas_stock[sector.idoffice] += 1
                unique_products_data.append({
                    'superid': unique_product.superid,
                    'locationname': sector.namesector,
                    'bodega': bodega_name,
                })
            

        response_data = {
            'id': producto.id,
            'sku': producto.sku,
            'name': producto.nameproduct,
            'price': producto.lastprice,
            'stock_total': sum(bodegas_stock.values()),
            'bodegas': {bodega_mapping[bodega_id]: stock for bodega_id, stock in bodegas_stock.items()},
            'unique_products': unique_products_data,
        }

        return JsonResponse(response_data)

    except Products.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)


#FACTURAS
@csrf_exempt
@require_POST
def actualizar_precio(request):
    try:
        # Cargar los datos enviados por el frontend
        print("Inicio de la función 'actualizar_precio'")
        data = json.loads(request.body)
        print(f"Datos recibidos: {data}")

        id_erp = data.get('iderp')  # ID de la variante
        sku = data.get('sku')
        b_price = data.get('bPrice')  # Precio bruto con impuestos
        type = data.get('type')  # Tipo de lista de precios

        # Validar los datos recibidos
        if not id_erp or not sku or not b_price or not type:
            print("Error: Datos incompletos")
            return JsonResponse({'error': 'Datos incompletos'}, status=400)

        # Paso 1: Construir el URL para obtener los detalles del precio en Bsale
        url_costs = f"{BSALE_API_URL}/price_lists/{type}/details.json?variantid={id_erp}"
        headers = {
            'access_token': BSALE_API_TOKEN,
            'Content-Type': 'application/json'
        }
        print(f"URL de consulta de costos: {url_costs}")

        # Realizar la solicitud GET para obtener información del detalle
        response = requests.get(url_costs, headers=headers)
        print(f"Respuesta de la consulta GET: {response.status_code}")
        print(f"Contenido de la respuesta GET: {response.text}")

        # Verificar el estado de la respuesta
        if response.status_code != 200:
            print("Error al obtener datos de Bsale")
            return JsonResponse({'error': 'Error al obtener datos de Bsale', 'detalle': response.text}, status=response.status_code)

        # Procesar los datos recibidos de Bsale
        bsale_data = response.json()
        items = bsale_data.get('items', [])
        if not items:
            print("No se encontraron ítems en la respuesta de Bsale")
            return JsonResponse({'error': 'No se encontró ningún ítem en la respuesta de Bsale'}, status=404)

        # Obtener id_detalle desde el primer ítem
        id_detalle = items[0].get('id')
        if not id_detalle:
            print("Error: No se encontró id_detalle en la respuesta")
            return JsonResponse({'error': 'No se encontró id_detalle en la respuesta de Bsale'}, status=404)

        print(f"ID detalle obtenido: {id_detalle}")

        # Paso 2: Construir la URL para actualizar el precio en Bsale
        url_update_price = f"{BSALE_API_URL}/price_lists/{type}/details/{id_detalle}.json"
        print(f"URL para actualizar precio: {url_update_price}")

        # Paso 3: Calcular el precio base sin IVA
        variant_value = float(b_price) / 1.19
        update_data = {
            'variantValue': variant_value,
            "id": id_detalle
        }
        print(f"Datos para la actualización (PUT): {update_data}")

        # Paso 4: Realizar la solicitud PUT para actualizar el precio
        put_response = requests.put(url_update_price, headers=headers, json=update_data)
        print(f"Respuesta de la solicitud PUT: {put_response.status_code}")
        print(f"Contenido de la respuesta PUT: {put_response.text}")

        # Verificar el estado de la solicitud PUT
        if put_response.status_code != 200:
            print("Error al actualizar el precio en Bsale")
            return JsonResponse({'error': 'Error al actualizar el precio en Bsale', 'detalle': put_response.text}, status=put_response.status_code)

        # Obtener la respuesta de la actualización
        updated_data = put_response.json()
        print(f"Datos actualizados en Bsale: {updated_data}")

        # Paso 5: Actualizar el lastPrice en la base de datos local
        from .models import Products  # Importa el modelo si no está ya importado
        try:
            print(f"Buscando el producto con SKU: {sku}")
            product = Products.objects.get(sku=sku)
            print(f"Producto encontrado: {product}")
            product.lastprice = float(b_price)
            product.save()
            print(f"Producto actualizado en la base de datos local: {product}")
        except Products.DoesNotExist:
            print(f"Error: Producto con SKU {sku} no encontrado en la base de datos local")
            return JsonResponse({'error': f'Producto con SKU {sku} no encontrado en la base de datos'}, status=404)
        except ValueError:
            print(f"Error: El valor proporcionado para lastprice ({b_price}) no es válido")
            return JsonResponse({'error': f'El valor proporcionado para lastprice ({b_price}) no es válido.'}, status=400)

        # Retornar la respuesta exitosa
        print("Precio actualizado correctamente")
        return JsonResponse({
            'message': 'Precio actualizado correctamente en Bsale y lastPrice actualizado en la base de datos local',
            'updated_data': updated_data
        }, status=200)

    except json.JSONDecodeError:
        print("Error: Datos inválidos")
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
def listar_compras(request):
    # Obtener parámetros de filtro y paginación desde el request
    status = request.GET.get('status')  # Aceptará '0', '1', '2', '3' o 'all'
    page_number = request.GET.get('page', 1)
    search_query = request.GET.get('q', '').strip()  # Búsqueda por folio

    # Filtrar las facturas según el estado
    if status == '0':
        compras = Purchase.objects.filter(status=0)  # Pendientes
    elif status == '1':
        compras = Purchase.objects.filter(status=1)  # Aceptadas
    elif status == '2':
        compras = Purchase.objects.filter(status=2)  # Rechazadas
    elif status == '3':
        compras = Purchase.objects.filter(status=3)  # Procesadas
    else:
        compras = Purchase.objects.all()  # Todas las facturas

    # Filtrar por folio si se proporciona un término de búsqueda
    if search_query:
        compras = compras.filter(number__icontains=search_query)

    # Ordenar en orden descendente por fecha de creación
    compras = compras.order_by('-dateadd')

    # Crear paginador
    paginator = Paginator(compras, 10)  # 10 facturas por página
    page_obj = paginator.get_page(page_number)

    # Formatear los datos en una lista
    compras_list = []
    for compra in page_obj:
        # Leer el archivo JSON para obtener datos adicionales si es necesario
        try:
            with open(compra.urljson, 'r') as json_file:
                factura_data = json.load(json_file)

            # Excluir facturas impresas solo si el estado no es "Procesadas"
            if factura_data.get('invoice_printed', False) and status != '3':
                continue  # Saltar facturas ya impresas
        except FileNotFoundError:
            pass  # Continuar si el archivo JSON no existe

        compras_list.append({
            'id': compra.id,
            'supplier': compra.supplier,
            'supplierName': compra.suppliername,
            'typeDocument': compra.typedoc,
            'number': compra.number,
            'status': compra.status,
            'subtotal': compra.subtotal,
            'dateAdd': compra.dateadd.strftime('%Y-%m-%d'),
            'printStatus': compra.printstatus,
            'urlJson': compra.urljson  # Incluir URL JSON para detalles
        })

    # Devolver los datos como JSON, incluyendo la información de paginación
    response_data = {
        'data': compras_list,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count
    }
    return JsonResponse(response_data)

@csrf_exempt
def resumen_factura(request):
    if request.method == 'POST':
        print("Payload recibido:", request.POST)

        # Obtener el campo `urlJson` del payload
        url_json = request.POST.get('urlJson')

        if not url_json:
            return JsonResponse({'error': 'No se ha proporcionado la URL del archivo JSON.'}, status=400)
        
        # Generar la ruta del archivo JSON
        json_file_path = os.path.join(settings.BASE_DIR, url_json.strip('/'))

        # Verificar si el archivo JSON existe
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                json_data = json.load(file)
                
                # Extraer los valores del header y detalles
                header = json_data.get('headers', {})  # Asegurar que sea un diccionario
                detalles = json_data.get('details', [])

                # Extraer el número del documento del header
                n_document = header.get('nDocument', None)  # Usar el nombre correcto de la clave

                # Añadir el campo `printed` si no existe en cada detalle
                for detalle in detalles:
                    if 'printed' not in detalle:
                        detalle['printed'] = False

                # Determinar si la factura completa está marcada como impresa
                invoice_printed = all(detalle.get('printed', False) for detalle in detalles)

                # Guardar los cambios en el archivo JSON para que persista la estructura
                with open(json_file_path, 'w') as file:
                    json.dump(json_data, file, indent=4)

                # Enviar los detalles y la URL del JSON como respuesta
                return JsonResponse({
                    'details': detalles,
                    'number': n_document,  # Usar n_document en la respuesta
                    'invoice_printed': invoice_printed,
                    'urlJson': url_json  # Incluye la URL del JSON en la respuesta
                })
        else:
            return JsonResponse({'error': 'Archivo JSON no encontrado.'}, status=404)
    else:
        return JsonResponse({'error': 'Método no permitido.'}, status=405)

@csrf_exempt
def listar_facturas_pendientes(request):
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)

    # Filtrar facturas pendientes (status = 0) y ordenar por fecha de creación descendente
    facturas = Purchase.objects.filter(status=0).order_by('-dateadd')  # Asegúrate de que `dateadd` sea el campo correcto

    # Filtrar por número de folio si se introduce una búsqueda
    if query:
        facturas = facturas.filter(number__icontains=query)

    # Paginación (10 facturas por página)
    paginator = Paginator(facturas, 10)
    try:
        facturas_page = paginator.page(page)
    except PageNotAnInteger:
        facturas_page = paginator.page(1)
    except EmptyPage:
        facturas_page = paginator.page(paginator.num_pages)

    # Formatear los datos de las facturas
    facturas_data = [{
        'id': factura.id,
        'typeDocument': factura.typedoc, 
        'number': factura.number,
        'supplier': factura.supplier,
        'supplierName': factura.suppliername,
        'subtotal': factura.subtotal,
        'status': factura.status,
        'dateAdd': factura.dateadd.strftime('%Y-%m-%d'),  # Formatear la fecha
    } for factura in facturas_page]

    # Crear la respuesta
    response = {
        'data': facturas_data,
        'total_pages': paginator.num_pages,
        'current_page': facturas_page.number,
    }

    return JsonResponse(response)

@csrf_exempt
def rechazar_factura(request):
    if request.method == 'POST':
        # Revisar si el id está en el POST
        factura_id = request.POST.get('id')
        if not factura_id:
            return JsonResponse({'error': 'ID de factura no proporcionado.'}, status=400)

        try:
            # Buscar la factura con el ID proporcionado
            factura = Purchase.objects.get(id=factura_id)
            # Cambiar el estado a "Rechazado"
            factura.status = 2
            factura.save()
            return JsonResponse({'message': 'Factura rechazada con éxito.'})
        except Purchase.DoesNotExist:
            # Si no se encuentra la factura, devolver un mensaje de error
            return JsonResponse({'error': 'Factura no encontrada.'}, status=404)
    return JsonResponse({'error': 'Método no permitido.'}, status=405)


#Aprobar Facturas

def calcular_stock_bodegas(request):
    """
    Calcula el stock total de los productos que están en las bodegas especificadas.
    """
    try:
        # IDs de las bodegas que se deben incluir en el cálculo
        bodegas_ids = [10, 9, 7, 6, 5, 4, 2, 1]

        # Filtrar los productos en las bodegas especificadas
        productos_bodegas = Uniqueproducts.objects.filter(locationname__in=bodegas_ids)

        # Extraer los IDs de los productos relacionados
        productos_ids = productos_bodegas.values_list('product_id', flat=True)

        # Calcular el stock total de los productos filtrados
        total_stock = Products.objects.filter(idproduct__in=productos_ids).aggregate(total=models.Sum('currentstock'))['total'] or 0

        return JsonResponse({"success": True, "total_stock": total_stock}, status=200)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@csrf_exempt
def aprobar_factura(request):
    if request.method == 'POST':
        try:
            # Parsear los datos enviados desde el frontend
            data = json.loads(request.body)
            factura_id = data.get('factura_id')  # ID de la factura enviada desde el frontend
            detalles = data.get('detalles', [])

            if not factura_id:
                return JsonResponse({'error': 'No se proporcionó el ID de la factura.'}, status=400)

            if not detalles:
                return JsonResponse({'error': 'No se proporcionaron detalles para actualizar.'}, status=400)

            # Lista para almacenar los resultados
            productos_actualizados = []
            productos_no_encontrados = []

            for detalle in detalles:
                sku = detalle.get('sku')
                costo = detalle.get('cost')

                if not sku or costo is None:
                    continue  # Ignorar detalles incompletos

                try:
                    # Buscar el producto por SKU y actualizar el costo
                    producto = Products.objects.get(sku=sku)
                    producto.lastcost = float(costo)
                    producto.save()

                    # Agregar el producto a la lista de actualizados
                    productos_actualizados.append({'sku': producto.sku, 'lastcost': producto.lastcost})
                except Products.DoesNotExist:
                    # Agregar los SKUs no encontrados a una lista separada
                    productos_no_encontrados.append(sku)

            # Cambiar el estado de la factura a "Aprobada" (1)
            try:
                factura = Purchase.objects.get(id=factura_id)
                factura.status = 1  # Estado "Aprobada"
                factura.save()
            except Purchase.DoesNotExist:
                return JsonResponse({'error': 'Factura no encontrada.'}, status=404)

            # Retornar la respuesta exitosa con los resultados
            return JsonResponse({
                'message': 'Factura aprobada con éxito.',
                'productos_actualizados': productos_actualizados,
                'productos_no_encontrados': productos_no_encontrados,
                'factura_status': factura.status
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos enviados no son válidos.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)

@csrf_exempt
def obtener_factura(request):
    if request.method == 'POST':
        # Obtener el ID de la factura desde el POST
        id_factura = request.POST.get('id')
        print("ID de la factura recibido:", id_factura)
        
        # Buscar la factura correspondiente en la base de datos
        factura = get_object_or_404(Purchase, id=id_factura)
        
        # Imprimir todos los atributos de la factura para depuración
        print("Contenido completo del objeto Purchase:")
        print(factura.__dict__)

        # Obtener la URL del archivo JSON desde la factura
        url_json = factura.urljson.strip('/')  # Asegurarse de eliminar cualquier barra invertida al inicio

        # Generar la ruta completa del archivo JSON
        json_file_path = os.path.join(settings.BASE_DIR, url_json)
        print(f"Ruta completa del archivo JSON: {json_file_path}")

        # Verificar si el archivo JSON existe y obtener los detalles
        detalles = []
        try:
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r', encoding='utf-8') as file:
                    json_data = json.load(file)
                    detalles = json_data.get('details', [])
                    if detalles is None:
                        detalles = []  # Asegurarse de que sea una lista vacía si no existen detalles
            else:
                print("Archivo JSON no encontrado en la ruta especificada.")
                return JsonResponse({'error': 'Archivo JSON de detalles no encontrado.'}, status=404)
        except json.JSONDecodeError:
            print("Error al decodificar el archivo JSON.")
            return JsonResponse({'error': 'Error al decodificar el archivo JSON.'}, status=500)

        # Preparar los datos para la respuesta en JSON
        data = {
            "headers": {
                "supplier": factura.supplier,
                "supplierName": factura.suppliername,
                "typeDocument": factura.typedoc,
                "nDocument": factura.number,
                "dcto": factura.observation,  
                "datePurchase": factura.dateadd,
                "dateExpired": factura.dateproccess,
                "observation": factura.observation,
                "typePay": "No Pagado al Proveedor",
                "nCheque": "0",  
                "qtyCheque": "0",  
                "subtotal": factura.subtotal,
                "urlPDF": factura.urljson,
                "urlJson": factura.urljson,
                "dateReception": factura.dateadd,
                "userProcess": "Usuario encargado",  
                "urlImg": factura.urlimg,  
                "subtotalNeto": factura.subtotal,
                "subtotalBruto": factura.subtotal + (factura.subtotal * 0.19),
                "statusCss": "alert-info",  
                "imgInvoice": factura.urlimg,
                "statusInvoiceD": factura.status,
                "dcto_subtotal" : factura.subtotal_with_discount
            },
            "details": detalles,  # Detalles extraídos del archivo JSON
        }

        # Retornar la respuesta como JSON
        return JsonResponse(data, safe=False)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)

""" Ingresar Documentos """

@csrf_exempt
def actualizar_precio_masivo(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            detalles = data.get('detalles', [])

            if not detalles:
                return JsonResponse({'status': 'error', 'message': 'No se proporcionaron detalles para actualizar.'}, status=400)

            errores = []
            actualizados = []

            for detalle in detalles:
                id_erp = detalle.get('iderp')
                sku = detalle.get('sku')
                b_price = detalle.get('bPrice')
                type = detalle.get('type', 3)  # Lista base predeterminada

                if not id_erp or not sku or not b_price:
                    errores.append({'sku': sku, 'message': 'Datos incompletos'})
                    continue

                try:
                    # Paso 1: Consultar el detalle de la lista de precios en Bsale
                    url_costs = f"{BSALE_API_URL}/price_lists/{type}/details.json?variantid={id_erp}"
                    headers = {
                        'access_token': BSALE_API_TOKEN,
                        'Content-Type': 'application/json'
                    }

                    response = requests.get(url_costs, headers=headers)
                    if response.status_code != 200:
                        errores.append({'sku': sku, 'message': 'Error al obtener datos de Bsale'})
                        continue

                    bsale_data = response.json()
                    items = bsale_data.get('items', [])
                    if not items:
                        errores.append({'sku': sku, 'message': 'No se encontró ningún ítem en Bsale'})
                        continue

                    id_detalle = items[0].get('id')
                    if not id_detalle:
                        errores.append({'sku': sku, 'message': 'No se encontró id_detalle en Bsale'})
                        continue

                    # Paso 2: Actualizar el precio en Bsale
                    url_update_price = f"{BSALE_API_URL}/price_lists/{type}/details/{id_detalle}.json"
                    variant_value = float(b_price) / 1.19
                    update_data = {'variantValue': variant_value, "id": id_detalle}

                    put_response = requests.put(url_update_price, headers=headers, json=update_data)
                    if put_response.status_code != 200:
                        errores.append({'sku': sku, 'message': 'Error al actualizar el precio en Bsale'})
                        continue

                    # Paso 3: Actualizar el precio en la base de datos local
                    try:
                        product = Products.objects.get(sku=sku)
                        product.lastprice = float(b_price)
                        product.save()
                        actualizados.append({'sku': sku, 'message': 'Precio actualizado correctamente'})
                    except Products.DoesNotExist:
                        errores.append({'sku': sku, 'message': 'Producto no encontrado en la base de datos local'})
                    except ValueError:
                        errores.append({'sku': sku, 'message': f'Valor inválido para Precio Base: {b_price}'})

                except Exception as e:
                    errores.append({'sku': sku, 'message': f'Error inesperado: {str(e)}'})

            # Respuesta final
            return JsonResponse({
                'status': 'success',
                'message': 'Precios procesados.',
                'actualizados': actualizados,
                'errores': errores
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Datos inválidos'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

@csrf_exempt
def create_category(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        if not name:
            return JsonResponse({'error': 'El nombre de la categoría es obligatorio.'}, status=400)
        category, created = Category.objects.get_or_create(name=name)
        if created:
            return JsonResponse({'message': 'Categoría creada correctamente.'})
        return JsonResponse({'error': 'La categoría ya existe.'}, status=400)
    
@csrf_exempt
def create_brand(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        if not name:
            return JsonResponse({'error': 'El nombre de la marca es obligatorio.'}, status=400)
        brand, created = Brand.objects.get_or_create(name=name)
        if created:
            return JsonResponse({'message': 'Marca creada correctamente.'})
        return JsonResponse({'error': 'La marca ya existe.'}, status=400)   
    
def search_brands(request):
    query = request.GET.get('q', '')
    if query:
        brands = Brand.objects.filter(name__icontains=query).values('id', 'name')
    else:
        brands = Brand.objects.all().values('id', 'name')
    return JsonResponse(list(brands), safe=False)


def get_categories(request):
    query = request.GET.get('q', '')
    categories = Category.objects.filter(name__icontains=query)[:20]
    category_list = [{'id': category.id, 'name': category.name} for category in categories]
    return JsonResponse({'categories': category_list})

def get_factura(request):
    tipo_documento = request.GET.get('type')
    numero_documento = request.GET.get('number')

    # Buscar la factura por tipo, número de documento y estado
    factura = get_object_or_404(
        Purchase, 
        typedoc=tipo_documento, 
        number=numero_documento,
        status__in=[0, 2]  # Solo estados Pendientes (0) o Rechazados (2)
    )

    # Leer el archivo JSON desde el campo `urlJson`
    try:
        with open(factura.urljson, 'r') as json_file:
            data = json.load(json_file)
        return JsonResponse(data, safe=False)
    except FileNotFoundError:
        return JsonResponse({'error': 'El archivo JSON no existe.'}, status=404)

def get_suppliers(request):
    # Obtiene el parámetro de búsqueda (si existe)
    query = request.GET.get('q', '')

    # Filtrar proveedores por RUT o nombre si hay un término de búsqueda
    if query:
        suppliers = Supplier.objects.filter(
            Q(namesupplier__icontains=query) | Q(rutsupplier__icontains=query)
        ).values('id', 'namesupplier', 'rutsupplier')
    else:
        # Si no hay búsqueda, devolver todos los proveedores
        suppliers = Supplier.objects.all().values('id', 'namesupplier', 'rutsupplier')

    # Convertimos a lista y retornamos en formato JSON
    return JsonResponse(list(suppliers), safe=False)

@csrf_exempt
def create_supplier(request):
    if request.method == 'POST':
        # Obtener los datos del proveedor desde la solicitud
        rut_supplier = request.POST.get('rut', '')
        name_supplier = request.POST.get('nombre', '')
        alias_supplier = request.POST.get('alias', '')
        print(rut_supplier,name_supplier,alias_supplier,"AAAAAA")
        if not rut_supplier or not name_supplier:
            return JsonResponse({'error': 'Datos incompletos para crear el proveedor.'}, status=400)

        # Crear un nuevo proveedor
        try:
            supplier = Supplier.objects.create(
                rutsupplier=rut_supplier,
                namesupplier=name_supplier,
                alias=alias_supplier
            )
            return JsonResponse({'message': 'Proveedor creado correctamente.', 'id': supplier.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)

from .models import Products, Brand
from datetime import datetime

@csrf_exempt
def crear_producto(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # Obtener datos del formulario enviados desde el frontend
        nombre_producto = data.get("nombre")
        precio = data.get("precio")
        marca = data.get("marca")
        proveedor_id = data.get("proveedor")
        categoria = data.get("categoria")
        alto = data.get("alto")
        largo = data.get("largo")
        profundidad = data.get("profundidad")
        peso = data.get("peso")
        alias = data.get("alias")

        # Validar que la marca exista en la base de datos
        marcas_existentes = [brand.name for brand in Brand.objects.all()]
        if marca not in marcas_existentes:
            return JsonResponse({"error": f"La marca '{marca}' no existe. Selecciona una marca válida."}, status=400)

        # Verificamos que la categoría esté definida
        if not categoria:
            return JsonResponse({"error": "La categoría es obligatoria para generar el SKU."}, status=400)

        # Generar el SKU con el prefijo correspondiente y el correlativo
        sku = obtener_correlativo(categoria)

        # Generar el código de barras comenzando con "9999"
        bar_code = f"9999{get_random_string(8, '0123456789')}"

        # Crear el JSON para la solicitud a Bsale (Producto Principal)
        bsale_product_data = {
            "name": nombre_producto,
            "description": f"{nombre_producto} - {marca}",
            "code": sku,
            "barCode": bar_code,
            "price": precio,
            "height": alto,
            "width": largo,
            "depth": profundidad,
            "weight": peso
        }

        headers = {
            "Content-Type": "application/json",
            "access_token": BSALE_API_TOKEN
        }

        # Crear el Producto en Bsale
        response_product = requests.post(f"{BSALE_API_URL}/products.json", json=bsale_product_data, headers=headers)

        if response_product.status_code == 201:
            bsale_product = response_product.json()

            # Crear la Variante en Bsale asociada al producto
            bsale_variant_data = {
                "productId": bsale_product["id"],
                "description": "",
                "barCode": f"{bar_code}01",
                "code": f"{sku}",
                "unlimitedStock": 0,
                "allowNegativeStock": 0
            }

            response_variant = requests.post(f"{BSALE_API_URL}/variants.json", json=bsale_variant_data, headers=headers)

            if response_variant.status_code == 201:
                bsale_variant = response_variant.json()

                # Guardar el producto en la base de datos local con el idERP como el ID de la variante
                nuevo_producto = Products.objects.create(
                    sku=sku,
                    nameproduct=nombre_producto,
                    prefixed = alias,
                    brands=marca,
                    codebar=bar_code,
                    iderp=bsale_variant["id"],  # ID de la variante en lugar del producto
                    lastprice=precio,
                    codsupplier=proveedor_id,
                    createdate=datetime.now().date(),
                    alto=alto,
                    largo=largo,
                    profundidad=profundidad,
                    peso=peso,
                )

                return JsonResponse({"message": "Producto y variante creados exitosamente", "product": nuevo_producto.sku, "variant_id": bsale_variant["id"]}, status=201)
            else:
                return JsonResponse({"error": "Error al crear la variante en Bsale", "details": response_variant.json()}, status=400)
        else:
            return JsonResponse({"error": "Error al crear el producto en Bsale", "details": response_product.json()}, status=400)


  

def get_sku_prefix(categoria):
    prefix_map = {
        "audio": "AUD",
        "electronica": "AUD",
        "instrumentos": "MUS",
        "estudio": "EST",
        "iluminacion": "ILU",
        "otros": "OTR"
    }
    return prefix_map.get(categoria)

import re

# Función para obtener el siguiente número correlativo de SKU en una categoría
def obtener_correlativo(categoria):
    # Obtener el prefijo correspondiente a la categoría
    prefix = get_sku_prefix(categoria)

    # Obtener todos los productos de la base de datos
    productos = Products.objects.all()

    # Lista para almacenar los números correlativos de todos los SKUs que coincidan con el prefijo
    numeros_sku = []

    # Recorremos cada producto y extraemos el número correlativo del SKU solo si coincide con el prefijo
    for producto in productos:
        match = re.match(rf'({prefix})(\d+)', producto.sku)  # Separa el prefijo (3 letras) y el número
        if match:
            numero = int(match.group(2))  # Convertimos la parte numérica en un entero
            numeros_sku.append(numero)

    # Ordenamos la lista de números de mayor a menor
    numeros_sku.sort(reverse=True)

    # Imprimimos los 5 SKUs más altos para verificar
    print("Los 5 SKUs más altos:", numeros_sku[:5])

    # Si existen números, tomamos el más alto y le sumamos uno
    if numeros_sku:
        nuevo_numero = numeros_sku[0] + 1
    else:
        nuevo_numero = 1  # Si no hay productos en esta categoría, comenzamos desde 1

    # Formatear el nuevo número correlativo con ceros a la izquierda y añadir el prefijo
    return f"{prefix}{str(nuevo_numero).zfill(5)}"

@csrf_exempt
def generar_json(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Obtener los datos necesarios del encabezado
            headers = data.get('headers', {})
            supplier = headers.get('supplier', '')
            supplier_name = headers.get('supplierName', '')
            type_document = headers.get('typeDocument', None)
            number_document = headers.get('nDocument', None)
            observation = headers.get('observation', '')
            date_purchase = headers.get('datePurchase', None)
            url_img = headers.get('urlImg', '')
            global_discount = float(headers.get('dcto', 0) or 0)  # Descuento global

            # Crear el nombre del archivo basado en los datos del encabezado
            file_name = f"s_{supplier}t_{type_document}f_{number_document}.json"

            # Construir la ruta relativa de guardado
            relative_file_path = os.path.join('models', 'invoices', 'json', file_name)
            absolute_file_path = os.path.join(settings.BASE_DIR, relative_file_path)

            # Crear las carpetas si no existen
            os.makedirs(os.path.dirname(absolute_file_path), exist_ok=True)

            # Variables para calcular los totales
            subtotal_without_discount = 0
            subtotal_with_discount = 0

            # Procesar los detalles de la factura
            for detalle in data.get('details', []):
                cost = float(detalle.get('cost', 0))  # Convertir costo a número
                product_discount = float(detalle.get('dctoItem', global_discount) or 0)  # Convertir descuento a número

                # Calcular el costo con descuento
                cost_with_discount = cost - (cost * (product_discount / 100))

                # Actualizar subtotales
                subtotal_without_discount += cost * detalle.get('qty', 1)  # Considerar la cantidad
                subtotal_with_discount += cost_with_discount * detalle.get('qty', 1)  # Considerar la cantidad

                # Agregar estos campos al detalle
                detalle['cost_with_discount'] = cost_with_discount  # Costo con descuento

            # Calcular IVA y subtotales finales
            iva_rate = 0.19  # Tasa de IVA (19%)
            iva_amount = subtotal_with_discount * iva_rate
            subtotal_bruto = subtotal_with_discount + iva_amount

            # Añadir los subtotales y el IVA al encabezado
            headers['subtotalWithoutDiscount'] = subtotal_without_discount
            headers['subtotalWithDiscount'] = subtotal_with_discount
            headers['iva'] = iva_amount
            headers['subtotalBruto'] = subtotal_bruto

            # Actualizar el JSON con los nuevos encabezados
            data['headers'] = headers

            # Guardar el JSON en el archivo especificado
            with open(absolute_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)

            # Buscar si la factura ya existe
            purchase, created = Purchase.objects.update_or_create(
                typedoc=type_document,
                number=number_document,
                defaults={
                    'supplier': supplier,
                    'suppliername': supplier_name,
                    'observation': observation,
                    'dateadd': timezone.now(),
                    'dateproccess': date_purchase,
                    'subtotal': subtotal_with_discount,  # Subtotal con descuento
                    'urljson': relative_file_path,  # Guardar solo la ruta relativa en la base de datos
                    'urlimg': url_img,
                    'status': 0,  # Estado predeterminado
                }
            )

            # Devolver la ruta del archivo creada y un mensaje de éxito
            return JsonResponse({
                'message': 'Archivo JSON procesado correctamente',
                'urlJson': relative_file_path,
                'subtotalWithoutDiscount': subtotal_without_discount,
                'subtotalWithDiscount': subtotal_with_discount,
                'iva': iva_amount,
                'subtotalBruto': subtotal_bruto,
                'purchaseId': purchase.id,
                'action': 'created' if created else 'updated'  # Indicar si se creó o actualizó
            }, status=201)

        except Exception as e:
            print("Error:", e)
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


def get_products(request):
    query = request.GET.get('q', '')
    page_number = request.GET.get('page', 1)
    page_size = 10  # Número de productos por página (ajústalo según tu necesidad)

    # Filtrar productos según la búsqueda por SKU o nombre
    products = Products.objects.filter(
        Q(sku__icontains=query) | Q(nameproduct__icontains=query)
    ).values('id', 'sku', 'nameproduct', 'brands', 'codebar', 'lastprice','iderp','lastcost')

    # Crear paginador
    paginator = Paginator(products, page_size)

    # Obtener la página de productos solicitada
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        return JsonResponse({'error': 'Página vacía.'}, status=404)

    # Convertir los resultados de la página a una lista
    products_list = list(page_obj)

    # Devolver los datos paginados en formato JSON
    response_data = {
        'products': products_list,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'total_products': paginator.count
    }

    return JsonResponse(response_data)

def get_line_document(request):
    products = Products.objects.all().values('idproduct', 'sku', 'nameproduct', 'lastcost', 'currentstock', 'codebar')
    data = {'data': list(products)}
    return JsonResponse(data)

@csrf_exempt
def add_purchase(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Obtener los datos del formulario de la recepción
        supplier = data.get('headers').get('proveedor')
        type_document = data.get('headers').get('tipoDocumento')
        n_document = data.get('headers').get('numeroDocumento')
        subtotal = data.get('headers').get('subtotal')
        observation = data.get('headers').get('observaciones')

        # Crear la compra en la base de datos
        purchase = Purchase.objects.create(
            supplier=supplier,
            typedoc=type_document,
            number=n_document,
            subtotal=subtotal,
            observation=observation,
        )

        # Guardar los productos asociados
        details = data.get('details')
        for detail in details:
            product = Products.objects.get(sku=detail['sku'])
            # Realizar las acciones necesarias con los productos...

        return JsonResponse({'message': 'Documento guardado con éxito'}, status=201)
    return JsonResponse({'error': 'Error al guardar documento'}, status=400)

def load_draft(request):
    data = json.loads(request.body)
    supplier = data.get('supplier')
    type_document = data.get('typeDocument')
    n_document = data.get('nDocument')

    try:
        purchase = Purchase.objects.get(supplier=supplier, typedoc=type_document, number=n_document)
        details = []  # Puedes agregar detalles del documento si es necesario

        data = {
            'headers': {
                'supplier': purchase.supplier,
                'supplierName': purchase.suppliername,
                'typeDocument': purchase.typedoc,
                'nDocument': purchase.number,
                'subtotal': purchase.subtotal,
                'datePurchase': purchase.dateadd,
                'dateExpired': purchase.dateproccess,
                'observation': purchase.observation,
                'typePay': "No Pagado",  # Si tienes el campo en la BD
                'nCheque': 0,  # Ajusta esto según tu modelo
                'qtyCheque': 0,  # Ajusta esto según tu modelo
            },
            'details': details
        }

        return JsonResponse({'resp': 1, 'data': data})
    except Purchase.DoesNotExist:
        return JsonResponse({'resp': 0, 'message': 'No existe borrador'}, status=404)
    
@csrf_exempt
def load_xml(request):
    data = json.loads(request.body)
    supplier = data.get('supplier')
    n_document = data.get('nDocument')

    # Simulación de la respuesta (ajusta según la lógica de tu aplicación)
    response_data = {
        'emissionDate': '2024-01-01',  # Ejemplo de datos simulados
        'expiredDate': '2024-01-15',
        'totalNetoDoc': 100000,
        'globalDcto': 5,
        'details': [
            {'sku': 'PROD1', 'model': 'Modelo A', 'cantidad': 10, 'costo': 10000, 'descuento': 5},
            {'sku': 'PROD2', 'model': 'Modelo B', 'cantidad': 5, 'costo': 20000, 'descuento': 10}
        ]
    }

    return JsonResponse(response_data)

def get_product_by_sku(request):
    sku = request.GET.get('sku')
    product = Products.objects.filter(sku=sku).values('sku', 'nameproduct', 'brands', 'codebar', 'lastprice').first()

    if product:
        return JsonResponse(product)
    else:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    
def get_document_lines(request, document_id):
    """
    API para obtener las líneas de un documento (factura, compra, etc.)
    """
    # Obtén el documento (por ejemplo, una compra)
    document = get_object_or_404(Purchase, id=document_id)
    
    # Recoge los datos de las líneas del documento
    # Supongamos que en 'document' tienes una relación con 'Products'
    # y puedes obtener los productos asociados a este documento
    lines = []
    for product in document.products.all():
        # Agrega cada línea con la información que necesitas
        lines.append({
            'item': product.id,
            'model': product.nameproduct,
            'sku': product.sku,
            'qty': product.currentstock,  # Puedes ajustar según la lógica de cantidad
            'cost': product.lastcost,     # Ajustar el costo según la lógica de tu negocio
            'codeBar': product.codebar,
            'dcto': 0,                    # Ajusta o calcula el descuento
            'subtotal': product.lastcost * product.currentstock,  # Subtotal basado en cantidad x costo
            'delivery': 'Pendiente',      # Ejemplo, podrías ajustar según lo necesario
            'check': False                # Ejemplo de estado o verificación
        })

    # Devuelve los datos en formato JSON
    return JsonResponse({'data': lines})

@csrf_exempt
def save_document_lines(request):
    """
    API para guardar las líneas de un documento (factura, compra, etc.)
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        supplier_id = data['headers']['supplier']
        document_type = data['headers']['typeDocument']
        document_number = data['headers']['nDocument']
        subtotal = data['headers']['subtotal']
        # Otros datos necesarios...

        # Crear o actualizar el documento (por ejemplo, una compra)
        supplier = get_object_or_404(Supplier, id=supplier_id)
        purchase = Purchase.objects.create(
            supplier=supplier,
            typedoc=document_type,
            number=document_number,
            subtotal=subtotal,
            # Otros campos necesarios...
        )

        # Guardar cada línea del documento
        for detail in data['details']:
            product = get_object_or_404(Products, sku=detail['sku'])
            # Crea la línea de producto dentro del documento
            # Si tienes un modelo específico para las líneas, puedes crearlo aquí
            purchase.products.add(product)
            # Aquí puedes manejar los detalles adicionales como cantidad, descuentos, etc.

        return JsonResponse({'message': 'Documento guardado con éxito'}, status=201)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


""" SECTORIZAR PRODUCTOS """

def consultar_productos_sector(request):
    sector = request.GET.get('sector')

    if not sector:
        return JsonResponse({'error': 'El parámetro sector es obligatorio.'}, status=400)

    # Extraer partes del sector como "B-1-G1-1"
    partes = sector.split('-')
    if len(partes) < 4:
        return JsonResponse({'error': 'Formato de sector inválido. Debe ser B-1-G1-1.'}, status=400)

    # Suponiendo que la segunda parte del sector es el ID de la bodega
    id_bodega = partes[1]
    zona = partes[2]
    piso_seccion = partes[3]

    # Buscar productos en esa bodega y sector específico
    productos = Uniqueproducts.objects.filter(
        locationname__icontains=f'{zona}-{piso_seccion}',
        idoffice=id_bodega  # Relación con el campo idoffice
    )

    # Serializar los productos en formato JSON
    productos_data = [{
        'superid': producto.superid,
        'sku': producto.sku,
        'nombre': producto.nameproduct,
        'marca': producto.brand,
        'cantidad': producto.quantity
    } for producto in productos]

    return JsonResponse({'productos': productos_data}, safe=False)


def buscar_productos_por_sector(request):
    sector_query = request.GET.get('sector', '')

    # Validar el formato del sector
    if not sector_query:
        return JsonResponse({'error': 'Debe ingresar un sector válido.'}, status=400)

    try:
        # Dividimos el sector ingresado en zona, piso y sección
        zone, floor_section = sector_query[0], sector_query[1:]
        floor, section = floor_section.split('-')

        # Buscar el sector en la tabla Sectoroffice
        sector = Sectoroffice.objects.filter(zone=zone, floor=floor, section=section)

        if not sector.exists():
            return JsonResponse({'error': 'Sector no encontrado.'}, status=404)

        sector = sector.first()  # Tomamos el primer sector encontrado.

        # Obtener la bodega asociada al sector
        bodega = Bodega.objects.get(idoffice=sector.idoffice)

        # Obtener los productos asociados al sector
        productos = Products.objects.filter(unique_products__location=sector.idsectoroffice)

        # Preparar los datos de respuesta
        productos_data = [{
            'id': producto.id,
            'sku': producto.sku,
            'name': producto.nameproduct,  # Cambiado a nameproduct
            'locationname': sector.namesector,
            'bodega': bodega.name  # Incluimos el nombre de la bodega
        } for producto in productos]

        return JsonResponse({'productos': productos_data})
    
    except Sectoroffice.DoesNotExist:
        return JsonResponse({'error': 'Sector no encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
   

@csrf_exempt
def search_products_by_sector(request):
    if request.method == 'POST':
        # Parsear el cuerpo JSON
        try:
            body = json.loads(request.body)
            term = body.get('searchTerm', '').strip()
        except json.JSONDecodeError:
            return JsonResponse({'resp': 3, 'msg': 'Error al decodificar JSON'})

        print(f"Término de búsqueda recibido: '{term}'")

        # Reemplazar ' por - en el término de búsqueda
        term = term.replace("'", "-")
        print(f"Término de búsqueda modificado: '{term}'")

        # Verificar si el término tiene el formato correcto, comenzando con 'B-'
        if term.startswith('B-'):
            parts = term.split('-')
            if len(parts) == 4:
                # Extraer id_office y name_sector a partir del término
                id_office = parts[1]
                name_sector = parts[2] + '-' + parts[3]
                
                print(f"Office ID: {id_office}, Sector Name: {name_sector}")

                # Buscar el sector en la base de datos
                sector = Sectoroffice.objects.filter(namesector=name_sector, idoffice=id_office).first()

                if sector:
                    print(f"Sector encontrado: {sector.namesector} con id {sector.idsectoroffice}")

                    # Buscar productos en Uniqueproducts asociados al sector encontrado, ordenados por ID inverso
                    productos = Uniqueproducts.objects.filter(location=sector.idsectoroffice).order_by('-id')  # Orden descendente
                    productos_data = []

                    for producto in productos:
                        # Acceder al producto relacionado, manejar errores si no existe
                        producto_data = {
                            'superid': producto.superid,
                            'sku': producto.product.sku if producto.product else "N/A",
                            'name': producto.product.nameproduct if producto.product else "N/A"
                        }
                        productos_data.append(producto_data)

                    # Generar la respuesta
                    response_data = {
                        'resp': 1,
                        'msg': 'Sector seleccionado',
                        'idSector': sector.idsectoroffice,
                        'cantProd': len(productos_data),
                        'terminoScaneado': term,
                        'nameSector': sector.namesector,
                        'productos': productos_data
                    }
                    return JsonResponse(response_data)
                else:
                    # Sector no encontrado
                    print(f"Sector '{name_sector}' no encontrado en oficina '{id_office}'")
                    return JsonResponse({'resp': 3, 'msg': f'Sector "{name_sector}" no encontrado en oficina "{id_office}"'})
            else:
                print(f"Formato de término incorrecto, partes encontradas: {parts}")
                return JsonResponse({'resp': 3, 'msg': 'Formato de término de búsqueda incorrecto.'})
        else:
            print(f"El término no contiene 'B-': {term}")
            return JsonResponse({'resp': 3, 'msg': 'El término de búsqueda no contiene el formato esperado.'})

    # Responder si el método no es POST
    return JsonResponse({'resp': 3, 'msg': 'Método no permitido'})

# @csrf_exempt
# def add_product_to_sector(request):
#     if request.method == 'POST':
#         try:
#             # Decodificar JSON
#             body = json.loads(request.body)
#             productos = body.get('productos', [])
#             sector_name = body.get('sector', '').strip()
#         except json.JSONDecodeError:
#             return JsonResponse({'resp': 3, 'msg': 'Error al decodificar JSON.'}, status=400)

#         # Validar datos
#         if not productos or not sector_name:
#             return JsonResponse({'resp': 3, 'msg': 'El Super ID del producto y el sector son obligatorios.'}, status=400)
#         if not sector_name.startswith('B-') or sector_name.count('-') != 3:
#             return JsonResponse({'resp': 3, 'msg': 'Formato de sector incorrecto.'}, status=400)

#         # Dividir sector_name
#         try:
#             _, id_office, zone_floor, section = sector_name.split('-')
#             name_sector = f'{zone_floor}-{section}'
#         except ValueError:
#             return JsonResponse({'resp': 3, 'msg': 'Formato de sector incorrecto.'}, status=400)

#         # Buscar el sector
#         sector = Sectoroffice.objects.filter(namesector=name_sector, idoffice=id_office).only('idsectoroffice').first()
#         if not sector:
#             return JsonResponse({'resp': 3, 'msg': f'Sector "{name_sector}" no encontrado.'}, status=404)

#         # Procesar productos
#         superids = [producto.get('superid') for producto in productos if producto.get('superid')]
#         if not superids:
#             return JsonResponse({'resp': 3, 'msg': 'No se proporcionaron Super IDs válidos.'}, status=400)

#         # Buscar productos en bloque
#         productos_encontrados = Uniqueproducts.objects.filter(superid__in=superids).only('superid', 'location', 'id')
#         encontrados_ids = set(productos_encontrados.values_list('superid', flat=True))
#         no_encontrados = list(set(superids) - encontrados_ids)

#         # Actualizar productos encontrados en bloque
#         productos_encontrados.update(location=sector.idsectoroffice)

#         # Responder
#         msg = 'Todos los productos fueron añadidos con éxito.'
#         resp_code = 1
#         if no_encontrados:
#             msg = f'Algunos productos no fueron encontrados: {", ".join(no_encontrados)}'
#             resp_code = 2

#         return JsonResponse({
#             'resp': resp_code,
#             'msg': msg,
#             'productos_actualizados': len(encontrados_ids),
#             'productos_no_encontrados': no_encontrados
#         }, status=200)

#     return JsonResponse({'resp': 3, 'msg': 'Método no permitido.'}, status=405)

@csrf_exempt
def add_product_to_sector(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)  # Decodificar el cuerpo JSON
            productos = body.get('productos', [])  # Obtener la lista de productos
            sector_name = body.get('sector', '')  # Obtener el nombre del sector
        except json.JSONDecodeError:
            return JsonResponse({'resp': 3, 'msg': 'Error al decodificar JSON'})

        if not productos or not sector_name:
            return JsonResponse({'resp': 3, 'msg': 'El Super ID del producto y el sector son obligatorios.'})

        if 'B-' in sector_name:
            parts = sector_name.split('-')
            if len(parts) == 4:
                id_office = parts[1]
                name_sector = parts[2] + '-' + parts[3]

                sector = Sectoroffice.objects.filter(namesector=name_sector, idoffice=id_office).first()

                if sector:
                    productos_no_encontrados = []
                    productos_actualizados = 0

                    for producto_data in productos:
                        superid = producto_data.get('superid', '')
                        if superid:
                            producto = Uniqueproducts.objects.filter(superid=superid).first()

                            if producto:
                                producto.location = sector.idsectoroffice
                                producto.save()
                                productos_actualizados += 1
                            else:
                                productos_no_encontrados.append(superid)
                        else:
                            productos_no_encontrados.append(superid)

                    if productos_no_encontrados:
                        return JsonResponse({
                            'resp': 2,
                            'msg': f'Algunos productos no fueron encontrados: {", ".join(productos_no_encontrados)}',
                            'productos_actualizados': productos_actualizados,
                            'sector': sector.namesector
                        })
                    else:
                        return JsonResponse({
                            'resp': 1,
                            'msg': 'Todos los productos fueron añadidos con éxito.',
                            'productos_actualizados': productos_actualizados,
                            'sector': sector.namesector
                        })
                else:
                    return JsonResponse({'resp': 3, 'msg': f'Sector "{name_sector}" no encontrado.'})
            else:
                return JsonResponse({'resp': 3, 'msg': 'Formato de sector incorrecto.'})
        else:
            return JsonResponse({'resp': 3, 'msg': 'El formato del sector no es válido.'})

    return JsonResponse({'resp': 3, 'msg': 'Método no permitido.'})


@csrf_exempt
def buscar_producto_superid(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            superid = body.get('superid', '')
            sector_origen = body.get('sector_origen', '')
        except json.JSONDecodeError:
            return JsonResponse({'resp': 3, 'msg': 'Error al decodificar JSON'})

        if not superid or not sector_origen:
            return JsonResponse({'resp': 3, 'msg': 'Debe proporcionar el Super ID y el sector de origen.'})

        # Verificar que el producto exista en el sector de origen
        parts_origen = sector_origen.split('-')
        if len(parts_origen) == 4:
            id_office = parts_origen[1]
            name_sector = parts_origen[2] + '-' + parts_origen[3]

            sector = Sectoroffice.objects.filter(namesector=name_sector, idoffice=id_office).first()
            if sector:
                producto = Uniqueproducts.objects.filter(superid=superid, location=sector.idsectoroffice).first()
                if producto:
                    return JsonResponse({
                        'resp': 1,
                        'producto': {
                            'superid': producto.superid,
                            'sku': producto.product.sku,
                            'name': producto.product.nameproduct
                        }
                    })
                else:
                    return JsonResponse({'resp': 3, 'msg': f'Producto con Super ID "{superid}" no encontrado en el sector de origen.'})
        return JsonResponse({'resp': 3, 'msg': 'Sector de origen no encontrado.'})

    return JsonResponse({'resp': 3, 'msg': 'Método no permitido.'})

@csrf_exempt
def move_products_to_sector(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            superids = body.get('productos', [])
            sector_destino = body.get('sector_destino', '')
            sector_origen = body.get('sector_origen', '')
        except json.JSONDecodeError:
            return JsonResponse({'resp': 3, 'msg': 'Error al decodificar JSON'})

        if not superids or not sector_destino:
            return JsonResponse({'resp': 3, 'msg': 'Debe proporcionar los productos y el sector de destino.'})

        # Verificar y mover los productos al sector de destino
        parts_destino = sector_destino.split('-')
        parts_origen = sector_origen.split('-')

        if len(parts_destino) == 4 and len(parts_origen) == 4:
            id_office_destino = parts_destino[1]
            name_sector_destino = parts_destino[2] + '-' + parts_destino[3]

            sector_dest = Sectoroffice.objects.filter(namesector=name_sector_destino, idoffice=id_office_destino).first()

            if sector_dest:
                productos_actualizados = []
                for superid in superids:
                    producto = Uniqueproducts.objects.filter(superid=superid).first()
                    if producto:
                        producto.location = sector_dest.idsectoroffice
                        producto.save()
                        productos_actualizados.append(producto.superid)
                
                return JsonResponse({'resp': 1, 'msg': 'Productos movidos con éxito.', 'productos_actualizados': productos_actualizados})
            else:
                return JsonResponse({'resp': 3, 'msg': f'Sector de destino "{name_sector_destino}" no encontrado.'})
        else:
            return JsonResponse({'resp': 3, 'msg': 'Formato de sector incorrecto.'})

    return JsonResponse({'resp': 3, 'msg': 'Método no permitido.'})

@csrf_exempt
def anadir_producto_sector(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            superid = body.get('superid', '')
            sector = body.get('sector', '')
        except json.JSONDecodeError:
            return JsonResponse({'resp': 3, 'msg': 'Error al decodificar JSON'})

        if not superid or not sector:
            return JsonResponse({'resp': 3, 'msg': 'Debe proporcionar el Super ID y el sector.'})

        # Verificar si el sector existe
        parts = sector.split('-')
        if len(parts) == 4:
            id_office = parts[1]
            name_sector = parts[2] + '-' + parts[3]

            sector_obj = Sectoroffice.objects.filter(namesector=name_sector, idoffice=id_office).first()
            if not sector_obj:
                return JsonResponse({'resp': 3, 'msg': 'Sector no encontrado.'})

            # Verificar si el producto con el Super ID existe
            producto = Uniqueproducts.objects.filter(superid=superid).first()
            if not producto:
                return JsonResponse({'resp': 3, 'msg': f'Producto con Super ID "{superid}" no encontrado.'})

            # Asignar el sector al producto
            producto.location = sector_obj.idsectoroffice
            producto.save()

            return JsonResponse({'resp': 1, 'msg': 'Producto añadido con éxito al sector.'})
        else:
            return JsonResponse({'resp': 3, 'msg': 'Formato de sector incorrecto.'})

    return JsonResponse({'resp': 3, 'msg': 'Método no permitido.'})

""" CUADRAR SETORES """
@csrf_exempt
def cuadrar_productos(request):
    """
    API para mover productos no escaneados a la bodega 'Narnia'.
    """
    if request.method == 'POST':
        try:
            # Decodificar el cuerpo JSON
            body = json.loads(request.body)
            superids = body.get('superids', [])  # Lista de superids escaneados
            sector_name = body.get('sector_id', '')  # ID del sector a cuadrar

            if not superids or not sector_name:
                return JsonResponse({'resp': 3, 'msg': 'Super IDs y sector son obligatorios.'})
            
            # Validar sector
            if 'B-' in sector_name:
                parts = sector_name.split('-')
                if len(parts) == 4:
                    id_office = parts[1]
                    name_sector = parts[2] + '-' + parts[3]

                    # Buscar el sector
                    sector = Sectoroffice.objects.filter(namesector=name_sector, idoffice=id_office).first()
                    if not sector:
                        return JsonResponse({'resp': 3, 'msg': f'Sector "{name_sector}" no encontrado.'})

                    # Buscar productos en el sector
                    productos_en_sector = Uniqueproducts.objects.filter(location=sector.idsectoroffice)
                    
                    # Buscar o crear el sector "Narnia"
                    sector_narnia, created = Sectoroffice.objects.get_or_create(
                        idsectoroffice=99999,
                        defaults={
                            'idoffice': 9999,
                            'namesector': 'Narnia',
                            'zone': 'NARN',
                            'floor': 0,
                            'section': 0,
                            'description': 'Sector virtual para productos no escaneados o sin ubicación asignada',
                            'state': 1,
                            'namedescriptive': 'Productos no clasificados (Narnia)'
                        }
                    )
                    
                    productos_movidos = []
                    
                    for producto in productos_en_sector:
                        if producto.superid not in superids:
                            # Mover producto al sector "Narnia"
                            producto.location = sector_narnia.idsectoroffice
                            producto.locationname = sector_narnia.namesector
                            producto.save()
                            productos_movidos.append({
                                'superid': producto.superid,
                                'sku': producto.product.sku if producto.product else None,
                                'name': producto.product.nameproduct if producto.product else None
                            })
                    
                    return JsonResponse({
                        'resp': 1,
                        'msg': 'Productos movidos exitosamente a Narnia.',
                        'productos_movidos': productos_movidos
                    })
                else:
                    return JsonResponse({'resp': 3, 'msg': 'Formato de sector incorrecto.'})
            else:
                return JsonResponse({'resp': 3, 'msg': 'El formato del sector no es válido.'})
        
        except json.JSONDecodeError:
            return JsonResponse({'resp': 3, 'msg': 'Error al decodificar JSON.'})
        except Exception as e:
            return JsonResponse({'resp': 3, 'msg': f'Error inesperado: {str(e)}'})

    return JsonResponse({'resp': 3, 'msg': 'Método no permitido.'})


# Función para obtener el ID del sector "Narnia"
def get_narnia_id():
    narnia_sector = Sectoroffice.objects.filter(namesector='Narnia').first()
    return narnia_sector.idsectoroffice if narnia_sector else None

# Función para enviar el correo con los productos enviados a Narnia
def enviar_correo_a_narnia(productos, sector):
    lista_productos = "\n".join([f"Super ID: {p.superid}, Nombre: {p.product.nameproduct}, SKU: {p.product.sku}" for p in productos])
    fecha_actual = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    
    subject = f"Productos enviados a Narnia desde el sector {sector.namesector}"
    message = f"Fecha: {fecha_actual}\n\nProductos enviados a Narnia:\n\n{lista_productos}"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        #['pfarias@emmett.cl'],  # Cambia por el correo destino
        ['erp@emmett.cl'],
        fail_silently=False,
    )


#Prueba conectar bsale

def obtener_variant_id_por_sku(sku):
    """Función para obtener el variant_id desde Bsale basado en el SKU"""
    url = f"https://api.bsale.cl/v1/variants.json?code={sku}"
    headers = {
        'access_token': BSALE_API_TOKEN,  # Reemplaza con tu token de Bsale
        'Accept': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data['count'] > 0 and len(data['items']) > 0:
            variant_id = data['items'][0]['id']
            return variant_id
        else:
            print(f"No se encontró un variant_id para el SKU {sku} en Bsale.")
            return None
    else:
        print(f"Error al obtener el variant_id. Status code: {response.status_code}")
        return None
    
def sincronizar_sku_con_bsale(sku, variant_id=None):
    print(f"Sincronizando SKU: {sku}")
    
    if variant_id is None:
        variant_id = obtener_variant_id_por_sku(sku)
        print(f"Variant ID obtenido: {variant_id}")
    
    if variant_id is not None:
        stock_local = obtener_stock_local_por_superid(sku)
        print(f"Stock local para {sku}: {stock_local}")
        
        if stock_local is not None:
            respuesta_bsale = actualizar_stock_bsale(variant_id, stock_local)
            print(f"Respuesta de Bsale: {respuesta_bsale}")
            
            if respuesta_bsale:
                print(f"Stock del SKU {sku} actualizado correctamente en Bsale.")
                return True
            else:
                print(f"Error al actualizar el SKU {sku} en Bsale.")
                return False
        else:
            print(f"El SKU {sku} no se encontró en la base de datos local.")
            return False
    else:
        print(f"No se pudo obtener el variant_id para el SKU {sku}.")
        return False
    
@csrf_exempt
def sincronizar_producto_por_sku(request, sku):
    """API para sincronizar el stock local con Bsale para un SKU específico."""
    if request.method == 'POST':
        resultado = sincronizar_sku_con_bsale(sku)
        if resultado:
            return JsonResponse({'status': 'Producto sincronizado correctamente'}, status=200)
        else:
            return JsonResponse({'error': 'No se pudo sincronizar el producto'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
def obtener_stock_local_por_superid(sku):
    """Función para obtener el stock local basado en la suma de los superid relacionados a un SKU"""
    producto = Products.objects.filter(sku=sku).first()

    if producto:
        superid_count = Uniqueproducts.objects.filter(product=producto).count()
        return superid_count
    else:
        print(f"El SKU {sku} no tiene productos únicos asociados.")
        return None
    


BSALE_API_URL = 'https://api.bsale.io/v1'

# Función para obtener el variantId
def obtener_variant_id(sku):
    url = f"{BSALE_API_URL}/stocks.json?code={sku}"
    headers = {
        'access_token': BSALE_API_TOKEN,
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("items"):
            variant_id = data['items'][0]['variant']['id']
            return variant_id
    return None

# Función para obtener el stock de un SKU en Bsale
def obtener_stock_bsale(variant_id):
    url = f"{BSALE_API_URL}/stocks.json?variantid={variant_id}"
    headers = {
        'access_token': BSALE_API_TOKEN,
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Función para actualizar el stock en Bsale
def actualizar_stock_bsale(variant_id, office_id, new_stock, cost):
    url = f"{BSALE_API_URL}/stocks/receptions.json"
    headers = {
        'access_token': BSALE_API_TOKEN,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        "document": "Guía",
        "officeId": office_id,
        "documentNumber": "123",
        "note": "Actualización de stock",
        "details": [
            {
                "quantity": new_stock,
                "variantId": variant_id,
                "cost": cost
            }
        ]
    }
    
    print(f"Enviando a Bsale: {data}")  # Para depuración
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("Stock actualizado exitosamente en Bsale.")
        return response.json()
    else:
        print(f"Error al actualizar stock en Bsale. Status code: {response.status_code}")
        print(f"Response content: {response.content}")
        return None
    
def calcular_stock_local(sku):
    """Función que calcula el stock local sumando los productos únicos relacionados al SKU"""
    productos_unicos = Uniqueproducts.objects.filter(product__sku=sku)
    stock_total = productos_unicos.count()
    return stock_total


def obtener_stock_id(variant_id, office_id):
    """Función para obtener el stock_id de una variante y sucursal (office) en Bsale"""
    headers = {
        'access_token': BSALE_API_TOKEN,
        'Accept': 'application/json'
    }
    # Filtrar por variant_id y office_id
    url = f"{BSALE_API_URL}/stocks.json?variantid={variant_id}&officeid={office_id}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            # Devolver el primer stock_id encontrado
            return data['items'][0]['id']
    return None


# Función en Django para manejar la sincronización de un SKU específico
@csrf_exempt
def sincronizar_producto(request, sku):
    if request.method == 'POST':
        try:
            # Obtener el producto local
            producto_local = Products.objects.get(sku=sku)
            
            # Calcular el stock local
            stock_local = calcular_stock_local(sku)
            print(f"Stock local para {sku}: {stock_local}")
            
            # Obtener el variant_id del producto local
            variant_id = producto_local.iderp
            print(f"Variant ID obtenido: {variant_id}")

            # Definir la office_id con la que trabajas, suponiendo que sea '1'
            office_id = 1

            # Obtener el stock_id de Bsale
            stock_id = obtener_stock_id(variant_id, office_id)

            if stock_id:
                # Si encontramos el stock_id, procedemos a actualizar el stock
                data = {
                    'quantity': stock_local  # Usar el stock local calculado
                }
                headers = {
                    'access_token': BSALE_API_TOKEN,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
                url = f"{BSALE_API_URL}/stocks/{stock_id}.json"
                
                # Hacer la solicitud PUT a la API de Bsale para actualizar el stock
                response = requests.put(url, json=data, headers=headers)
                
                if response.status_code == 200:
                    return JsonResponse({'resp': 1, 'msg': f'Stock del SKU {sku} actualizado en Bsale con éxito.'})
                else:
                    print(f"Error al actualizar stock en Bsale. Status code: {response.status_code}")
                    print(f"Respuesta de Bsale: {response.text}")
                    return JsonResponse({'resp': 3, 'msg': f'Error al actualizar el SKU {sku} en Bsale.'}, status=400)
            else:
                print("No se encontró el stock_id en Bsale.")
                return JsonResponse({'resp': 3, 'msg': 'No se encontró el stock_id en Bsale.'}, status=404)
        
        except Products.DoesNotExist:
            return JsonResponse({'resp': 3, 'msg': f'Producto con SKU {sku} no encontrado.'}, status=404)

    return JsonResponse({'resp': 3, 'msg': 'Método no permitido.'}, status=405)

@csrf_exempt
def registrar_recepcion_stock(request, sku, qty):
    if request.method in ['POST', 'PUT']:
        try:
            producto = Products.objects.get(sku=sku)
            stock_local = qty  # Usamos qty como la cantidad de stock a registrar

            variant_id = producto.iderp
            office_id = 1

            print(f"Variant ID: {variant_id}, Office ID: {office_id}, Stock local: {stock_local}")

            data = {
                "document": "Guía",
                "officeId": office_id,
                "documentNumber": "123",
                "note": "Recepción de stock vía API",
                "details": [
                    {
                        "quantity": stock_local,
                        "variantId": variant_id,
                        "cost": producto.lastcost
                    }
                ]
            }

            headers = {
                'access_token': BSALE_API_TOKEN,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            url = f"{BSALE_API_URL}/stocks/receptions.json"
            response = requests.post(url, json=data, headers=headers)

            if response.status_code in [200, 201]:
                return JsonResponse({'resp': 1, 'msg': f'Stock del SKU {sku} registrado en Bsale con éxito.'})
            else:
                return JsonResponse({
                    'resp': 3,
                    'msg': f'Error al registrar recepción del SKU {sku} en Bsale.',
                    'detalle_error': response.text
                }, status=response.status_code)

        except Products.DoesNotExist:
            return JsonResponse({'resp': 3, 'msg': f'Producto con SKU {sku} no encontrado.'}, status=404)
        except Exception as e:
            print(f"Error inesperado: {e}")
            return JsonResponse({'resp': 3, 'msg': 'Error inesperado en la recepción de stock.'}, status=500)

    return JsonResponse({'resp': 3, 'msg': 'Método no permitido.'}, status=405)



""" APIS PARA DESPACHO DE PRODUCTOS """

# Funciones Mock (puedes reemplazar por la lógica real)
def get_unique_document_bll(type, number):
    # Lógica para obtener los detalles de un documento específico
    # Aquí puedes filtrar según los detalles que necesites.
    
    # Ejemplo para obtener todos los productos (puedes ajustar esto a tu estructura de documentos):
    products = Products.objects.filter(sku=number)  # Filtrando por un SKU como número del documento (ajustar según tus datos)
    
    details = []
    for product in products:
        details.append({
            'code': product.sku,
            'name': product.nameproduct,
            'quantity': 5,  # Asignar cantidad específica según lógica
            'total_unit_value': product.lastprice or 0  # Precio unitario (ajustar lógica si hay más cálculos involucrados)
        })
    
    return details
def get_product_by_sid(sid):
    # Buscar el producto por SID (Super ID) en la tabla de productos únicos
    unique_product = Uniqueproducts.objects.filter(superid=sid).select_related('product').first()
    
    if unique_product:
        return {
            'idERP': unique_product.product.iderp,  # ID de ERP del producto relacionado
            'sku': unique_product.product.sku
        }
    else:
        return {'error': 'Producto no encontrado'}

def dispatch_sid_bll(data):
    try:
        with transaction.atomic():
            # Obtener el producto único por su SID
            unique_product = Uniqueproducts.objects.filter(superid=data['sid']).first()
            
            if not unique_product:
                return {'error': 'Producto no encontrado'}
            
            # Verificar y actualizar stock
            if unique_product.state == 1:  # Ejemplo de verificación de estado
                return {'error': 'Producto ya descontado'}
            
            # Simula la lógica para "descontar" el producto
            unique_product.state = 1  # Actualizar el estado del producto como descontado
            unique_product.save()
            
            return {'rows': 1}  # Devolver la cantidad de productos actualizados
    except Exception as e:
        return {'error': str(e)}

def post_consumption_bll(data):
    # Simulación de actualización en Bsale o sistemas externos
    return {'error': ''}

def get_pass_consumption_bll():
    return {'passConsumption': 'mypassword'}

# API Endpoints
@csrf_exempt
def current_dispatch(request):
    if request.method == "GET":
        dispatches = list(Dispatch.objects.values())
        return JsonResponse({'data': dispatches})

@csrf_exempt
def details_document(request):
    if request.method == "POST":
        data = json.loads(request.body)
        type = data.get('type')
        number = data.get('number')
        details = get_unique_document_bll(type, number)
        formatted_details = format_table(details)
        request.session['currentDispatch'] = formatted_details
        return JsonResponse({'data': formatted_details})

def format_table(details):
    formatted = []
    for item in details:
        formatted.append({
            'quantity': item['quantity'],
            'code': item['code'],
            'description': item['description'],
            'total_unit_value': item['total_unit_value'],
            'count': 0
        })
    return formatted

@csrf_exempt
def dispatch_consumption(request):
    if request.method == "POST":
        try:
            # Obtener los datos del request
            data = json.loads(request.body)
            n_document = data.get('nDocument', 0)
            type_document = data.get('typeDocument')
            company = data.get('company')
            products = data.get('products', [])

            # Verificar o crear el sector "Despachados"
            sector_despachados, created = Sectoroffice.objects.get_or_create(
                zone="DESP",
                defaults={
                    'idoffice': 0,
                    'iduserresponsible': 0,
                    'floor': 0,
                    'section': 0,
                    'namesector': "Despachados",
                    'state': 1
                }
            )
            print(f"Sector 'Despachados' idsectoroffice: {sector_despachados.idsectoroffice}")

            # Iniciar una transacción atómica
            with transaction.atomic():
                for product in products:
                    superid = product.get('superid')
                    cantidad = int(product.get('quantity', 1))

                    # Verificar si el superid existe en Uniqueproducts con estado 0
                    unique_product = Uniqueproducts.objects.select_related('product').filter(superid=superid, state=0).first()

                    if not unique_product:
                        print(f"SuperID {superid} no encontrado o ya despachado.")
                        return JsonResponse({'title': 'SuperID no encontrado o ya despachado', 'icon': 'error'})

                    # Si el location es None, asignarlo al sector "Despachados"
                    if unique_product.location is None:
                        unique_product.location = sector_despachados.idsectoroffice
                        unique_product.save()
                        print(f"Producto con SuperID {superid} asignado a 'Despachados' (Location ID: {sector_despachados.idsectoroffice})")

                    # Obtener el Sectoroffice relacionado usando el location de unique_product
                    sector = Sectoroffice.objects.filter(idsectoroffice=unique_product.location).first()
                    if not sector:
                        print(f"Sector no encontrado para el Location ID {unique_product.location}")
                        return JsonResponse({'title': 'Sector no encontrado para el producto', 'icon': 'error'})

                    product_instance = unique_product.product
                    stock_disponible = Uniqueproducts.objects.filter(product=product_instance, state=0).count()

                    if stock_disponible < cantidad:
                        print(f"Error: Producto {product_instance.sku} no tiene suficiente stock. Stock actual: {stock_disponible}")
                        return JsonResponse({
                            'title': 'Stock insuficiente',
                            'icon': 'error',
                            'message': f'El producto {product_instance.sku} no tiene suficiente stock disponible.'
                        })

                    # Preparar los datos para enviar a Bsale
                    data_bsale = {
                        "note": f"Despacho desde empresa {company}",
                        "officeId": 1,
                        "details": [{"quantity": cantidad, "variantId": product_instance.iderp}]
                    }
                    print(f"Datos enviados a Bsale: {json.dumps(data_bsale, indent=2)}")

                    headers = {
                        "access_token": BSALE_API_TOKEN,
                        "Content-Type": "application/json"
                    }

                    response = requests.post("https://api.bsale.io/v1/stocks/consumptions.json", headers=headers, json=data_bsale)

                    if response.status_code not in [200, 201]:
                        raise Exception(f"Error en Bsale: {response.status_code} - {response.text}")

                    # Mover el producto al sector "Despachados" y actualizar su estado
                    unique_product.location = sector_despachados.idsectoroffice
                    unique_product.observation = f"Salida: {type_document} | Empresa: {company}"
                    unique_product.typedocout = type_document
                    unique_product.ndocout = n_document
                    unique_product.datelastinventory = timezone.now()
                    unique_product.state = 1
                    unique_product.ncompany = company
                    unique_product.save()

                    print(f"Producto {unique_product.superid} despachado y movido al sector 'Despachados'.")

            return JsonResponse({'title': 'Productos despachados con éxito', 'icon': 'success'})

        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return JsonResponse({'title': 'Error en el despacho', 'icon': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'title': 'Método no permitido', 'icon': 'error'}, status=405)
#BSALE_API_TOKEN = "1b7908fa44b56ba04a3459db5bb6e9b12bb9fadc"  # Coloca tu token de autenticación


@csrf_exempt
def get_unique_document(request):
    type_document = request.GET.get('type')
    number = request.GET.get('number')

    if not type_document or not number:
        print("Error: Faltan parámetros de tipo de documento o número")
        return JsonResponse({'error': 'Faltan parámetros de tipo de documento o número'}, status=400)

    # Construir la URL inicial para obtener el ID del documento
    url_costs = f"{BSALE_API_URL}/documents/costs.json?codesii={type_document}&number={number}"
    headers = {
        'access_token': BSALE_API_TOKEN,
        'Content-Type': 'application/json'
    }

    print(f"Construyendo URL para obtener ID del documento: {url_costs}")

    try:
        # Realizar la solicitud para obtener la información básica del documento
        response = requests.get(url_costs, headers=headers)
        print(f"Respuesta de la API para obtener ID del documento: {response.status_code} - {response.text}")

        if response.status_code == 401:
            print("Error de autenticación: Verifica tu token o permisos de acceso")
            return JsonResponse({'error': 'Error de autenticación: Verifica tu token o permisos de acceso'}, status=401)

        if response.status_code != 200:
            print(f"Error al obtener el ID del documento: {response.status_code}")
            return JsonResponse({'error': 'Error al obtener el ID del documento'}, status=response.status_code)

        # Obtener el ID del documento desde la respuesta
        info = response.json()
        document_id = info.get('id')
        if not document_id:
            print("Error: No se encontró el ID del documento en la respuesta")
            return JsonResponse({'error': 'No se encontró el ID del documento'}, status=404)

        print(f"ID del documento obtenido: {document_id}")

        # Extraer los detalles de los productos y consultar el nombre en el modelo Products
        products = []
        for detail in info.get('cost_detail', []):
            variant = detail.get('variant', {})
            shipping_detail = detail.get('shipping_detail', {})

            sku = variant.get('code')
            # Consulta el producto por SKU
            product = Products.objects.filter(sku=sku).first()
            name = product.nameproduct if product else "Nombre no encontrado"

            product_data = {
                'code': sku,
                'name': name,
                'description': variant.get('description'),
                'quantity': shipping_detail.get('quantity'),
                'totalAmount': shipping_detail.get('variantTotalCost')
            }
            print(f"Producto procesado: {product_data}")
            products.append(product_data)

        print("Devolviendo la información de los productos correctamente")
        return JsonResponse(products, safe=False)

    except requests.RequestException as e:
        print(f"Error en la comunicación con la API: {str(e)}")
        return JsonResponse({'error': 'Error en la comunicación con la API', 'details': str(e)}, status=500)
    
@csrf_exempt
def validate_superid(request):
    if request.method == "POST":
        try:
            # Intenta decodificar el cuerpo de la solicitud como JSON
            data = json.loads(request.body.decode('utf-8'))
            superid = data.get('superid')

            if not superid:
                return JsonResponse({"error": "Missing superid"}, status=400)

            # Buscar el superid en la tabla Uniqueproducts
            unique_product = Uniqueproducts.objects.filter(superid=superid).first()

            if not unique_product:
                return JsonResponse({"error": "Superid not found"}, status=404)

            # Verificar que el producto asociado al superid tenga un SKU válido
            associated_product = unique_product.product  # Relación ForeignKey con Products

            if not associated_product or not associated_product.sku:
                return JsonResponse({"error": "No SKU associated with this superid"}, status=404)

            # Respuesta exitosa con los datos necesarios
            return JsonResponse({
                "message": "Superid validated successfully",
                "superid": superid,
                "sku": associated_product.sku,
                "description": associated_product.nameproduct,
                "quantity": unique_product.correlative
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST method is allowed"}, status=405)


@csrf_exempt
def validate_superid_simplified(request):
    if request.method == "POST":
        try:
            # Obtener los datos desde la solicitud JSON
            body = json.loads(request.body)
            sid = body.get('sid')
            document_products = body.get('document_products', [])

            # Imprimir los datos recibidos para depuración
            print(f"SuperID recibido: {sid}")
            print(f"Productos recibidos del documento (SKUs): {document_products}")

            # Verificar si el `superid` existe en `Uniqueproducts`
            unique_product = Uniqueproducts.objects.select_related('product').filter(superid=sid).first()

            if not unique_product:
                print("SuperID no encontrado en la base de datos.")
                return JsonResponse({'error': 'SuperID no encontrado'}, status=404)

            # Imprimir los datos completos del registro encontrado
            print(f"Datos del Uniqueproduct encontrado: {unique_product.__dict__}")

            # Verificar si el producto asociado existe y tiene un SKU
            associated_sku = unique_product.product.sku if unique_product.product else None
            print(f"Producto asociado: {unique_product.product}")
            print(f"SKU asociado encontrado: {associated_sku}")

            if not associated_sku:
                print("Producto asociado no tiene un SKU válido.")
                return JsonResponse({'error': 'Producto asociado no tiene un SKU válido'}, status=400)

            # Si `document_products` está vacío, tratarlo como "Consumo Interno"
            if not document_products:
                print("No se proporcionaron productos del documento. Considerando como Consumo Interno.")
                return JsonResponse({
                    'row': 1,
                    'title': 'SuperID validado para Consumo Interno',
                    'icon': 'success',
                    'sku': associated_sku
                })

            # Validación para despacho normal: verificar si el SKU está en `document_products`
            if associated_sku not in document_products:
                print("El SKU asociado no coincide con los productos del documento.")
                return JsonResponse({'error': 'El SKU asociado no coincide con los productos del documento'}, status=400)

            # Respuesta exitosa para despacho normal
            return JsonResponse({
                'row': 1,
                'title': 'SuperID y SKU validados correctamente',
                'icon': 'success',
                'sku': associated_sku
            })

        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return JsonResponse({'error': 'Error inesperado en la operación'}, status=500)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


"""Imprimir Etiquetas"""
from reportlab.lib.utils import ImageReader
from datetime import date

@csrf_exempt
def imprimir_etiqueta_qr(request):
    if request.method == 'POST':
        # Obtener los datos enviados desde el front-end
        sku = request.POST.get('sku')
        number = request.POST.get('number')
        model = request.POST.get('model')
        qty = int(request.POST.get('qty', 1))
        codebar = request.POST.get('codebar', '')
        url_json = request.POST.get('urlJson')  # Ruta del archivo JSON

        if not sku or qty <= 0 or not url_json:
            return JsonResponse({'error': 'Datos inválidos para generar la etiqueta.'}, status=400)

        try:
            producto = Products.objects.get(sku=sku)
        except Products.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado.'}, status=404)

        pdf_filename = f'etiqueta_{sku}.pdf'
        relative_file_path = os.path.join('models', 'etiquetas', pdf_filename)
        absolute_file_path = os.path.join(settings.MEDIA_ROOT, relative_file_path)
        os.makedirs(os.path.dirname(absolute_file_path), exist_ok=True)

        last_unique_product = Uniqueproducts.objects.filter(product=producto).order_by('-correlative').first()
        current_correlative = (last_unique_product.correlative if last_unique_product else 0) + 1
        base_numeric_sku = ''.join(filter(str.isdigit, sku))  # Extraer números del SKU
        if not base_numeric_sku:
            return JsonResponse({'error': 'El SKU no contiene números válidos.'}, status=400)

        base_superid = f"{base_numeric_sku}e"

        page_width, page_height = 102 * mm, 50 * mm
        pdf = canvas.Canvas(absolute_file_path, pagesize=(page_width, page_height))

        super_ids = []
        for i in range(qty):
            super_id = f"{base_superid}{str(current_correlative).zfill(2)}"
            super_ids.append(super_id)

            is_left = i % 2 == 0
            x_offset = 3 * mm if is_left else 56 * mm

            # QR Code
            x_qr, y_qr = x_offset, 25 * mm
            x_bar = x_offset, 25 * mm

            qr_width, qr_height = 22 * mm, 22 * mm

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=5,
                border=0,  # Sin borde blanco
            )
            qr.add_data(super_id)
            qr.make(fit=True)

            qr_img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            qr_img.save(buffer, format="PNG")
            buffer.seek(0)

            qr_image = ImageReader(buffer)
            pdf.drawImage(qr_image, x_qr, y_qr, width=qr_width, height=qr_height)

            # SKU
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(x_qr + qr_width + 4 * mm, y_qr + 30, f"{sku}")

            # Etiqueta contador
            pdf.drawString(x_qr + qr_width + 4 * mm, y_qr + 20, f"{i + 1} de {qty}")

            # Fecha
            pdf.drawString(x_qr + qr_width + 4 * mm, y_qr + 10, f"{date.today().strftime('%d-%m-%Y')}")

            # Nombre del producto
            y_product_text = y_qr - 15
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(x_qr, y_product_text, f"{producto.nameproduct}")
            # Código de barras
            x_barcode = x_qr - 6 * mm  # Mover a la derecha o ajustar como desees
            y_barcode = y_qr - 50 # Ajustar a la misma altura del QR
            barcode_sku = code128.Code128(sku, barWidth=0.38 * mm, barHeight=9 * mm)
            barcode_sku.drawOn(pdf, x_barcode, y_barcode)
           

            # SuperID y número de documento
            y_super_id = y_barcode + 30
            pdf.setFont("Helvetica-Bold",10)
            pdf.drawString(x_qr, y_super_id - 3, f"{super_id}")
            pdf.drawString(x_qr + 25 * mm, y_super_id -3 , f"{number}")

            # Guardar el nuevo UniqueProduct
            Uniqueproducts.objects.create(
                product=producto,
                superid=super_id,
                correlative=current_correlative,
                state=0,
                cost=producto.lastcost,
                locationname="Almacen",
                observation="Etiqueta generada automáticamente",
                printlabel=os.path.join(settings.MEDIA_URL, relative_file_path),  # Guardar URL en printlabel
                iddocumentincome=number,
                dateadd=date.today()
            )

            # Incrementar el correlativo
            current_correlative += 1

            if not is_left and i < qty - 1:
                pdf.showPage()

        pdf.save()

        # Actualizar el stock en Bsale
        office_id = 1  # ID de la oficina en Bsale, cámbialo según sea necesario
        variant_id = producto.iderp  # Supongamos que el ID del producto es el mismo que la variante en Bsale
        cost = producto.lastcost
        print(variant_id, office_id, qty,cost,"DATOS PARA BSALE")
        bsale_response = actualizar_stock_bsale(variant_id, office_id, qty,cost)

        if not bsale_response:
            return JsonResponse({'error': 'Etiqueta creada, pero no se pudo actualizar stock en Bsale.'}, status=500)


        try:
            with open(url_json, 'r+') as json_file:
                data = json.load(json_file)
                for detail in data.get('details', []):
                    if detail.get('sku') == sku:
                        detail['printed'] = True
                json_file.seek(0)
                json.dump(data, json_file, indent=4)
                json_file.truncate()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return JsonResponse({'error': f'Error al procesar el archivo JSON: {str(e)}'}, status=400)

        try:
            factura = Purchase.objects.get(urljson=url_json)
            if all(detail.get('printed') for detail in data.get('details', [])):
                factura.status = 3
                factura.save()
        except Purchase.DoesNotExist:
            pass

        pdf_url = os.path.join(settings.MEDIA_URL, relative_file_path)
        return JsonResponse({
            'urlPdf': pdf_url,
            'superids': super_ids,
            'sku': sku
        })

    return JsonResponse({'error': 'Método no permitido.'}, status=405)






@csrf_exempt
def imprimir_etiqueta(request):
    if request.method == 'POST':
        # Obtener los datos enviados desde el front-end
        sku = request.POST.get('sku')
        model = request.POST.get('model')
        qty = int(request.POST.get('qty', 1))
        codebar = request.POST.get('codebar', '')
        url_json = request.POST.get('urlJson')  # Ruta del archivo JSON

        # Validaciones iniciales
        if not sku or qty <= 0 or not url_json:
            return JsonResponse({'error': 'Datos inválidos para generar la etiqueta.'}, status=400)
        
        # Obtener el producto correspondiente del modelo Products
        try:
            producto = Products.objects.get(sku=sku)
        except Products.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado.'}, status=404)

        # Crear el nombre y la ruta del archivo PDF
        pdf_filename = f'etiqueta_{sku}.pdf'
        relative_file_path = os.path.join('models', 'etiquetas', pdf_filename)
        absolute_file_path = os.path.join(settings.MEDIA_ROOT, relative_file_path)
        os.makedirs(os.path.dirname(absolute_file_path), exist_ok=True)

        # Obtener el último correlativo y SuperID para el producto
        last_unique_product = Uniqueproducts.objects.filter(product=producto).order_by('-correlative').first()
        current_correlative = (last_unique_product.correlative if last_unique_product else 0) + 1
        base_numeric_sku = ''.join(filter(str.isdigit, sku))  # Extraer números del SKU
        if not base_numeric_sku:
            return JsonResponse({'error': 'El SKU no contiene números válidos.'}, status=400)

        base_superid = f"{base_numeric_sku}e"

        # Crear el PDF con tamaño 10.2 cm x 5 cm
        page_width, page_height = 102 * mm, 50 * mm
        pdf = canvas.Canvas(absolute_file_path, pagesize=(page_width, page_height))

        super_ids = []
        for i in range(qty):
            # Generar SuperID
            super_id = f"{base_superid}{str(current_correlative).zfill(2)}"
            super_ids.append(super_id)

            # Parte izquierda de la etiqueta (SKU y código de barras horizontal)
            x_sku_left, y_sku_left = 5 * mm, 35 * mm
            barcode_sku_left = code128.Code128(sku, barWidth=0.3 * mm, barHeight=9 * mm)
            barcode_sku_left.drawOn(pdf, x_sku_left, y_sku_left)
            pdf.setFont("Helvetica", 6)
            pdf.drawString(x_sku_left + 20, y_sku_left - 10, f"SKU: {sku}")

            # SuperID en vertical (rotado)
            pdf.saveState()
            pdf.rotate(90)
            x_superid_rotated_left, y_superid_rotated_left = 10 * mm, -2 * mm
            barcode_superid_left = code128.Code128(super_id, barWidth=0.4 * mm, barHeight=9 * mm)
            barcode_superid_left.drawOn(pdf, y_superid_rotated_left, -x_superid_rotated_left)
            pdf.setFont("Helvetica", 6)
            pdf.drawString(y_superid_rotated_left + 15, -x_superid_rotated_left - 15, f"SuperID: {super_id}")
            pdf.restoreState()

            # Parte derecha de la etiqueta (si se requiere más de un elemento por página)
            if i % 2 == 1:
                x_sku_right, y_sku_right = 60 * mm, 35 * mm
                barcode_sku_right = code128.Code128(sku, barWidth=0.3 * mm, barHeight=9 * mm)
                barcode_sku_right.drawOn(pdf, x_sku_right, y_sku_right)
                pdf.setFont("Helvetica", 6)
                pdf.drawString(x_sku_right + 20, y_sku_right - 10, f"SKU: {sku}")

                pdf.saveState()
                pdf.rotate(90)
                x_superid_rotated_right, y_superid_rotated_right = 65 * mm, -2 * mm
                barcode_superid_right = code128.Code128(super_id, barWidth=0.4 * mm, barHeight=9 * mm)
                barcode_superid_right.drawOn(pdf, y_superid_rotated_right, -x_superid_rotated_right)
                pdf.setFont("Helvetica", 6)
                pdf.drawString(y_superid_rotated_right + 15, -x_superid_rotated_right - 15, f"SuperID: {super_id}")
                pdf.restoreState()

            # Guardar el nuevo UniqueProduct
            Uniqueproducts.objects.create(
                product=producto,
                superid=super_id,
                correlative=current_correlative,
                state=0,
                cost=producto.lastcost,
                locationname="Almacen",
                observation="Etiqueta generada automáticamente",
                printlabel=os.path.join(settings.MEDIA_URL, relative_file_path)  # Guardar URL en printlabel
            )

            # Incrementar el correlativo
            current_correlative += 1

            # Añadir una nueva página si es necesario
            if i % 2 == 1 and i < qty - 1:
                pdf.showPage()

        pdf.save()

        # Actualizar el stock en Bsale
        office_id = 1  # ID de la oficina en Bsale, cámbialo según sea necesario
        variant_id = producto.iderp  # Supongamos que el ID del producto es el mismo que la variante en Bsale
        cost = producto.lastcost
        print(variant_id, office_id, qty,cost,"DATOS PARA BSALE")
        bsale_response = actualizar_stock_bsale(variant_id, office_id, qty,cost)

        if not bsale_response:
            return JsonResponse({'error': 'Etiqueta creada, pero no se pudo actualizar stock en Bsale.'}, status=500)


        # Modificar el archivo JSON para marcar el producto como impreso
        try:
            with open(url_json, 'r+') as json_file:
                data = json.load(json_file)
                for detail in data.get('details', []):
                    if detail.get('sku') == sku:
                        detail['printed'] = True
                json_file.seek(0)
                json.dump(data, json_file, indent=4)
                json_file.truncate()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return JsonResponse({'error': f'Error al procesar el archivo JSON: {str(e)}'}, status=400)

        # Actualizar el estado de la factura si todos los productos están impresos
        try:
            facturas = Purchase.objects.filter(urljson=url_json)
            if not facturas.exists():
                return JsonResponse({'error': 'No se encontraron facturas asociadas.'}, status=404)

            factura = facturas.first()  # Obtener la primera factura si hay múltiples
            if all(detail.get('printed') for detail in data.get('details', [])):
                factura.status = 3  # Procesado
                factura.save()
        except Purchase.DoesNotExist:
            pass  # Si no existe la factura, no hacemos nada

        # Devolver la URL del PDF generado
        pdf_url = os.path.join(settings.MEDIA_URL, relative_file_path)
        return JsonResponse({
            'urlPdf': pdf_url,
            'superids': super_ids,
            'sku': sku
        })

    return JsonResponse({'error': 'Método no permitido.'}, status=405)


from tqdm import tqdm
from django.db.models import Count
import sys
CHUNK_SIZE = 50  # Número de elementos por solicitud
from django.http import StreamingHttpResponse
import time
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def comparar_stock_bsale(request):
    try:
        # Inicialización
        print("Iniciando comparación de stock...")  # Log inicial
        total_productos_locales = 0
        productos_comparados = 0
        productos_con_diferencia_stock = []
        processed_iderps = set()  # Para rastrear productos ya procesados

        # Obtener productos locales
        productos_locales = Products.objects.values('sku', 'iderp', 'currentstock')
        productos_local_dict = {producto['iderp']: producto for producto in productos_locales}
        total_productos_locales = len(productos_local_dict)
        print(f"Productos locales obtenidos: {total_productos_locales}")

        iderp_locales = set(productos_local_dict.keys())
        if not iderp_locales:
            print("No hay productos locales para comparar.")
            return JsonResponse({
                "message": "No hay productos locales para comparar.",
                "resumen": {
                    "total_productos_locales": total_productos_locales,
                    "productos_comparados": 0,
                    "productos_con_diferencias": 0,
                    "detalles": []
                }
            }, status=200)

        # Procesar datos de Bsale
        next_url = f'{BSALE_API_URL}/stocks.json'
        while next_url:
            print(f"Consultando Bsale en: {next_url}")
            response = requests.get(next_url, headers={'access_token': BSALE_API_TOKEN})
            if response.status_code != 200:
                print(f"Error al obtener datos de Bsale: {response.status_code}")
                return JsonResponse({
                    "message": f"Error al obtener datos de Bsale: {response.status_code}",
                    "resumen": {}
                }, status=response.status_code)

            data = response.json()
            items = data.get('items', [])
            print(f"Productos obtenidos de Bsale en este lote: {len(items)}")

            for item in items:
                variant = item.get('variant')
                if not variant:
                    continue
                iderp = variant.get('id')
                bsale_stock = item.get('quantity', 0)

                # Solo procesar productos locales y no procesados previamente
                if iderp in iderp_locales and iderp not in processed_iderps:
                    processed_iderps.add(iderp)  # Marcar como procesado
                    productos_comparados += 1
                    producto_local = productos_local_dict[iderp]
                    diferencia_stock = bsale_stock - producto_local['currentstock']

                    if diferencia_stock != 0:
                        productos_con_diferencia_stock.append({
                            "sku": producto_local['sku'],
                            "stock_local": producto_local['currentstock'],
                            "stock_bsale": bsale_stock,
                            "diferencia": diferencia_stock
                        })
                        print(f"Diferencia encontrada para SKU {producto_local['sku']}: {diferencia_stock}")

            next_url = data.get('next', None)

        # Resumen final
        resumen = {
            "total_productos_locales": total_productos_locales,
            "productos_comparados": productos_comparados,
            "productos_con_diferencias": len(productos_con_diferencia_stock),
            "detalles": productos_con_diferencia_stock
        }
        print("Comparación completada. Resumen:")
        print(resumen)

        return JsonResponse({
            "message": "Proceso completado.",
            "resumen": resumen
        }, status=200)

    except Exception as e:
        print(f"Error inesperado: {str(e)}")  # Mostrar el error en consola
        return JsonResponse({"error": str(e)}, status=500)
    


""" @csrf_exempt
def comparar_stock_y_ajustar(request):
try:
    # Inicialización
    print("Iniciando comparación y ajuste de stock...")
    total_productos_locales = 0
    productos_comparados = 0
    productos_ajustados = 0
    productos_con_diferencia_stock = []
    processed_iderps = set()  # Para rastrear productos ya procesados

    # Obtener productos locales
    productos_locales = Products.objects.values('sku', 'iderp', 'currentstock')
    productos_local_dict = {producto['iderp']: producto for producto in productos_locales}
    total_productos_locales = len(productos_local_dict)
    print(f"Productos locales obtenidos: {total_productos_locales}")

    iderp_locales = set(productos_local_dict.keys())
    if not iderp_locales:
        print("No hay productos locales para comparar.")
        return JsonResponse({
            "message": "No hay productos locales para comparar.",
            "resumen": {
                "total_productos_locales": total_productos_locales,
                "productos_comparados": 0,
                "productos_ajustados": 0,
                "productos_con_diferencias": 0,
                "detalles": []
            }
        }, status=200)

    # Procesar datos de Bsale
    next_url = f'{BSALE_API_URL}/stocks.json'
    while next_url:
        print(f"Consultando Bsale en: {next_url}")
        response = requests.get(next_url, headers={'access_token': BSALE_API_TOKEN})
        if response.status_code != 200:
            print(f"Error al obtener datos de Bsale: {response.status_code}")
            return JsonResponse({
                "message": f"Error al obtener datos de Bsale: {response.status_code}",
                "resumen": {}
            }, status=response.status_code)

        data = response.json()
        items = data.get('items', [])
        print(f"Productos obtenidos de Bsale en este lote: {len(items)}")

        for item in items:
            variant = item.get('variant')
            if not variant:
                continue
            iderp = variant.get('id')
            bsale_stock = item.get('quantity', 0)

            # Solo procesar productos locales y no procesados previamente
            if iderp in iderp_locales and iderp not in processed_iderps:
                processed_iderps.add(iderp)  # Marcar como procesado
                productos_comparados += 1
                producto_local = productos_local_dict[iderp]
                diferencia_stock = bsale_stock - producto_local['currentstock']

                if diferencia_stock != 0:
                    productos_con_diferencia_stock.append({
                        "sku": producto_local['sku'],
                        "stock_local": producto_local['currentstock'],
                        "stock_bsale": bsale_stock,
                        "diferencia": diferencia_stock
                    })
                    print(f"Diferencia encontrada para SKU {producto_local['sku']}: {diferencia_stock}")

                    # Si hay stock faltante en el local, registrar en Bsale
                    if diferencia_stock > 0:
                        print(f"Ajustando stock para SKU {producto_local['sku']}...")
                        ajuste_response = registrar_recepcion_stock(
                            request, producto_local['sku'], diferencia_stock
                        )
                        if ajuste_response.status_code in [200, 201]:
                            productos_ajustados += 1
                        else:
                            print(f"Error al ajustar stock para SKU {producto_local['sku']}: {ajuste_response.content}")

        next_url = data.get('next', None)

    # Resumen final
    resumen = {
        "total_productos_locales": total_productos_locales,
        "productos_comparados": productos_comparados,
        "productos_ajustados": productos_ajustados,
        "productos_con_diferencias": len(productos_con_diferencia_stock),
        "detalles": productos_con_diferencia_stock
    }
    print("Comparación y ajuste completados. Resumen:")
    print(resumen)

    return JsonResponse({
        "message": "Proceso completado.",
        "resumen": resumen
    }, status=200)

except Exception as e:
    print(f"Error inesperado: {str(e)}")  # Mostrar el error en consola
    return JsonResponse({"error": str(e)}, status=500) """

@csrf_exempt
def actualizar_stock_local(request):
    # Definir ubicaciones que cuentan como "Narnia"
    narnia_locations = ['XT99-99', 'NRN1-1']

    # Obtiene todos los productos con sus unique_products asociados
    productos = Products.objects.all().prefetch_related('unique_products')
    total_productos = productos.count()

    # Configura la barra de progreso
    print("Actualizando stock local...")

    for idx, producto in enumerate(tqdm(productos, total=total_productos), start=1):
        # Contar los Uniqueproducts que están en stock, excluyendo las ubicaciones de "Narnia" y considerando solo state=0
        stock_local = producto.unique_products.filter(
            state=0
        ).exclude(locationname__in=narnia_locations).count()

        # Actualizar el campo `currentstock` con el conteo obtenido
        producto.currentstock = stock_local
        producto.save()

        # Mostrar progreso en la consola
        print(f"Progreso: {idx}/{total_productos} productos actualizados (SKU: {producto.sku}, Stock actualizado: {stock_local})")

    print("Actualización de stock local completada.")
    return JsonResponse({'message': 'Actualización de stock local completada.'}, status=200)


BSALE_API_URLID = "https://api.bsale.io/v1/variants.json"

@csrf_exempt
def actualizar_iderp(request):
    if request.method == 'GET':
        productos = Products.objects.all()  # Obtener todos los productos en la base de datos
        total_productos = productos.count()
        actualizados = 0
        eliminados = 0

        for producto in productos:
            sku = producto.sku
            url = f"{BSALE_API_URLID}?code={sku}"
            headers = {
                'access_token': BSALE_API_TOKEN,
                'Accept': 'application/json'
            }

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if data.get("count", 0) > 0:
                    id_bsale = data["items"][0]["id"]
                    # Actualizar el campo iderp en el producto
                    producto.iderp = id_bsale
                    producto.save()
                    actualizados += 1
                    print(f"Actualizado SKU: {sku} con iderp: {id_bsale} ({actualizados}/{total_productos})")
                else:
                    # Si no se encuentra el SKU, eliminar el producto y sus relaciones
                    with transaction.atomic():
                        producto.delete()  # Esto elimina el producto y, por cascading, sus relaciones
                    eliminados += 1
                    print(f"SKU {sku} no encontrado en Bsale. Producto eliminado ({eliminados}/{total_productos})")
            else:
                print(f"Error al consultar SKU {sku} en Bsale: {response.status_code} ({actualizados}/{total_productos})")

            # Opcional: Pausar ligeramente entre cada solicitud para evitar saturar el API

        print("Proceso de actualización completado.")
        return JsonResponse({
            "msg": "Proceso de actualización completado", 
            "total_actualizados": actualizados,
            "total_eliminados": eliminados
        })

    return JsonResponse({'msg': 'Método no permitido'}, status=405)



#Clave Dinamica

# Genera una clave dinámica para el usuario ADMIN
@csrf_exempt
@login_required(login_url='login_view')
def generate_dynamic_key(request):
    if request.user.usuario.rol == 'ADMIN':
        # Generar una clave aleatoria de 6 dígitos
        key = ''.join(random.choices(string.digits, k=6))

        # Guardar la clave en la base de datos con una validez de 5 minutos
        expiration_time = timezone.now() + datetime.timedelta(minutes=5)
        DynamicKey.objects.create(key=key, expiration_time=expiration_time)

        return JsonResponse({'key': key, 'expiration_time': expiration_time}, status=201)
    return JsonResponse({'error': 'No autorizado'}, status=403)

# Validar la clave dinámica
@csrf_exempt
@login_required(login_url='login_view')
def validate_dynamic_key(request):
    data = json.loads(request.body)
    key = data.get('key')
    
    # Verificar si la clave existe y no ha expirado
    try:
        dynamic_key = DynamicKey.objects.get(key=key, expiration_time__gte=timezone.now())
        return JsonResponse({'valid': True}, status=200)
    except DynamicKey.DoesNotExist:
        return JsonResponse({'valid': False, 'error': 'Clave no válida o expirada'}, status=400)
    



""" @csrf_exempt
@login_required(login_url='login_view')
def crear_sector(request):
    
@csrf_exempt
@login_required(login_url='login_view')
def buscar_sector(request):
    """
"""  BSALE_API_URL = 'https://api.bsale.io/v1'
BSALE_API_TOKEN = 'BSALE_API_TOKEN' """
#mover luego

from django.db.models import Sum
#  
@csrf_exempt
def obtener_datos_producto(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    sku = request.POST.get("sku")
    if not sku:
        return JsonResponse({"error": "El SKU es obligatorio"}, status=400)

    try:
        # Obtener datos del producto
        producto = Products.objects.prefetch_related('unique_products').get(sku=sku)

        # Calcular el stock total
        valid_bodega_ids = [10, 9, 7, 6, 5, 4, 2, 1]
        sectores = {sector.idsectoroffice: sector for sector in Sectoroffice.objects.all()}
        stock_total = sum(
            1 for unique_product in producto.unique_products.filter(state=0)
            if sectores.get(unique_product.location) and sectores[unique_product.location].idoffice in valid_bodega_ids
        )

        # Consultar precio en Bsale
        price_list_id = 3  # ID fijo de la lista de precios
        bsale_url = f"https://api.bsale.cl/v1/price_lists/{price_list_id}/details.json"
        headers = {
            "Content-Type": "application/json",
            "access_token": BSALE_API_TOKEN
        }
        params = {"code": sku}

        try:
            bsale_response = requests.get(bsale_url, headers=headers, params=params)
            bsale_response.raise_for_status()
            bsale_data = bsale_response.json()
            bsale_price = bsale_data.get("items", [{}])[0].get("variantValueWithTaxes", "No disponible")
        except requests.exceptions.RequestException:
            bsale_price = "No disponible"

        # Respuesta simplificada
        return JsonResponse({
            "sku": producto.sku,
            "lastCost": producto.lastcost or 0,
            "lastPrice": producto.lastprice or 0,
            "bsalePrice": bsale_price,
            "totalStock": stock_total,
            "iderp": producto.iderp

        })

    except Products.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#CREAR SECTORES
    

@csrf_exempt
def crear_sector_API(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Validación de los campos
            idoffice = data.get('idoffice')
            zone = data.get('zone')
            floor = data.get('floor')
            section = data.get('section')
            namesector = data.get('namesector')
            description = data.get('description', '')

            if not (idoffice and zone and floor and section and namesector):
                return JsonResponse({'error': 'Todos los campos son obligatorios excepto descripción'}, status=400)

            # Crear el sector
            sector = Sectoroffice.objects.create(
                idoffice=idoffice,
                zone=zone,
                floor=floor,
                section=section,
                namesector=namesector,
                description=description,
            )

            # Generar el código QR
            qr_code_content = f"B-{idoffice}-{zone}{floor}-{section}"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_code_content)
            qr.make(fit=True)

            # Convertir QR a imagen en formato base64 para enviar o guardar
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            # Retornar respuesta con los datos del sector creado
            return JsonResponse({
                'message': 'Sector creado con éxito.',
                'sector': {
                    'idsectoroffice': sector.idsectoroffice,
                    'idoffice': sector.idoffice,
                    'zone': sector.zone,
                    'floor': sector.floor,
                    'section': sector.section,
                    'namesector': sector.namesector,
                    'description': sector.description,
                    'qr_code_content': qr_code_content,
                },
                'qr_code': buffer.getvalue().decode('latin1')  # Imagen del QR
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


def listar_bodegas(request):
    try:
        # Obtener las bodegas activas
        bodegas = Bodega.objects.all().values('idoffice', 'name')  # Ajusta los nombres de los campos según tu modelo
        return JsonResponse(list(bodegas), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

from django.db.models import Subquery, OuterRef

def listar_sectores(request):
    try:
        # Anotar el nombre de la bodega usando una subconsulta
        sectores = (
            Sectoroffice.objects.annotate(
                bodega_name=Subquery(
                    Bodega.objects.filter(idoffice=OuterRef('idoffice')).values('name')[:1]
                )
            )
            .values(
                'idsectoroffice',
                'idoffice',
                'zone',
                'floor',
                'section',
                'namesector',
                'description',
                'bodega_name',
            )
        )
        
        return JsonResponse(list(sectores), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

#Carga masiva
import csv

@csrf_exempt
def bulk_upload(request, model_type):
    if request.method == 'POST':
        csv_file = request.FILES.get('file')
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({'error': 'El archivo debe ser un CSV'}, status=400)

        data_reader = csv.reader(csv_file.read().decode('utf-8').splitlines())
        next(data_reader)  # Omitimos la cabecera del archivo CSV

        created, errors = 0, 0
        if model_type == 'brand':
            for row in data_reader:
                try:
                    Brand.objects.create(name=row[0])
                    created += 1
                except Exception as e:
                    errors += 1
        elif model_type == 'category':
            for row in data_reader:
                try:
                    Category.objects.create(name=row[0])
                    created += 1
                except Exception as e:
                    errors += 1
        else:
            return JsonResponse({'error': 'Modelo no válido'}, status=400)

        return JsonResponse({'created': created, 'errors': errors})
    


#Editar Productos
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["PUT"])
def editar_producto(request, sku):
    try:
        # Verificar si el producto existe
        producto = Products.objects.filter(sku=sku).first()
        if not producto:
            return JsonResponse({'success': False, 'message': 'Producto no encontrado'}, status=404)
        
        # Parsear el cuerpo de la solicitud
        body = json.loads(request.body)

        # Actualizar los campos del producto
        producto.nameproduct = body.get('name', producto.nameproduct)
        producto.prefixed = body.get('prefixed', producto.prefixed)
        producto.brands = body.get('brands', producto.brands)
        producto.iderp = body.get('iderp', producto.iderp)
        producto.alto = body.get('alto', producto.alto)
        producto.largo = body.get('largo', producto.largo)
        producto.profundidad = body.get('profundidad', producto.profundidad)
        producto.peso = body.get('peso', producto.peso)
        
        # Guardar cambios en la base de datos
        producto.save()

        return JsonResponse({'success': True, 'message': 'Producto actualizado correctamente'}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Error al procesar el cuerpo de la solicitud'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error inesperado: {str(e)}'}, status=500)
    
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from io import BytesIO


@csrf_exempt
def imprimir_etiqueta_sector_simple(request):
    if request.method == 'POST':
        try:
            # Leer los datos de la solicitud
            data = json.loads(request.body)
            sectores = data.get('sectores', [])  # Lista de sectores [{idsector, qty}, ...]

            if not sectores:
                return JsonResponse({'error': 'La lista de sectores es obligatoria.'}, status=400)

            # Configuración del PDF
            pdf_filename = 'etiquetas_sectores.pdf'
            relative_file_path = os.path.join('models', 'sectores', pdf_filename)
            absolute_file_path = os.path.join(settings.MEDIA_ROOT, relative_file_path)
            os.makedirs(os.path.dirname(absolute_file_path), exist_ok=True)

            # Configuración de la página
            page_width, page_height = 100 * mm, 50 * mm  # Tamaño de la página
            pdf = canvas.Canvas(absolute_file_path, pagesize=(page_width, page_height))

            x_positions = [10 * mm, 60 * mm]  # Posiciones horizontales para los dos QR
            y_position = 10 * mm  # Posición vertical

            current_column = 0  # Controla si estamos en la primera o segunda columna

            for sector_data in sectores:
                idsector = sector_data.get('idsector')
                qty = sector_data.get('qty', 1)

                if not idsector or qty <= 0:
                    continue

                # Obtener la información del sector
                try:
                    sector = Sectoroffice.objects.get(idsectoroffice=idsector)
                except Sectoroffice.DoesNotExist:
                    continue

                # Generar la etiqueta
                etiqueta = f"B-{sector.idoffice}-{sector.zone}{sector.floor}-{sector.section}"
                text_etiqueta = f"{sector.zone}{sector.floor}-{sector.section}"


                for _ in range(qty):
                    # Generar el QR
                    qr_code = QrCodeWidget(etiqueta)
                    qr_bounds = qr_code.getBounds()
                    qr_width = qr_bounds[2] - qr_bounds[0]
                    qr_height = qr_bounds[3] - qr_bounds[1]

                    # Tamaño del QR en el PDF
                    qr_size = 40 * mm
                    qr_x = x_positions[current_column]
                    qr_y = y_position

                    # Crear un dibujo para el QR
                    qr_drawing = Drawing(qr_size, qr_size)
                    qr_drawing.add(qr_code)
                    qr_drawing.scale(qr_size / qr_width, qr_size / qr_height)

                    # Dibujar el QR
                    renderPDF.draw(qr_drawing, pdf, qr_x, qr_y)

                    # Dibujar el texto debajo del QR
                    pdf.setFont("Helvetica-Bold", 30)  # Texto en negrita y grande
                    pdf.drawCentredString(
                        qr_x + (qr_size / 2),  # Centrar horizontalmente
                        qr_y - 5 * mm,       # Ajustar posición vertical
                        text_etiqueta              # Texto del sector
                    )

                    # Mover a la siguiente columna
                    current_column += 1

                    # Si hemos llenado dos columnas, pasamos a una nueva página
                    if current_column >= len(x_positions):
                        pdf.showPage()
                        current_column = 0

            pdf.save()

            # Devolver la URL del PDF
            pdf_url = os.path.join(settings.MEDIA_URL, relative_file_path)
            return JsonResponse({
                'message': 'Etiquetas generadas correctamente.',
                'urlPdf': pdf_url
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Formato JSON inválido.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)

@csrf_exempt
def imprimir_etiquetas_masivas(request):
    if request.method == 'POST':
        try:
            # Leer los datos de la solicitud
            data = json.loads(request.body)
            sectores = data.get('sectores', [])  # Lista de sectores [{idsector, qty}, ...]
            
            if not sectores:
                return JsonResponse({'error': 'La lista de sectores es obligatoria.'}, status=400)

            # Configuración del PDF
            pdf_filename = 'etiquetas_sectores.pdf'
            relative_file_path = os.path.join('models', 'sectores', pdf_filename)
            absolute_file_path = os.path.join(settings.MEDIA_ROOT, relative_file_path)
            os.makedirs(os.path.dirname(absolute_file_path), exist_ok=True)

            page_width, page_height = 100 * mm, 50 * mm
            pdf = canvas.Canvas(absolute_file_path, pagesize=(page_width, page_height))

            for sector_data in sectores:
                idsector = sector_data.get('idsector')
                qty = sector_data.get('qty', 1)

                if not idsector or qty <= 0:
                    continue

                # Obtener la información del sector
                try:
                    sector = Sectoroffice.objects.get(idsectoroffice=idsector)
                except Sectoroffice.DoesNotExist:
                    continue

                # Generar la etiqueta
                etiqueta = f"B-{sector.idoffice}-{sector.zone}{sector.floor}-{sector.section}"

                for _ in range(qty):
                    # Generar el QR
                    qr_code = QrCodeWidget(etiqueta)
                    qr_bounds = qr_code.getBounds()
                    qr_drawing = Drawing(0, 0)
                    qr_drawing.add(qr_code)

                    qr_size = 40 * mm
                    qr_x = (page_width - qr_size) / 2
                    qr_y = (page_height - qr_size - 10 * mm)

                    # Dibujar el QR y el texto
                    renderPDF.draw(qr_drawing, pdf, qr_x, qr_y)
                    pdf.setFont("Helvetica", 10)
                    pdf.drawCentredString(page_width / 2, qr_y - 5 * mm, etiqueta)

                    # Añadir una nueva página si hay más etiquetas
                    pdf.showPage()

            pdf.save()

            # Devolver la URL del PDF
            pdf_url = os.path.join(settings.MEDIA_URL, relative_file_path)
            return JsonResponse({
                'message': 'Etiquetas generadas correctamente.',
                'urlPdf': pdf_url
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Formato JSON inválido.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)

from django.core.serializers.json import DjangoJSONEncoder

def backup_unique_products_view(request):
    try:
        backup_file = "uniqueproducts_backup.json"
        
        # Extraer todos los registros de Uniqueproducts
        unique_products = list(Uniqueproducts.objects.all().values())
        
        # Guardar los datos en un archivo JSON con un encoder que maneje datetime
        with open(backup_file, 'w') as f:
            json.dump(unique_products, f, indent=4, cls=DjangoJSONEncoder)
        
        return JsonResponse({"status": "success", "message": f"Respaldo creado en {backup_file}"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})
    
@csrf_exempt
def restore_unique_products_view(request):
    try:
        if request.method != 'POST':
            return JsonResponse({"status": "error", "message": "Método no permitido."})

        # Obtener el archivo cargado desde el request
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({"status": "error", "message": "No se proporcionó un archivo."})

        # Leer el contenido del archivo y cargarlo como JSON
        print("Leyendo el archivo de respaldo...")
        file_data = uploaded_file.read().decode('utf-8')
        unique_products = json.loads(file_data)
        print(f"Archivo leído correctamente. Total de registros: {len(unique_products)}")

        # Eliminar registros actuales
        print("Eliminando registros existentes...")
        Uniqueproducts.objects.all().delete()
        print("Registros eliminados correctamente.")

        # Procesar e insertar registros en lotes
        restored_products = []
        missing_products = []  # Almacenar los IDs de productos faltantes
        BATCH_SIZE = 5000  # Tamaño del lote para inserción

        print("Iniciando la restauración de registros...")
        for index, record in enumerate(tqdm(unique_products, desc="Procesando registros", unit="registro")):
            product_id = record.pop("product_id")

            try:
                product = Products.objects.get(id=product_id)  # Buscar producto relacionado
                restored_products.append(Uniqueproducts(product=product, **record))
            except Products.DoesNotExist:
                missing_products.append(product_id)  # Registrar producto faltante

            # Insertar en la base de datos cada BATCH_SIZE registros
            if len(restored_products) >= BATCH_SIZE:
                Uniqueproducts.objects.bulk_create(restored_products)
                restored_products = []  # Reiniciar la lista
                print(f"Lote de {BATCH_SIZE} registros insertado...")

        # Insertar los registros restantes
        if restored_products:
            Uniqueproducts.objects.bulk_create(restored_products)
            print(f"Último lote de {len(restored_products)} registros insertado.")

        print("Restauración completada.")
        return JsonResponse({
            "status": "success",
            "message": f"Se han restaurado los registros correctamente.",
            "missing_products": missing_products
        })

    except Exception as e:
        print(f"Error durante la restauración: {e}")
        return JsonResponse({"status": "error", "message": str(e)})

def normalize_keys(data):
    """Convierte las claves de un diccionario o lista de diccionarios a minúsculas."""
    if isinstance(data, list):
        return [normalize_keys(item) for item in data]
    elif isinstance(data, dict):
        return {key.lower(): normalize_keys(value) for key, value in data.items()}
    else:
        return data

@csrf_exempt
def restore_unique_products_view(request):
    try:
        if request.method != 'POST':
            return JsonResponse({"status": "error", "message": "Método no permitido."})

        # Obtener el archivo cargado desde el request
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({"status": "error", "message": "No se proporcionó un archivo."})

        print("Leyendo el archivo de respaldo...")

        # Leer el contenido completo del archivo y almacenarlo en memoria
        file_content = uploaded_file.read().decode('utf-8')

        # Convertir el contenido en un generador de JSON
        unique_products = json.loads(file_content)

        # Normalizar claves del JSON a minúsculas
        unique_products = normalize_keys(unique_products)
        print(f"Archivo leído y normalizado. Total de registros: {len(unique_products)}")

        # Eliminar registros actuales
        print("Eliminando registros existentes...")
        Uniqueproducts.objects.all().delete()
        print("Registros eliminados correctamente.")

        # Procesar e insertar registros en lotes
        restored_products = []
        missing_products = []  # Almacenar los SKUs de productos faltantes
        BATCH_SIZE = 100  # Tamaño del lote para inserción

        print("Iniciando la restauración de registros...")
        for record in tqdm(unique_products, desc="Restaurando registros", unit="registro"):
            sku = record.get("product_id")  # Ahora 'product_id' contiene el SKU del producto
            superid = record.get("superid")
            correlative = record.get("correlative")
            printlabel = record.get("printlabel")
            state = record.get("state")
            cost = record.get("cost")
            soldvalue = record.get("solvalue")
            datelastinventory = record.get("datelastinventory")
            observation = record.get("observation")
            location = record.get("location")
            typedocincome = record.get("typedocincome")
            ndocincome = record.get("ndocincome")
            typedocout = record.get("typedocout")
            ndocout = record.get("ndocout")
            dateadd = record.get("dateadd")
            iddocumentincome = record.get("iddocumentincome")
            ncompany = record.get("ncompany")

            # Convertir dateLastInventory si existe
            if datelastinventory:
                try:
                    datelastinventory = datetime.fromtimestamp(int(datelastinventory) / 1000)
                except (ValueError, TypeError):
                    datelastinventory = None

            try:
                # Buscar producto relacionado por SKU
                product = Products.objects.filter(sku=sku).first()
                if not product:
                    missing_products.append({"sku": sku, "reason": "Producto no existe"})
                    continue

                restored_products.append(
                    Uniqueproducts(
                        product=product,
                        superid=superid,
                        correlative=correlative,
                        printlabel=printlabel,
                        state=state,
                        cost=cost,
                        soldvalue=soldvalue,
                        datelastinventory=datelastinventory,
                        observation=observation,
                        location=location,
                        typedocincome=typedocincome,
                        ndocincome=ndocincome,
                        typedocout=typedocout,
                        ndocout=ndocout,
                        dateadd=dateadd,
                        iddocumentincome=iddocumentincome,
                        ncompany=ncompany,
                    )
                )

                # Insertar registros en lotes
                if len(restored_products) >= BATCH_SIZE:
                    Uniqueproducts.objects.bulk_create(restored_products)
                    restored_products = []
                    print(f"Lote de {BATCH_SIZE} registros insertado...")

            except Exception as e:
                missing_products.append({"sku": sku, "reason": f"Error inesperado: {e}"})

        # Insertar registros restantes
        if restored_products:
            Uniqueproducts.objects.bulk_create(restored_products)
            print(f"Último lote de {len(restored_products)} registros insertado.")

        print("Restauración completada.")

        return JsonResponse({
            "status": "success",
            "message": f"Se han restaurado {len(unique_products) - len(missing_products)} registros.",
            "missing_products": missing_products
        })

    except Exception as e:
        print(f"Error durante la restauración: {e}")
        return JsonResponse({"status": "error", "message": str(e)})
    

#Revisar carga masiva base de datos
import pandas as pd
def cargar_excel(file_path):
    errores = []  # Lista para almacenar los errores

    try:
        # Leer el archivo Excel
        df = pd.read_excel(file_path)

        # Recorrer cada fila del Excel
        for index, row in df.iterrows():
            sku = row['SKU']
            id_unico = row['IDUnico']
            id_sector_office = row['IDSectorOffice']

            # Verificar si el SKU existe en la tabla Products
            try:
                product = Products.objects.get(sku=sku)
            except Products.DoesNotExist:
                errores.append({'SKU': sku, 'Error': 'SKU no encontrado', 'Sector': id_sector_office})
                continue

            # Verificar si el ID Sector Office existe
            try:
                sector = Sectoroffice.objects.get(idsectoroffice=id_sector_office)
            except Sectoroffice.DoesNotExist:
                errores.append({'SKU': sku, 'Error': 'Sector no encontrado', 'Sector': id_sector_office})
                continue

            # Crear o actualizar el Uniqueproduct
            Uniqueproducts.objects.update_or_create(
                superid=id_unico,
                defaults={
                    'product': product,
                    'locationname': f"Sector {id_sector_office}",
                    'state': 1,  # Estado predeterminado
                }
            )
            print(f"Producto {sku} con ID único {id_unico} asignado al sector {id_sector_office}.")

        # Generar PDF de errores si existen
        if errores:
            generar_pdf_errores(errores, "errores_carga.pdf")
            print("Errores encontrados. Se ha generado un archivo PDF con los detalles.")

        print("Carga completada.")
    except Exception as e:
        print(f"Error al procesar el Excel: {str(e)}")


def generar_pdf_errores(errores, pdf_filename):
    try:
        # Ruta para guardar el PDF
        pdf_path = os.path.join("media", pdf_filename)
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        # Crear el PDF
        pdf = canvas.Canvas(pdf_path, pagesize=letter)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, 750, "Errores de Carga Masiva")
        pdf.drawString(50, 730, "-------------------------------------------")

        y_position = 710
        for error in errores:
            pdf.drawString(50, y_position, f"SKU: {error['SKU']}")
            pdf.drawString(200, y_position, f"Error: {error['Error']}")
            pdf.drawString(400, y_position, f"Sector: {error['Sector']}")
            y_position -= 20

            if y_position < 50:  # Crear nueva página si el espacio se agota
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                y_position = 750

        pdf.save()
        print(f"Archivo PDF generado: {pdf_path}")
    except Exception as e:
        print(f"Error al generar el PDF: {str(e)}")


@csrf_exempt
def bulk_upload_products(request):
    try:
        if request.method != 'POST':
            return JsonResponse({"status": "error", "message": "Método no permitido."})

        # Leer archivo JSON
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({"status": "error", "message": "No se proporcionó un archivo."})

        file_data = uploaded_file.read().decode('utf-8')
        products_data = json.loads(file_data)

        # Normalizar claves
        products_data = normalize_keys(products_data)
        print(f"Archivo leído y normalizado. Total de registros: {len(products_data)}")

        # Extraer SKUs existentes
        existing_skus = set(Products.objects.values_list('sku', flat=True))
        print(f"SKUs existentes en la base de datos: {len(existing_skus)}")

        # Procesar e insertar productos
        new_products = []
        duplicate_skus = []
        for record in tqdm(products_data, desc="Cargando productos", unit="producto"):
            sku = record.get("aux")  # En tu JSON, AUX representa el SKU

            # Verificar si el SKU ya existe
            if sku in existing_skus:
                duplicate_skus.append(sku)
                continue  # Saltar al siguiente registro

            # Convertir fecha si es necesario
            createdate = record.get("createdate")
            if createdate and createdate != 0:
                try:
                    createdate = datetime.fromtimestamp(int(createdate) / 1000)
                except (ValueError, TypeError):
                    createdate = None
            else:
                createdate = None

            # Crear objeto de producto
            new_products.append(
                Products(
                    sku=sku,
                    nameproduct=record.get("nameproduct"),
                    prefixed=record.get("prefixed"),
                    brands=record.get("brand"),
                    codebar=record.get("codebar"),
                    codebar2=record.get("codebar2"),
                    codebar3=record.get("codebar3"),
                    iderp=record.get("iderp"),
                    codsupplier=record.get("codsupplier"),
                    description=record.get("description"),
                    lastcost=record.get("lastcost"),
                    latestreplenishment=None,  # Manejo adicional si se necesita
                    lastprice=record.get("lastprice"),
                    currentstock=record.get("currentstock"),
                    createdate=createdate,
                    imgthumbs=record.get("imgthumbs"),
                    idmelimain=record.get("idmelimain"),
                    idproduct=record.get("idproduct"),
                    meliprice_s1=record.get("meliprice_s1"),
                    uniquecodebar=record.get("uniquecodebar", False),
                    profundidad=record.get("profundidad"),
                    largo=record.get("largo"),
                    alto=record.get("alto"),
                    peso=record.get("peso"),
                )
            )

        # Insertar en la base de datos
        if new_products:
            Products.objects.bulk_create(new_products)
            print(f"Se han insertado {len(new_products)} nuevos productos.")

        # Respuesta con resumen
        return JsonResponse({
            "status": "success",
            "message": f"Se insertaron {len(new_products)} productos nuevos.",
            "duplicates": duplicate_skus
        })

    except Exception as e:
        print(f"Error durante la carga: {e}")
        return JsonResponse({"status": "error", "message": str(e)})