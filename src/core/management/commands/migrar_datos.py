# core/management/commands/migrar_datos.py
from django.core.management.base import BaseCommand
from core.models import Uniqueproducts, Products, NewUniqueProduct, NewProduct

class Command(BaseCommand):
    help = "Actualiza valores de 'Uniqueproducts' y 'Products' con datos de 'NewUniqueProduct' y 'NewProduct'"

    def handle(self, *args, **options):
        # Actualización de Uniqueproducts
        self.stdout.write("Actualizando valores de 'superid' y 'location' en Uniqueproducts...")

        new_unique_products = NewUniqueProduct.objects.using('new_db').all()

        for new_product in new_unique_products:
            Uniqueproducts.objects.update_or_create(
                product_id=new_product.idSectorOffice,
                defaults={
                    'superid': new_product.sID,
                    'location': new_product.idSectorOffice
                }
            )
        
        self.stdout.write(self.style.SUCCESS("Valores de 'Uniqueproducts' actualizados correctamente."))

        # Actualización de Products
        self.stdout.write("Actualizando valores en Products...")

        new_products = NewProduct.objects.using('new_db').all()

        for new_product in new_products:
            Products.objects.filter(sku=new_product.sku).update(
                nameProduct=new_product.nameProduct,
                codebar=new_product.codeBar,
                description=new_product.descriptionCommercial,
                idProduct=new_product.idProduct
            )
        
        self.stdout.write(self.style.SUCCESS("Valores de 'Products' actualizados correctamente."))
