from django.contrib import admin
from core.models import Usuario, Products, Supplier, Uniqueproducts,Purchase,Bodega,Sectoroffice

# Configuración del admin para el modelo Usuario
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('correo', 'nombres_apellidos', 'rut', 'telefono')  # Campos que se muestran en la lista
    search_fields = ('correo', 'nombres_apellidos', 'rut')  # Campos que se pueden buscar

# Configuración del admin para el modelo Products
@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nameproduct', 'brands', 'currentstock')  # Mostrar campos clave en Products
    search_fields = ('=sku', 'nameproduct', 'brands','=iderp')  # Agregar búsqueda para SKU, nombre del producto y marcas

# Configuración del admin para el modelo Supplier
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('namesupplier', 'rutsupplier', 'alias')  # Campos a mostrar en Supplier
    search_fields = ('namesupplier', 'rutsupplier', 'alias')  # Campos que se pueden buscar en Supplier

# Configuración del admin para el modelo Uniqueproducts
@admin.register(Uniqueproducts)
class UniqueproductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'superid', 'locationname', 'product')  # Mostrar ID, superid, ubicación y producto relacionado
    search_fields = ['id', 'superid', 'locationname']  # Búsqueda por ID, superid y ubicación

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'idpurchase', 'supplier', 'subtotal', 'status', 'dateadd')  # Muestra los campos que quieras
    search_fields = ('idpurchase', 'supplier')  # Agrega un campo de búsqueda
    list_filter = ('status',)  # Puedes agregar filtros en el panel de admin, como por estado

admin.site.register(Purchase, PurchaseAdmin)

admin.site.register(Bodega)
admin.site.register(Sectoroffice)


