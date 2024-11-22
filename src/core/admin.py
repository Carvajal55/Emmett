from django.contrib import admin
from core.models import Usuario, Products, Supplier, Uniqueproducts, Purchase, Bodega, Sectoroffice,Brand,Category
from openpyxl import Workbook
from django.http import HttpResponse



# Configuración del admin para el modelo Products con exportación a Excel
@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nameproduct', 'brands', 'currentstock','uniquecodebar')  # Mostrar campos clave en Products
    search_fields = ('sku', 'nameproduct', 'brands', '=iderp')  # Agregar búsqueda para SKU, nombre del producto y marcas
    actions = ['export_products_to_excel']  # Añadir la acción de exportar a Excel

    def export_products_to_excel(self, request, queryset):
        # Crear un nuevo libro de trabajo y hoja
        wb = Workbook()
        ws = wb.active
        ws.title = "Products Data"

        # Obtener todos los campos del modelo Products
        field_names = [field.name for field in Products._meta.fields]

        # Escribir los nombres de los campos en la primera fila
        ws.append(field_names)

        # Escribir los datos
        for obj in queryset:
            row = [getattr(obj, field) for field in field_names]
            ws.append(row)

        # Configurar la respuesta HTTP para devolver el archivo Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="products_data.xlsx"'
        wb.save(response)
        return response

    export_products_to_excel.short_description = "Exportar Products a Excel"

# Configuración del admin para el modelo Supplier
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('namesupplier', 'rutsupplier', 'alias')  # Campos a mostrar en Supplier
    search_fields = ('namesupplier', 'rutsupplier', 'alias')  # Campos que se pueden buscar en Supplier

# Configuración del admin para el modelo Uniqueproducts
@admin.register(Uniqueproducts)
class UniqueproductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'superid', 'locationname', 'product') 
    search_fields = ('id', 'superid', 'product__sku', 'product__nameproduct')  # Campos específicos del modelo relacionado


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('iddocument','number', 'idpurchase')
    search_fields = ('id','iddocument','number', 'idpurchase')

@admin.register(Bodega)
class Bodega(admin.ModelAdmin):
    list_display = ('idoffice','name')
    search_fields = ('idoffice','name')

@admin.register(Sectoroffice)
class Sectoroffice(admin.ModelAdmin):
    list_display = ('idsectoroffice','idoffice','zone','floor','section','namesector')
    search_fields = ('idsectoroffice','idoffice','zone','floor','section','namesector')

class UsuarioAdmin(admin.ModelAdmin):
    # Muestra el correo del usuario asociado usando un método
    list_display = ('nombres_apellidos', 'rol')
    ordering = ('user__email',)  # Ordena por correo del usuario

   

admin.site.register(Brand)

admin.site.register(Category)


admin.site.register(Usuario, UsuarioAdmin)