# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


import uuid

class Usuario(models.Model):
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('VENTAS', 'Ventas'),
        ('BODEGA', 'Bodega'),
        ('SADMIN','SuperAdmin')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True,blank=True)  # Relación con el modelo User de Django
    nombres_apellidos = models.CharField(max_length=255, blank=True, null=True)
    rut = models.CharField(max_length=12, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    correo = models.EmailField(unique=True,null=True,blank=True)  # Correo único
    clave = models.CharField(max_length=100, default='40emmett90')  # Clave por defecto
    rol = models.CharField(max_length=10, choices=ROLES, default='VENTAS')  # Rol de usuario

    def __str__(self):
        return f"{self.nombres_apellidos} ({self.rol})"




class Categoryserp(models.Model):
    namecategory = models.CharField(db_column='nameCategory', max_length=45, blank=True, null=True)  # Field name made lowercase.
    parentcategoryid = models.IntegerField(db_column='parentCategoryId', blank=True, null=True)  # Field name made lowercase.
    childrencategoryid = models.IntegerField(db_column='childrenCategoryId', blank=True, null=True)  # Field name made lowercase.
    iderp = models.IntegerField(db_column='idERP', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'categorysERP'


class Productconfig(models.Model):
    lastid = models.IntegerField(db_column='lastID', blank=True, null=True)  # Field name made lowercase.
    category = models.CharField(max_length=50, blank=True, null=True)
    prefixed = models.CharField(max_length=4, blank=True, null=True)
    categoryid = models.IntegerField(db_column='categoryID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'productConfig'


class Products(models.Model):
    sku = models.CharField(max_length=45, blank=True, null=True)
    nameproduct = models.CharField(max_length=250, blank=True, null=True)  # Field name made lowercase.
    prefixed = models.CharField(max_length=500, blank=True, null=True)
    brands = models.CharField(max_length=100, blank=True, null=True)
    codebar = models.CharField(max_length=45, blank=True, null=True)
    codebar2 = models.CharField(max_length=45, blank=True, null=True)
    codebar3 = models.CharField(max_length=45, blank=True, null=True)
    iderp = models.CharField(db_column='idERP', max_length=45, blank=True, null=True)  # Field name made lowercase.
    codsupplier = models.CharField(db_column='codSupplier', max_length=45, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(max_length=500, blank=True, null=True)
    lastcost = models.IntegerField(db_column='lastCost', blank=True, null=True)  # Field name made lowercase.
    latestreplenishment = models.DateTimeField(db_column='latestReplenishment', blank=True, null=True)  # Field name made lowercase.
    lastprice = models.IntegerField(db_column='lastPrice', blank=True, null=True)  # Field name made lowercase.
    typeprice = models.IntegerField(db_column='typePrice', blank=True, null=True)  # Field name made lowercase.
    currentstock = models.IntegerField(db_column='currentStock', blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateField(db_column='createDate', blank=True, null=True)  # Field name made lowercase.
    imgthumbs = models.CharField(db_column='imgThumbs', max_length=500, blank=True, null=True)  # Field name made lowercase.
    idmelimain = models.CharField(db_column='IDMELIMAIN', max_length=100, blank=True, null=True)  # Field name made lowercase.
    idproduct = models.IntegerField(db_column='idProduct', blank=True, null=True)  # Field name made lowercase.
    meliprice_s1 = models.IntegerField(db_column='meliPrice_s1', blank=True, null=True)  # Field name made lowercase.
    uniquecodebar = models.BooleanField(default=False, blank=True, null=True)  # Nuevo campo
    alto = models.IntegerField(blank=True, null=True) 
    largo = models.IntegerField(blank=True, null=True)  # Field name made lowercase.
    profundidad = models.IntegerField(blank=True, null=True)  # Field name made lowercase.
    peso = models.IntegerField(blank=True, null=True)  # Field name made lowercase.

     
     
    class Meta:
        db_table = 'products'


class Productscost(models.Model):
    sku = models.CharField(max_length=45, blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    purchasedate = models.DateField(db_column='purchaseDate', blank=True, null=True)  # Field name made lowercase.
    idsupplier = models.IntegerField(db_column='idSupplier', blank=True, null=True)  # Field name made lowercase.

    class Meta:
         db_table = 'productsCost'


class Productsprices(models.Model):
    sku = models.CharField(max_length=45, blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    offerprice = models.IntegerField(db_column='offerPrice', blank=True, null=True)  # Field name made lowercase.
    manualprice = models.IntegerField(db_column='manualPrice', blank=True, null=True)  # Field name made lowercase.
    channel = models.IntegerField(blank=True, null=True)
    effectivedate = models.DateField(db_column='effectiveDate', blank=True, null=True)  # Field name made lowercase.
    effectivedatetime = models.DateTimeField(db_column='effectiveDateTime', blank=True, null=True)  # Field name made lowercase.
    manager = models.CharField(max_length=50, blank=True, null=True)
    idplist = models.IntegerField(db_column='idPlist', blank=True, null=True)  # Field name made lowercase.
    idvariantplist = models.IntegerField(db_column='idVariantPlist', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'productsPrices'


class Purchase(models.Model):
    supplier = models.CharField(max_length=45, blank=True, null=True)
    suppliername = models.CharField(db_column='supplierName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    typedoc = models.IntegerField(db_column='typeDoc', blank=True, null=True)  # Field name made lowercase.
    number = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    observation = models.CharField(max_length=45, blank=True, null=True)
    dateadd = models.DateField(db_column='dateAdd', blank=True, null=True)  # Field name made lowercase.
    dateproccess = models.DateField(db_column='dateProccess', blank=True, null=True)  # Field name made lowercase.
    idpurchase = models.CharField(db_column='idPurchase', max_length=100, blank=True, null=True)  # Field name made lowercase.
    subtotal = models.IntegerField(blank=True, null=True)
    urljson = models.CharField(db_column='urlJson', max_length=500, blank=True, null=True)  # Field name made lowercase.
    urlimg = models.CharField(db_column='urlImg', max_length=500, blank=True, null=True)  # Field name made lowercase.
    printstatus = models.IntegerField(db_column='printStatus', blank=True, null=True)  # Field name made lowercase.
    dateprint = models.DateField(db_column='datePrint', blank=True, null=True)  # Field name made lowercase.
    iddocument = models.CharField(db_column='idDocument', max_length=45, blank=True, null=True)  # Field name made lowercase.
    subtotal = models.FloatField(default=0)  # Subtotal sin descuento
    subtotal_with_discount = models.FloatField(default=0)
    class Meta:
        db_table = 'purchase'




class Sectoroffice(models.Model):
    idsectoroffice = models.AutoField(db_column='idSectorOffice', primary_key=True)  # Field name made lowercase.
    idoffice = models.IntegerField(db_column='idOffice')  # Field name made lowercase.
    iduserresponsible = models.IntegerField(db_column='idUserResponsible', blank=True, null=True)  # Field name made lowercase.
    zone = models.CharField(max_length=5, blank=True, null=True)
    floor = models.IntegerField(blank=True, null=True)
    section = models.IntegerField(blank=True, null=True)
    namesector = models.CharField(db_column='nameSector', max_length=45, blank=True, null=True)  # Field name made lowercase.
    picturearea = models.CharField(db_column='pictureArea', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    diagramarea = models.CharField(db_column='diagramArea', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(max_length=500, blank=True, null=True)
    pdfbarcode = models.CharField(db_column='pdfBarcode', max_length=500, blank=True, null=True)  # Field name made lowercase.
    state = models.IntegerField(blank=True, null=True)
    namedescriptive = models.CharField(db_column='nameDescriptive', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'sectorOffice'


class Supplier(models.Model):
    namesupplier = models.CharField(db_column='nameSupplier', max_length=45, blank=True, null=True)  # Field name made lowercase.
    rutsupplier = models.CharField(db_column='rutSupplier', max_length=45, blank=True, null=True)  # Field name made lowercase.
    alias = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
         db_table = 'supplier'


class Uniqueproducts(models.Model):
    product = models.ForeignKey(Products, related_name='unique_products', on_delete=models.CASCADE, db_column='idProduct')  # Cambiado a ForeignKey
    superid = models.CharField(db_column='superID', max_length=45, blank=True, null=True)
    locationname = models.CharField(db_column='locationName', max_length=45, blank=True, null=True)
    correlative = models.IntegerField(blank=True, null=True)
    printlabel = models.CharField(db_column='printLabel', blank=True, null=True,max_length=255)  # Field name made lowercase.
    state = models.IntegerField(blank=True, null=True)
    cost = models.IntegerField(blank=True, null=True)
    soldvalue = models.IntegerField(db_column='soldValue', blank=True, null=True)  # Field name made lowercase.
    datelastinventory = models.DateTimeField(db_column='dateLastInventory', blank=True, null=True)  # Field name made lowercase.
    observation = models.CharField(max_length=1000, blank=True, null=True)
    location = models.IntegerField(blank=True, null=True)
    typedocincome = models.IntegerField(db_column='typeDocIncome', blank=True, null=True)  # Field name made lowercase.
    ndocincome = models.IntegerField(db_column='nDocIncome', blank=True, null=True)  # Field name made lowercase.
    typedocout = models.IntegerField(db_column='typeDocOut', blank=True, null=True)  # Field name made lowercase.
    ndocout = models.IntegerField(db_column='nDocOut', blank=True, null=True)  # Field name made lowercase.
    dateadd = models.DateTimeField(db_column='dateAdd', blank=True, null=True)  # Field name made lowercase.
    iddocumentincome = models.IntegerField(db_column='idDocumentIncome', blank=True, null=True)  # Field name made lowercase.
    ncompany = models.IntegerField(blank=True, null=True)  # Field name made lowercase.

    class Meta:
         db_table = 'uniqueProducts'

        
class Bodega(models.Model):
    idoffice = models.IntegerField()  # Campo numérico
    idExternal = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    country = models.CharField(max_length=255)
    municipality = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255)
    postalCode = models.CharField(max_length=10, null=True, blank=True)
    isVirtual = models.BooleanField(default=False)
    costCenter = models.IntegerField(null=True, blank=True)
    state = models.IntegerField()
    hrefExternal = models.CharField(max_length=255, null=True, blank=True)  # Dejar vacío
    urlPhoto = models.CharField(max_length=255, null=True, blank=True)  # Dejar vacío
    emailStore = models.EmailField()
    token = models.CharField(max_length=255, null=True, blank=True)  # Dejar vacío

    def __str__(self):
        return self.name
    

class Dispatch(models.Model):
    sid = models.CharField(max_length=50)
    code = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    total_unit_value = models.FloatField()
    quantity = models.IntegerField()
    count = models.IntegerField(default=0)

class DynamicKey(models.Model):
    key = models.CharField(max_length=6, unique=True)
    expiration_time = models.DateTimeField()

    def is_valid(self):
        return timezone.now() <= self.expiration_time
    
#NUEVOS MODELOS
class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

