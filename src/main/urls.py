"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
   
    path('', core_views.login_view, name="login_view"),
    
    path('dashboard', core_views.index, name="index"),

   # Ruta para la vista de creación de usuarios
    path('crear_usuario/', core_views.crear_usuario_view, name="crear_usuarios_view"),
    path('buscar_productos/', core_views.buscar_productos, name='buscar_productos'),  # URL que apunta al HTML
    path('recepciones_aceptadas/', core_views.recepciones_aceptadas, name='recepciones_aceptadas'),  # URL que apunta al HTML
    path('recepciones_pendientes/', core_views.recepciones_pendientes, name='recepciones_pendientes'),  # URL que apunta al HTML
    path('ingresar_documentos/', core_views.ingresar_documentos, name='ingresar_documentos'), 
    path('anadir_psector/', core_views.anadir_psector, name='anadir_psector'), # URL que apunta al HTML
    path('cuadrar_sector/', core_views.cuadrar_sector_view, name='cuadrar_sector'), # URL que apunta al HTML
    path('despacho/', core_views.despacho, name='despacho'),



    
    # Rutas para las APIs relacionadas con usuarios
    path('api/crear-usuario/', core_views.create_user, name="crear_usuario"),
    path('api/listar-usuarios/', core_views.list_users, name="listar_usuarios"),
    path('api/actualizar-usuario/<int:user_id>/', core_views.update_user, name="actualizar_usuario"),
    path('api/eliminar-usuario/<int:user_id>/', core_views.delete_user, name="eliminar_usuario"),
    #BUSCAR PRODUCTOS
    path('api/buscar-productos/', core_views.buscar_productosAPI, name='buscar_productosAPI'),
    path('api/producto-detalles/<int:product_id>/', core_views.producto_detalles, name='producto_detalles'),
    path('api/listar-bodegas/', core_views.listar_bodegas, name='crear_producto'),
    path('api/listar-compras/', core_views.listar_compras, name='listar_compras'),
    path('api/resumen-facturas/', core_views.resumen_factura, name='resumen_factura'),
    path('api/listar-facturas-pendientes/', core_views.listar_facturas_pendientes, name='listar_facturas_pendientes'),
    path('api/rechazar-factura/', core_views.rechazar_factura, name='rechazar_factura'),
    path('api/aprobar-factura/', core_views.aprobar_factura, name='aprobar_factura'),
    path('api/obtener_factura/', core_views.obtener_factura, name='obtener_factura'),
    path('factura/aprobar/<int:id>/', core_views.factura_aprobar_view, name='factura_aprobar'),
    #Imprimir etiquetas
    path('api/imprimir-etiqueta/', core_views.imprimir_etiqueta, name='imprimir_etiqueta'),
    #Ingresar Documentos
    path('api/create-supplier/', core_views.create_supplier, name='create_supplier'),
    path('api/create-product/', core_views.create_product, name='create_product'),
    path('api/generar-json/', core_views.generar_json, name='generar_json'),
    path('api/get-suppliers/', core_views.get_suppliers, name='get_suppliers'),
    path('api/get-products/', core_views.get_products, name='get_products'),
    path('api/add-purchase/', core_views.add_purchase, name='add_purchase'),
    path('api/get-product/', core_views.get_product_by_sku, name='get_product_by_sku'),
    path('api/load-draft/', core_views.load_draft, name='load_draft'),
    path('api/load-xml/', core_views.load_xml, name='load_xml'),
    path('api/get-document-lines/<int:document_id>/', core_views.get_document_lines, name='get_document_lines'),
    path('api/save-document-lines/', core_views.save_document_lines, name='save_document_lines'),
    path('api/actualizar_precio/', core_views.actualizar_precio, name='actualizar_precio'),

    # Sectorizar 
    path('api/consultar-productos-sector/', core_views.consultar_productos_sector, name='consultar_productos_sector'),
    path('api/buscar-productos-por-sector/', core_views.buscar_productos_por_sector, name='buscar_productos_por_sector'),
    path('api/buscar-productos-sector/', core_views.search_products_by_sector, name='buscar_productos_sector'),
    path('api/anadir-producto-sector/', core_views.add_product_to_sector, name='anadir_producto_al_sector'),  
    path('api/buscar-producto-superid/', core_views.buscar_producto_superid, name='buscar_producto_superid'),
    path('api/mover-productos/', core_views.move_products_to_sector, name='mover_productos'),
    path('api/anadir-producto-sector/', core_views.anadir_producto_sector, name='anadir_producto_sector'),
    #Cuadrar Sector
    path('api/cuadrar-productos/', core_views.cuadrar_productos, name='cuadrar_productos'),

    #conectar conbsale
    path('api/sincronizar-producto/<str:sku>/', core_views.sincronizar_producto, name='sincronizar_producto_por_sku'),
    path('api/recepcion-stock/<str:sku>/', core_views.registrar_recepcion_stock, name='registrar_recepcion_stock'),

    #Despacho
   path('api/current-dispatch/', core_views.current_dispatch, name='current_dispatch'),
   path('api/details-document/', core_views.details_document, name='details_document'),
   #path('api/dispatch-product/', core_views.dispatch_product, name='dispatch_product'),
   path('api/dispatch-consumption/', core_views.dispatch_consumption, name='dispatch_consumption'),
   path('api/consult-bsale-document/', core_views.get_unique_document, name='get_unique_document'),
   path('api/validate-superid/', core_views.validate_superid_simplified, name='validate_superid'),
   path('api/dispatch-product/', core_views.validate_superid_simplified, name='dispatch_product'),

   path('api/comparar-stock-bsale/', core_views.comparar_stock_bsale, name='comparar_stock_bsale'),
   path('api/actualizar-stock-local/', core_views.actualizar_stock_local, name='actualizar_stock_local'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
