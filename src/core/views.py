from django.shortcuts import render, redirect
from core.models import *
from django.contrib.auth import login as login_f
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate
from django.conf import settings
from pymongo import MongoClient
from datetime import datetime, timedelta
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
from io import BytesIO
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



@login_required(login_url='login_view')
def delete_user(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    usuario.delete()
    return JsonResponse({'message': 'Usuario eliminado exitosamente.'}, status=204)

@login_required(login_url='login_view')
def recepciones_aceptadas(request):
    return render(request, 'recepciones_aceptadas.html')

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
    return render(request, 'anadir_psector.html')

@login_required(login_url='login_view')
def cuadrar_sector_view(request):
    return render(request, 'cuadrar_sector.html')

@login_required(login_url='login_view')
def despacho(request):
    return render(request, 'despacho.html')


""" 
APIS  """

def login_view(request):
    template_name = "login.html"
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login_f(request, user)
            return redirect("index")
        else:
            context['error_message'] = 'El usuario o la contraseña son incorrectos.'

    return render(request, template_name, context)



@login_required(login_url='login_view')
def index(request):
    template_name = "index.html"
    context = {}
    meses_anteriores = []
    # Obtenemos la fecha actual
    fecha_actual = datetime.now()

    # Agregamos el mes actual a la lista
    meses_anteriores.append(fecha_actual.strftime('%B %Y'))

    # Iteramos para obtener los 4 meses anteriores
    for _ in range(4):
        # Restamos un mes a la fecha actual
        fecha_actual -= timedelta(days=fecha_actual.day)
        fecha_actual -= timedelta(days=1)
        # Agregamos el mes actual a la lista
        meses_anteriores.append(fecha_actual.strftime('%B %Y'))
    context["meses"] = meses_anteriores
    return render(request, template_name, context)

# Crear usuario
@csrf_exempt
@login_required(login_url='login_view')
def create_user(request):
    data = json.loads(request.body)

    correo = data.get('correo')
    clave = data.get('clave', '40emmett90')  # Clave por defecto
    nombres_apellidos = data.get('nombres_apellidos', '')
    rut = data.get('rut', '')
    telefono = data.get('telefono', '')

    if not correo:
        return JsonResponse({'error': 'El campo correo es obligatorio.'}, status=400)

    # Crear el usuario
    usuario = Usuario.objects.create(
        correo=correo,
        clave=clave,
        nombres_apellidos=nombres_apellidos,
        rut=rut,
        telefono=telefono,
    )

    return JsonResponse({'message': 'Usuario creado exitosamente.'}, status=201)



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
    bodegas = Bodega.objects.all()
    
    bodegas_data = [
        {
            'id': bodega.idoffice,
            'name': bodega.name
        }
        for bodega in bodegas
    ]
    
    return JsonResponse({'bodegas': bodegas_data})


def buscar_productosAPI(request):
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)

    # Filtrar productos por SKU o nombre si hay un término de búsqueda
    if query:
        productos = Products.objects.filter(
            models.Q(sku__icontains=query) | models.Q(nameproduct__icontains=query)
        ).prefetch_related('unique_products')
    else:
        return JsonResponse({
            'products': [],
            'total_pages': 1,
            'current_page': 1
        })

    # Excluir ubicaciones que cuentan como "Narnia"
    narnia_locations = ['XT99-99', 'NRN1-1']

    # Obtener todos los sectores de la oficina
    sectores = {sector.idsectoroffice: sector.namesector for sector in Sectoroffice.objects.all()}

    # Paginación, 10 productos por página
    paginator = Paginator(productos, 10)
    try:
        productos_page = paginator.page(page)
    except PageNotAnInteger:
        productos_page = paginator.page(1)
    except EmptyPage:
        productos_page = paginator.page(paginator.num_pages)

    productos_data = []
    for producto in productos_page:
        unique_products_data = []
        for unique_product in producto.unique_products.filter(state=0).exclude(locationname__in=narnia_locations):
            location_name = sectores.get(unique_product.location, 'Ubicación no encontrada')

            unique_products_data.append({
                'superid': unique_product.superid,
                'locationname': location_name
            })
        
        productos_data.append({
            'id': producto.id,
            'sku': producto.sku,
            'name': producto.nameproduct,
            'price': producto.lastprice,
            'stock_total': len(unique_products_data),  # Stock total basado en el número de productos únicos
            'unique_products': unique_products_data
        })

    response = {
        'products': productos_data,
        'total_pages': paginator.num_pages,
        'current_page': productos_page.number,
    }

    return JsonResponse(response)




