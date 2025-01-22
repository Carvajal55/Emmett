from django.contrib import admin
from core.models import *
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

class CategoryserpAdmin(admin.ModelAdmin):
    list_display = ('namecategory', 'iderp')  # Muestra estas columnas en el listado
    search_fields = ('namecategory',)        # Habilita búsqueda por el campo namecategory

admin.site.register(Categoryserp, CategoryserpAdmin)


admin.site.register(Usuario, UsuarioAdmin)

# Personalización para el modelo InvoiceProductSuperID
class InvoiceProductSuperIDInline(admin.TabularInline):
    model = InvoiceProductSuperID
    extra = 0  # No añadir líneas adicionales por defecto
    fields = ('superid', 'dispatched')
    readonly_fields = ('superid',)
    can_delete = False  # Evitar eliminar desde el admin


# Personalización para el modelo InvoiceProduct
class InvoiceProductInline(admin.TabularInline):
    model = InvoiceProduct
    extra = 0
    fields = ('product_sku', 'total_quantity', 'dispatched_quantity', 'is_complete')
    readonly_fields = ('product_sku', 'total_quantity', 'dispatched_quantity', 'is_complete')
    inlines = [InvoiceProductSuperIDInline]  # Mostrar los SuperIDs asociados


# Configuración del modelo Invoice
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'document_type', 'document_number', 'dispatched', 'created_at', 'updated_at')
    list_filter = ('dispatched', 'document_type', 'created_at')
    search_fields = ('document_number',)
    inlines = [InvoiceProductInline]  # Mostrar productos asociados
    readonly_fields = ('created_at', 'updated_at')  # Campos de solo lectura


# Configuración del modelo InvoiceProduct
@admin.register(InvoiceProduct)
class InvoiceProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'invoice', 'product_sku', 'total_quantity', 'dispatched_quantity', 'is_complete')
    list_filter = ('is_complete',)
    search_fields = ('product_sku',)
    inlines = [InvoiceProductSuperIDInline]


# Configuración del modelo InvoiceProductSuperID
@admin.register(InvoiceProductSuperID)
class InvoiceProductSuperIDAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'superid', 'dispatched')
    list_filter = ('dispatched',)
    search_fields = ('superid',)