def producto_detalles(request, product_id):
    try:
        # Obtener el producto con sus productos únicos relacionados
        producto = Products.objects.prefetch_related('unique_products').get(id=product_id)
        
        # Obtener todas las bodegas para usarlas en el mapeo
        bodegas = Bodega.objects.all()
        bodega_mapping = {bodega.idoffice: bodega.name for bodega in bodegas}

        # Obtener todas las ubicaciones (sectores) para usarlas en el mapeo
        sectores = Sectoroffice.objects.all()
        sector_mapping = {sector.idsectoroffice: sector for sector in sectores}

        # Imprimir los primeros 10 sectores en la consola (excluyendo NRN)
        print("Primeros 10 sectores (excluyendo NRN):")
        counter = 0
        for sector in sectores:
            if sector.zone == 'NRN':
                continue  # Excluir sectores con la zona 'NRN'
            print(f"ID Sector: {sector.idsectoroffice}, Name: {sector.namesector}, Office ID: {sector.idoffice}, Zone: {sector.zone}, Floor: {sector.floor}, Section: {sector.section}")
            counter += 1
            if counter >= 10:
                break  # Detener después de los primeros 10 sectores

        # Filtrar los productos únicos relacionados con el producto, excluyendo Narnia (XT99-99) y sectores con zone='NRN'
        unique_products = producto.unique_products.exclude(location__in=Sectoroffice.objects.filter(namesector="XT99-99")).exclude(location__in=Sectoroffice.objects.filter(zone="NRN"))
        
        # Inicializar el stock por bodega
        bodegas_stock = {bodega.idoffice: 0 for bodega in bodegas}
        
        # Calcular el stock de cada bodega contando la cantidad de `superid` asociados a cada sector (ubicación)
        for unique_product in unique_products:
            # Obtener el sector asociado a la ubicación (location) del producto
            sector = sector_mapping.get(unique_product.location)

            if sector and sector.namesector != "XT99-99" and sector.zone != "NRN":  # Excluir Narnia y sectores con zone 'NRN'
                bodega_name = bodega_mapping.get(sector.idoffice, 'Bodega desconocida')  # Usar el idOffice del sector para obtener el nombre de la bodega

                # Incrementar el stock en la bodega correspondiente (contando el `superid`)
                if sector.idoffice in bodegas_stock:
                    bodegas_stock[sector.idoffice] += 1  # Incrementar 1 por cada `superid` encontrado
            else:
                bodega_name = 'Ubicación no encontrada' if not sector else 'Narnia'

            unique_product.bodega = bodega_name  # Asociar la bodega al producto único

        # Crear la respuesta con los detalles del producto
        response_data = {
            'id': producto.id,
            'sku': producto.sku,
            'name': producto.nameproduct,
            'price': producto.lastprice,
            'stock_total': sum(bodegas_stock.values()),  # Stock total sumando todas las bodegas, excepto Narnia y NRN
            'bodegas': {bodega_mapping[bodega_id]: stock for bodega_id, stock in bodegas_stock.items()},  # Información de stock por bodega
            'unique_products': [
                {
                    'superid': unique_product.superid,
                    'locationname': sector_mapping.get(unique_product.location, 'Ubicación no encontrada').namesector,  # Nombre del sector
                    'bodega': unique_product.bodega,  # Nombre de la bodega asociada
                } for unique_product in unique_products
            ]
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
        data = json.loads(request.body)

        id_erp = data.get('idERP')
        sku = data.get('sku')
        b_price = data.get('bPrice')
        type = data.get('type')

        # Validar los datos recibidos
        if not id_erp or not sku or not b_price or not type:
            return JsonResponse({'error': 'Datos incompletos'}, status=400)

        # Paso 1: Construir el URL para obtener los costos en Bsale
        url_costs = f"{BSALE_API_URL}/price_lists/{type}/details.json?variantid={id_erp}"
        headers = {
            'access_token': BSALE_TOKEN,  # Usar 'access_token' en lugar de 'Authorization'
            'Content-Type': 'application/json'
        }

        # Realizar la solicitud GET para obtener información del documento
        response = requests.get(url_costs, headers=headers)

        # Verificar el estado de la respuesta
        if response.status_code != 200:
            return JsonResponse({'error': 'Error al obtener datos de Bsale', 'detalle': response.text}, status=response.status_code)

        # Procesar los datos recibidos de Bsale
        bsale_data = response.json()
        items = bsale_data.get('items', [])
        if items:
            product_id = items[0].get('id')
            print(f"ID del producto en el primer ítem: {product_id}")
        else:
            print("No se encontraron ítems en la respuesta de Bsale")
            return JsonResponse({'error': 'No se encontró ningún ítem en la respuesta de Bsale'}, status=404)

        # Paso 2: Construir la URL para actualizar el precio en Bsale
        url_update_price = f"{BSALE_API_URL}/price_lists/{type}/details/{product_id}.json"
        print(url_update_price)

        # Paso 3: Calcular el precio base sin IVA
        variant_value = float(b_price) / 1.19  # Convertir b_price a float antes de dividir
        update_data = {
            'variantValue': variant_value,
            "id":product_id
        }

        # Paso 4: Realizar la solicitud PUT para actualizar el precio
        put_response = requests.put(url_update_price, headers=headers, json=update_data)

        # Verificar el estado de la solicitud PUT
        if put_response.status_code != 200:
            return JsonResponse({'error': 'Error al actualizar el precio en Bsale', 'detalle': put_response.text}, status=put_response.status_code)

        # Obtener la respuesta de la actualización y devolver el resultado
        updated_data = put_response.json()

        return JsonResponse({
            'message': 'Precio actualizado correctamente en Bsale',
            'bsale_data': bsale_data,
            'updated_data': updated_data
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def listar_compras(request):
    # Obtener parámetros de filtro y paginación desde el request
    status = request.GET.get('status')  # Aceptará '0', '1', '2' o 'all'
    page_number = request.GET.get('page', 1)
    search_query = request.GET.get('q', '').strip()  # Búsqueda por folio

    # Filtrar las facturas según el estado
    if status == '0':
        compras = Purchase.objects.filter(status=0)  # Pendientes
    elif status == '1':
        compras = Purchase.objects.filter(status=1)  # Aceptadas
    elif status == '2':
        compras = Purchase.objects.filter(status=2)  # Rechazadas
    else:
        compras = Purchase.objects.all()  # Todas las facturas

    # Filtrar por folio si se proporciona un término de búsqueda
    if search_query:
        compras = compras.filter(number__icontains=search_query)

    # Crear paginador
    paginator = Paginator(compras, 10)  # 10 facturas por página
    page_obj = paginator.get_page(page_number)

    # Formatear los datos en una lista
    compras_list = []
    for compra in page_obj:
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
                
                # Extraer el detalle de la factura
                detalles = json_data.get('details', [])

                # Añadir el campo `printed` si no existe en cada detalle
                for detalle in detalles:
                    if 'printed' not in detalle:
                        detalle['printed'] = False

                # Determinar si la factura completa está marcada como impresa
                json_data['invoice_printed'] = all(detalle.get('printed', False) for detalle in detalles)

                # Guardar los cambios en el archivo JSON para que persista la estructura
                with open(json_file_path, 'w') as file:
                    json.dump(json_data, file, indent=4)

                # Enviar los detalles y la URL del JSON como respuesta
                return JsonResponse({
                    'details': detalles,
                    'invoice_printed': json_data['invoice_printed'],
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

    # Filtrar facturas pendientes (status = 0) y ordenar por fecha de adición descendente
    facturas = Purchase.objects.filter(status=0).order_by('-dateadd')
    
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

@csrf_exempt
def aprobar_factura(request):
    if request.method == 'POST':
        # Revisar si el id está en el POST
        factura_id = request.POST.get('id')
        if not factura_id:
            return JsonResponse({'error': 'ID de factura no proporcionado.'}, status=400)

        try:
            # Buscar la factura con el ID proporcionado
            factura = Purchase.objects.get(id=factura_id)
            # Cambiar el estado a "Aprobada"
            factura.status = 1
            factura.save()
            return JsonResponse({'message': 'Factura aprobada con éxito.'})
        except Purchase.DoesNotExist:
            # Si no se encuentra la factura, devolver un mensaje de error
            return JsonResponse({'error': 'Factura no encontrada.'}, status=404)
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
            },
            "details": detalles,  # Detalles extraídos del archivo JSON
        }

        # Retornar la respuesta como JSON
        return JsonResponse(data, safe=False)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)

""" Ingresar Documentos """
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


@csrf_exempt
def create_product(request):
    if request.method == 'POST':
        # Obtener los datos del producto desde la solicitud
        sku = request.POST.get('sku', '')
        name_product = request.POST.get('nombre', '')
        brand = request.POST.get('marca', '')
        price = request.POST.get('precio', 0)
        descripcion = request.POST.get('precio', 0)

        if not sku or not name_product:
            return JsonResponse({'error': 'Datos incompletos para crear el producto.'}, status=400)

        # Crear un nuevo producto
        try:
            product = Products.objects.create(
                sku=sku,
                nameproduct=name_product,
                brands=brand,
                lastprice=int(price),
                description = descripcion,
            )
            return JsonResponse({'message': 'Producto creado correctamente.', 'id': product.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)

@csrf_exempt
def generar_json(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Obtener los datos necesarios del encabezado para el modelo Purchase
            headers = data.get('headers', {})
            supplier = headers.get('supplier', '')
            supplier_name = headers.get('supplierName', '')
            type_document = headers.get('typeDocument', None)
            number_document = headers.get('nDocument', None)
            observation = headers.get('observation', '')
            date_purchase = headers.get('datePurchase', None)
            subtotal = headers.get('subtotal', 0)
            url_img = headers.get('urlImg', '')

            # Crear el nombre del archivo basado en los datos del encabezado
            file_name = f"s_{supplier}t_{type_document}f_{number_document}.json"

            # Construir la ruta relativa de guardado
            relative_file_path = os.path.join('models', 'invoices', 'json', file_name)
            absolute_file_path = os.path.join(settings.BASE_DIR, relative_file_path)

            # Crear las carpetas si no existen
            os.makedirs(os.path.dirname(absolute_file_path), exist_ok=True)

            # Iterar sobre los detalles de la factura para asignar el `idERP` a cada SKU
            for detalle in data.get('details', []):
                sku = detalle.get('sku', '')
                try:
                    producto = Products.objects.get(sku=sku)
                    detalle['idERP'] = producto.iderp  # Asignar el valor de `idERP`
                except Products.DoesNotExist:
                    detalle['idERP'] = None  # Si no se encuentra el SKU, asignar None

            # Guardar el JSON en el archivo especificado
            with open(absolute_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)

            # Crear el registro en la base de datos
            purchase = Purchase.objects.create(
                supplier=supplier,
                suppliername=supplier_name,
                typedoc=type_document,
                number=number_document,
                observation=observation,
                dateadd=timezone.now(),
                dateproccess=date_purchase,
                subtotal=subtotal,
                urljson=relative_file_path,  # Guardar solo la ruta relativa en la base de datos
                urlimg=url_img,
                status=0,  # Estado predeterminado
            )

            # Devolver la ruta del archivo creada y un mensaje de éxito
            return JsonResponse({
                'message': 'Archivo JSON y registro creados correctamente',
                'urlJson': relative_file_path,
                'purchaseId': purchase.id
            }, status=201)

        except Exception as e:
            print("Error:", e)
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)
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


def get_products(request):
    query = request.GET.get('q', '')
    page_number = request.GET.get('page', 1)
    page_size = 10  # Número de productos por página (ajústalo según tu necesidad)

    # Filtrar productos según la búsqueda por SKU o nombre
    products = Products.objects.filter(
        Q(sku__icontains=query) | Q(nameproduct__icontains=query)
    ).values('id', 'sku', 'nameproduct', 'brands', 'codebar', 'lastprice')

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
        # Parse the JSON body
        try:
            body = json.loads(request.body)
            term = body.get('searchTerm', '')
        except json.JSONDecodeError:
            return JsonResponse({'resp': 3, 'msg': 'Error decoding JSON'})

        print(f"Search term received: '{term}'")

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
                    print(f"Sector found: {sector.namesector} with id {sector.idsectoroffice}")

                    # Buscar productos en Uniqueproducts asociados al sector encontrado
                    productos = Uniqueproducts.objects.filter(location=sector.idsectoroffice)
                    productos_data = []

                    for producto in productos:
                        try:
                            # Intentar acceder al producto relacionado
                            productos_data.append({
                                'superid': producto.superid,
                                'sku': producto.product.sku if producto.product else "N/A",
                                'name': producto.product.nameproduct if producto.product else "N/A"
                            })
                        except Products.DoesNotExist:
                            print(f"No related Product found for Uniqueproduct with superid {producto.superid}")
                            continue  # Ignorar este producto si no tiene un producto relacionado

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

@csrf_exempt
def add_product_to_sector(request):
    if request.method == 'POST':
        # Verificar si los datos vienen en formato JSON
        try:
            body = json.loads(request.body)  # Decodificar el cuerpo JSON
            productos = body.get('productos', [])  # Obtener la lista de productos
            sector_name = body.get('sector', '')  # Obtener el nombre del sector
        except json.JSONDecodeError:
            return JsonResponse({'resp': 3, 'msg': 'Error al decodificar JSON'})

        # Verificar que se proporcionaron los productos y el sector
        if not productos or not sector_name:
            return JsonResponse({'resp': 3, 'msg': 'El Super ID del producto y el sector son obligatorios.'})

        # Dividir el sector para obtener idOffice y nameSector
        if 'B-' in sector_name:
            parts = sector_name.split('-')
            if len(parts) == 4:
                id_office = parts[1]
                name_sector = parts[2] + '-' + parts[3]

                # Buscar el sector
                sector = Sectoroffice.objects.filter(namesector=name_sector, idoffice=id_office).first()

                if sector:
                    productos_no_encontrados = []
                    productos_actualizados = 0

                    # Procesar cada producto en la lista de productos
                    for producto_data in productos:
                        superid = producto_data.get('superid', '')
                        if superid:
                            # Buscar el producto por superid
                            producto = Uniqueproducts.objects.filter(superid=superid).first()

                            if producto:
                                # Asociar el producto al sector actualizando el campo 'location'
                                producto.location = sector.idsectoroffice
                                producto.save()
                                productos_actualizados += 1
                            else:
                                productos_no_encontrados.append(superid)
                        else:
                            productos_no_encontrados.append(superid)

                    # Preparar el mensaje de respuesta
                    if productos_no_encontrados:
                        return JsonResponse({
                            'resp': 2,
                            'msg': f'Algunos productos no fueron encontrados: {", ".join(productos_no_encontrados)}',
                            'productos_actualizados': productos_actualizados
                        })
                    else:
                        return JsonResponse({'resp': 1, 'msg': 'Todos los productos fueron añadidos con éxito.'})

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
    if request.method == 'POST':
        try:
            body = json.loads(request.body)  # Decodificar el cuerpo JSON
            superids = body.get('superids', [])  # Obtener la lista de superids de productos escaneados
            sector_name = body.get('sector_id', '')  # Obtener el sector donde se está cuadrando
        except json.JSONDecodeError:
            return JsonResponse({'resp': 3, 'msg': 'Error al decodificar JSON'})

        # Verificar que se proporcionaron los superids y el sector
        if not superids or not sector_name:
            return JsonResponse({'resp': 3, 'msg': 'Super IDs y sector son obligatorios.'})

        # Dividir el sector para obtener idOffice y nameSector
        if 'B-' in sector_name:
            parts = sector_name.split('-')
            if len(parts) == 4:
                id_office = parts[1]
                name_sector = parts[2] + '-' + parts[3]

                # Buscar el sector
                sector = Sectoroffice.objects.filter(namesector=name_sector, idoffice=id_office).first()

                if sector:
                    # Productos en Narnia
                    productos_en_narnia = []

                    # Iterar por los productos en el sector actual
                    productos = Uniqueproducts.objects.filter(location=sector.idsectoroffice)

                    for producto in productos:
                        if producto.superid not in superids:
                            # El producto no fue escaneado, así que lo movemos a "Narnia"
                            producto.location = get_narnia_id()  # Función que obtiene el ID de Narnia
                            producto.save()
                            productos_en_narnia.append(producto)

                    if productos_en_narnia:
                        # Enviar un correo con los productos que fueron enviados a Narnia
                        enviar_correo_a_narnia(productos_en_narnia, sector)

                    return JsonResponse({'resp': 1, 'msg': 'Cuadratura realizada con éxito.'})
                else:
                    return JsonResponse({'resp': 3, 'msg': f'Sector "{name_sector}" no encontrado.'})
            else:
                return JsonResponse({'resp': 3, 'msg': 'Formato de sector incorrecto.'})
        else:
            return JsonResponse({'resp': 3, 'msg': 'El formato del sector no es válido.'})

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
        'access_token': '1b7908fa44b56ba04a3459db5bb6e9b12bb9fadc',  # Reemplaza con tu token de Bsale
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
    
def actualizar_stock_bsale(variant_id, stock):
    """Función para actualizar el stock en Bsale usando el variant_id"""
    url = f"https://api.bsale.cl/v1/variants/{variant_id}/stock.json"
    headers = {
        'access_token': '1b7908fa44b56ba04a3459db5bb6e9b12bb9fadc',  # Reemplaza con tu token
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    data = {
        'quantityAvailable': stock  # Stock actualizado
    }
    
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return True
    else:
        print(f"Error al actualizar stock en Bsale. Status code: {response.status_code}")
        return False
    

BSALE_API_URL = 'https://api.bsale.io/v1'
BSALE_TOKEN = '1b7908fa44b56ba04a3459db5bb6e9b12bb9fadc'

# Función para obtener el variantId
def obtener_variant_id(sku):
    url = f"{BSALE_API_URL}/stocks.json?code={sku}"
    headers = {
        'access_token': BSALE_TOKEN,
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
        'access_token': BSALE_TOKEN,
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Función para actualizar el stock en Bsale
def actualizar_stock_bsale(variant_id, office_id, new_stock):
    url = f"{BSALE_API_URL}/stocks/receptions.json"
    headers = {
        'access_token': BSALE_TOKEN,
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
                "cost": 3200
            }
        ]
    }
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al actualizar stock en Bsale. Status code: {response.status_code}")
        return None
    
def calcular_stock_local(sku):
    """Función que calcula el stock local sumando los productos únicos relacionados al SKU"""
    productos_unicos = Uniqueproducts.objects.filter(product__sku=sku)
    stock_total = productos_unicos.count()
    return stock_total


def obtener_stock_id(variant_id, office_id):
    """Función para obtener el stock_id de una variante y sucursal (office) en Bsale"""
    headers = {
        'access_token': BSALE_TOKEN,
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
                    'access_token': BSALE_TOKEN,
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
                'access_token': BSALE_TOKEN,
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
            n_document = data.get('nDocument')
            type_document = data.get('typeDocument')
            company = data.get('company')
            products = data.get('products', [])

            # Procesar cada producto para el consumo en Bsale
            for product in products:
                superid = product.get('superid')
                cantidad = int(product.get('quantity', 1))  # Cantidad a descontar (1 por defecto)

                # Verificar si el superid existe en Uniqueproducts
                unique_product = Uniqueproducts.objects.select_related('product').filter(superid=superid).first()

                if not unique_product:
                    print(f"SuperID {superid} no encontrado en la base de datos.")
                    return JsonResponse({'title': 'SuperID no encontrado', 'icon': 'error', 'row': 0})

                # Obtener el `Sectoroffice` relacionado usando el `location` de `unique_product`
                sector = Sectoroffice.objects.filter(idsectoroffice=unique_product.location).first()
                if not sector:
                    print(f"Sector no encontrado para el Location ID {unique_product.location}")
                    return JsonResponse({'title': 'Sector no encontrado para el producto', 'icon': 'error'})

                idoffice = sector.idoffice
                print(f"ID de Oficina obtenido: {idoffice}")

                # Obtener el `iderp` del producto asociado
                product_instance = unique_product.product
                iderp = product_instance.iderp  # Aquí se obtiene el `iderp`
                print(f"Producto asociado: {product_instance}, SKU: {product_instance.sku}, ID ERP: {iderp}")

                if not iderp:
                    return JsonResponse({'title': 'El producto asociado no tiene un ID ERP válido', 'icon': 'error', 'row': 0})

                # Mover el producto a la bodega "Despachados"
                despachados_bodega, created = Bodega.objects.get_or_create(
                    name="Despachados",
                    defaults={
                        "description": "Bodega para productos despachados",
                        "address": "Dirección ficticia para despachos",
                        "latitude": -33.4489,
                        "longitude": -70.6693,
                        "country": "Chile",
                        "city": "Santiago",
                        "state": 1,
                        "emailStore": "despachos@example.com",
                        "idoffice": idoffice  # Usa el `idoffice` obtenido de Sectoroffice
                    }
                )

                # Actualizar la información del producto en la base de datos local
                unique_product.location = despachados_bodega.idoffice
                unique_product.observation = f"Salida: {type_document} | Empresa: {company}"
                unique_product.typedocout = type_document
                unique_product.ndocout = n_document
                unique_product.datelastinventory = timezone.now()
                unique_product.state = 1  # Estado de "descontado"
                unique_product.ncompany = company
                unique_product.save()

                # Preparar los datos para enviar a Bsale
                data_bsale = {
                    "note": f"Despacho desde empresa {company}",
                    "officeId": idoffice,  # ID de la oficina actual
                    "details": [
                        {
                            "quantity": cantidad,
                            "variantId": iderp  # Usar `iderp` para el consumo en Bsale
                        }
                    ]
                }

                # Hacer la solicitud POST a Bsale usando la URL de consumo correcta
                headers = {
                    "access_token": BSALE_TOKEN,
                    "Content-Type": "application/json"
                }

                response = requests.post("https://api.bsale.io/v1/stocks/consumptions.json", headers=headers, json=data_bsale)
                
                # Verificar si la respuesta de Bsale es exitosa
                if response.status_code not in [200, 201]:
                    print(f"Error al consumir en Bsale: {response.status_code} - {response.text}")
                    return JsonResponse({'title': 'Error al consumir en Bsale', 'icon': 'error', 'message': response.text}, status=response.status_code)

            return JsonResponse({'title': 'Productos despachados con éxito', 'icon': 'success'})

        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return JsonResponse({'title': 'Error en el despacho', 'icon': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'title': 'Método no permitido', 'icon': 'error'}, status=405)

BSALE_API_URL = "https://api.bsale.cl/v1"  # URL base de Bsale
BSALE_API_TOKEN = "1b7908fa44b56ba04a3459db5bb6e9b12bb9fadc"  # Coloca tu token de autenticación


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
        'access_token': BSALE_TOKEN,
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

            # Verificar si el SKU asociado está en la lista de productos del documento
            if associated_sku not in document_products:
                print("El SKU asociado no coincide con los productos del documento.")
                return JsonResponse({'error': 'El SKU asociado no coincide con los productos del documento'}, status=400)

            # Respuesta exitosa
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
from reportlab.pdfgen import canvas
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import mm
from reportlab.graphics.barcode import code128


@csrf_exempt
def imprimir_etiqueta(request):
    if request.method == 'POST':
        # Obtener los datos enviados desde el front-end
        sku = request.POST.get('sku')
        model = request.POST.get('model')
        qty = int(request.POST.get('qty', 1))
        codebar = request.POST.get('codebar', '')

        # Verificar que el SKU y la cantidad sean válidos
        if not sku or qty <= 0:
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

        # Obtener el último correlativo y superID para el producto
        last_unique_product = Uniqueproducts.objects.filter(product=producto).order_by('-correlative').first()
        current_correlative = (last_unique_product.correlative if last_unique_product else 0) + 1
        base_superid = last_unique_product.superid[:-len(str(last_unique_product.correlative))] if last_unique_product else sku

        # Crear el PDF con tamaño 10.2 cm x 5 cm
        page_width, page_height = 102 * mm, 50 * mm
        pdf = canvas.Canvas(absolute_file_path, pagesize=(page_width, page_height))

        super_ids = []
        for i in range(qty):
            # Calcular el superID y actualizar el correlativo
            super_id = f"{base_superid}{current_correlative}"
            super_ids.append(super_id)

            # Parte izquierda de la etiqueta
            x_sku_left, y_sku_left = 5 * mm, 35 * mm
            barcode_sku_left = code128.Code128(sku, barWidth=0.3 * mm, barHeight=9 * mm)
            barcode_sku_left.drawOn(pdf, x_sku_left, y_sku_left)
            pdf.setFont("Helvetica", 6)
            #pdf.drawString(x_sku_left, y_sku_left - 10, f"SKU: {sku}")

            # SuperID en vertical (rotado)
            pdf.saveState()
            pdf.rotate(90)
            x_superid_rotated_left, y_superid_rotated_left = 10 * mm, -2 * mm
            barcode_superid_left = code128.Code128(super_id, barWidth=0.4 * mm, barHeight=9 * mm)
            barcode_superid_left.drawOn(pdf, y_superid_rotated_left, -x_superid_rotated_left)
            pdf.restoreState()

            # Texto debajo del SuperID
            pdf.setFont("Helvetica", 6)
            #pdf.drawString(10 * mm, 5 * mm, f"SuperID: {super_id}")

            # Parte derecha de la etiqueta (si se requiere más de un elemento por página)
            if i % 2 == 1:
                x_sku_right, y_sku_right = 60 * mm, 35 * mm
                barcode_sku_right = code128.Code128(sku, barWidth=0.3 * mm, barHeight=9 * mm)
                barcode_sku_right.drawOn(pdf, x_sku_right, y_sku_right)
                pdf.setFont("Helvetica", 6)
                #pdf.drawString(x_sku_right, y_sku_right - 10, f"SKU: {sku}")

                pdf.saveState()
                pdf.rotate(90)
                x_superid_rotated_right, y_superid_rotated_right = 65 * mm, -2 * mm
                barcode_superid_right = code128.Code128(super_id, barWidth=0.4 * mm, barHeight=9 * mm)
                barcode_superid_right.drawOn(pdf, y_superid_rotated_right, -x_superid_rotated_right)
                pdf.restoreState()
                #pdf.drawString(60 * mm, 5 * mm, f"SuperID: {super_id}")

            # Guardar el nuevo UniqueProduct
            Uniqueproducts.objects.create(
                product=producto,
                superid=super_id,
                correlative=current_correlative,
                state=0,
                cost=producto.lastcost,
                locationname="Almacen",
                observation="Etiqueta generada automáticamente"
            )

            # Incrementar el correlativo para el siguiente
            current_correlative += 1

            # Añadir una nueva página solo si es necesario (después de imprimir ambos productos en la página actual)
            if i % 2 == 1 and i < qty - 1:
                pdf.showPage()

        pdf.save()

       # Llamar a `registrar_recepcion_stock` con `sku` y `qty`
        response_stock = registrar_recepcion_stock(request, sku, qty)

        # Verificar el estado de la respuesta para mostrar en el mensaje final
        if response_stock.status_code == 200:
            msg_stock = "Stock registrado en Bsale con éxito."
        else:
            msg_stock = f"Error al registrar stock en Bsale: {response_stock.json().get('msg', 'Error desconocido')}"

        # Devolver la ruta del archivo creada y un mensaje de éxito
        # Devolver la URL del archivo creada, superid, y el estado de la recepción de stock
        pdf_url = os.path.join(settings.MEDIA_URL, relative_file_path)
        return JsonResponse({
            'urlPdf': pdf_url,
            'superid': super_ids,
            'sku': sku,
            'msg_stock': msg_stock
        })

    return JsonResponse({'error': 'Método no permitido.'}, status=405)

from tqdm import tqdm
from django.db.models import Count
import sys
CHUNK_SIZE = 50  # Número de elementos por solicitud


@csrf_exempt
def comparar_stock_bsale(request):
    # URL base de Bsale y headers para la solicitud
    bsale_url = f'{BSALE_API_URL}/stocks.json'
    headers = {
        'access_token': BSALE_TOKEN
    }

    print("| Inicio del proceso de comparación de stock entre Bsale y el inventario local.")

    # Obtener todos los productos locales con sus idERP y currentstock
    print("| Obteniendo datos de productos locales con stock actual...")
    productos_locales = Products.objects.values('sku', 'iderp', 'currentstock')

    # Crear un diccionario de productos locales por idERP para acceso rápido
    productos_local_dict = {producto['iderp']: producto for producto in productos_locales}
    print(f"| Total de productos locales obtenidos: {len(productos_local_dict)}")

    # Inicialización para el progreso
    total_items = 0
    processed_items = 0

    next_url = bsale_url
    diferencias = []

    print("| Iniciando obtención de datos de Bsale...")

    while next_url:
        response = requests.get(next_url, headers=headers)
        if response.status_code != 200:
            print(f"Error al obtener datos de Bsale: {response.status_code} - {response.text}")
            return JsonResponse({'error': 'Error al obtener datos de Bsale'}, status=response.status_code)
        
        data = response.json()
        items = data.get('items', [])
        total_items += len(items)  # Actualizar el total de productos

        for item in items:
            bsale_id = item['id']
            bsale_stock = item['quantity']
            iderp = item['variant']['id']  # Este es el ID que corresponde al idERP local
            
            # Buscar el producto local por idERP
            producto_local = productos_local_dict.get(iderp)

            if producto_local:
                # Comparar stock de Bsale con el stock local
                resultado = {
                    "sku": producto_local['sku'],
                    "iderp": iderp,
                    "stock_local": producto_local['currentstock'],
                    "stock_bsale": bsale_stock,
                    "diferencia": bsale_stock - producto_local['currentstock']
                }
            else:
                # Producto no encontrado en local
                resultado = {
                    "sku": "0",
                    "iderp": iderp,
                    "stock_local": 0,
                    "stock_bsale": bsale_stock,
                    "diferencia": None
                }

            # Añadir resultado a la lista de diferencias y print detallado
            diferencias.append(resultado)
            print(f"| Comparación - SKU: {resultado['sku']}, IDERP: {resultado['iderp']}, "
                  f"Stock Local: {resultado['stock_local']}, Stock Bsale: {resultado['stock_bsale']}, "
                  f"Diferencia: {resultado['diferencia']}")

            # Actualizar y mostrar barra de progreso
            processed_items += 1
            progress = (processed_items / total_items) * 100
            sys.stdout.write(f"\r| Progreso: [{processed_items}/{total_items}] {progress:.2f}% completado")
            sys.stdout.flush()

        # Continuar con la siguiente página de Bsale
        next_url = data.get('next')
        print("\n| Página siguiente de Bsale cargada." if next_url else "\n| No hay más páginas en Bsale.")

    print(f"\n| Comparación completada. Total de productos comparados: {len(diferencias)}")

    return JsonResponse({'diferencias': diferencias})

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
                'access_token': BSALE_TOKEN,
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

