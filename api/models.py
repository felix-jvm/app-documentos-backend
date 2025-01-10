from django.db import models

class Procedimiento(models.Model):
    ID = models.AutoField(primary_key=True)
    Codigo = models.CharField(db_column='Codigo', max_length=500, blank=False, null=False)
    Objetivo = models.TextField(db_column='Objetivo', blank=False, null=False)
    Alcance = models.TextField(db_column='Alcance', blank=False, null=False)
    Diagrama_Flujo = models.BinaryField(db_column='Diagrama_Flujo', blank=True, null=True)
    deleted = models.BooleanField(db_column='deleted', default=False, blank=True, null=True)


    class Meta:
        managed = True
        db_table = 'Procedimiento'
                                                                           
class DocumentosReferencias(models.Model):        
   ID = models.AutoField(primary_key=True) 
   IDDocumento = models.IntegerField(db_column='IDDocumento', blank=True, null=True)
   IDProcedimiento = models.IntegerField(db_column='IDProcedimiento', blank=True, null=True)

   class Meta:
        managed = True
        db_table = 'DocumentosReferencias'   

class Documentos(models.Model):        
   ID = models.AutoField(primary_key=True) 
   Codigo = models.CharField(db_column='Codigo', max_length=50, blank=False, null=False)
   Descripcion = models.CharField(db_column='Descripcion', max_length=100, blank=True, null=True)
   Fecha = models.DateField(db_column='Fecha', auto_now_add=True, blank=True, null=True)
   Version = models.CharField(db_column='Version', max_length=500, blank=True, null=True)  
   IDTipoDocumento = models.IntegerField(db_column='IDTipoDocumento', blank=True, null=True)
   IDDepartamento = models.IntegerField(db_column='IDDepartamento', blank=True, null=True)      
   TipoDoc_Dep_Repr = models.CharField(db_column='TipoDoc_Dep_Repr', max_length=100, blank=True, null=True)

   class Meta:
        managed = True
        db_table = 'Documentos'

class Responsabilidades(models.Model):        
   ID = models.AutoField(primary_key=True) 
   IDProcedimiento = models.IntegerField(db_column='IDProcedimiento', blank=False, null=False)
   IDPuesto = models.IntegerField(db_column='IDPuesto', blank=False, null=False)
   Descripcion = models.CharField(db_column='Descripcion', max_length=500, blank=False, null=False)   

   class Meta:
        managed = True
        db_table = 'Responsabilidades'        

class Puestos(models.Model):        
   ID = models.AutoField(primary_key=True) 
   Descripcion = models.CharField(db_column='Descripcion', max_length=50, blank=False, null=False)
   UnidadNegocio = models.IntegerField(db_column='UnidadNegocio', blank=True, null=True)
   Actividad = models.IntegerField(db_column='Actividad', blank=True, null=True)

   class Meta:
        managed = True
        db_table = 'Puestos'        

class TerminologiasDef(models.Model):        
   ID = models.AutoField(primary_key=True) 
   IDProcedimiento = models.IntegerField(db_column='IDProcedimiento', blank=False, null=False)
   IDTermino = models.IntegerField(db_column='IDTermino', blank=False, null=False)
   Descripcion = models.CharField(db_column='Descripcion', max_length=500, blank=False, null=False)

   class Meta:
        managed = True
        db_table = 'TerminologiasDef'

class Termino(models.Model):        
   ID = models.AutoField(primary_key=True) 
   Descripcion = models.CharField(db_column='Descripcion', max_length=50, blank=False, null=False)
   DescripcionGeneral = models.CharField(db_column='DescripcionGeneral', max_length=500, blank=True, null=True)

   class Meta:
        managed = True
        db_table = 'Termino'        

class DescripcionesProcedimiento(models.Model):        
   ID = models.AutoField(primary_key=True) 
   Codigo = models.CharField(db_column='Codigo', max_length=50, default='NA', blank=True, null=True)
   IDProcedimiento = models.IntegerField(db_column='IDProcedimiento', blank=False, null=False)
   Descripcion = models.TextField(db_column='Descripcion')

   class Meta:
        managed = True
        db_table = 'DescripcionesProcedimiento'        

class SubDescripciones(models.Model):        
   ID = models.AutoField(primary_key=True) 
   Codigo = models.CharField(db_column='Codigo', max_length=50, default='NA', blank=True, null=True)
   IDDescripcion = models.IntegerField(db_column='IDDescripcion', blank=True, null=True)
   SubDescripcion = models.TextField(db_column='SubDescripcion')

   class Meta:
        managed = True
        db_table = 'SubDescripciones'        

class Anexos(models.Model):        
   ID = models.AutoField(primary_key=True) 
   Num = models.IntegerField(db_column='Num', blank=True, null=True)
   Nombre = models.CharField(db_column='Nombre', max_length=50, blank=True, null=True)   
   Codigo = models.CharField(db_column='Codigo', max_length=50, blank=True, null=True)
   IDProcedimiento = models.IntegerField(db_column='IDProcedimiento', blank=True, null=True)

   class Meta:
        managed = True
        db_table = 'Anexos'

class RevAprobacion(models.Model):        
   ID = models.AutoField(primary_key=True)
   IDProcedimiento = models.IntegerField(blank=False, null=False)    
   ElaboradoPor = models.CharField(db_column='ElaboradoPor', max_length=50, blank=True, null=True)
   FirmaElaborado = models.CharField(db_column='FirmaElaborado', max_length=50, blank=True, null=True)
   PuestoElaborado = models.CharField(db_column='PuestoElaborado', max_length=50, blank=True, null=True)   
   RevisadoPor = models.CharField(db_column='RevisadoPor', max_length=50, blank=True, null=True)
   FirmaRevisado = models.CharField(db_column='FirmaRevisado', max_length=50, blank=True, null=True)
   PuestoRevisado = models.CharField(db_column='PuestoRevisado', max_length=50, blank=True, null=True)
   AprobadoPor = models.CharField(db_column='AprobadoPor', max_length=50, blank=True, null=True)
   FirmaAprobado = models.CharField(db_column='FirmaAprobado', max_length=50, blank=True, null=True)
   PuestoAprobado = models.CharField(db_column='PuestoAprobado', max_length=50, blank=True, null=True)

   class Meta:
        managed = True
        db_table = 'RevAprobacion'        

class HistorialCambios(models.Model):        
   ID = models.AutoField(primary_key=True) 
   Fecha = models.DateField(auto_now_add=True)
   Version = models.CharField(db_column='Version', max_length=500, blank=True, null=True)   
   Descripcion = models.CharField(db_column='Descripcion', max_length=500, blank=True, null=True)
   IDProcedimiento = models.IntegerField(db_column='IDProcedimiento', blank=True, null=True)

   class Meta:
        managed = True
        db_table = 'HistorialCambios'

class TipoDocumento(models.Model):        
   ID = models.AutoField(primary_key=True)
   Descripcion = models.CharField(db_column='Descripcion', max_length=50, blank=True, null=True)   
   Codificacion = models.CharField(db_column='Codificacion', max_length=10, blank=True, null=True)

   class Meta:
        managed = True
        db_table = 'TipoDocumento'        

class Departamento(models.Model):        
   ID = models.AutoField(primary_key=True)
   Descripcion = models.CharField(db_column='Descripcion', max_length=50, blank=True, null=True)   
   Codigo = models.CharField(db_column='Codigo', max_length=10, blank=True, null=True)        

   class Meta:
        managed = True
        db_table = 'Departamento'

class Usuario(models.Model):
    ID = models.AutoField(primary_key=True)
    Nombre = models.CharField(db_column='Nombre', max_length=50, blank=False, null=False) 
    Contrasena = models.BinaryField(db_column='Contrasena', blank=False, null=False)
    Activo = models.BooleanField(db_column='Activo', default=True, blank=False, null=False)    
    PermisoNivel = models.IntegerField(db_column='PermisoNivel', blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'Usuario'    

class PermisoNivel(models.Model):
    ID = models.AutoField(primary_key=True)
    Nivel = models.IntegerField(db_column='Nivel', blank=False, null=False)
    Descripcion = models.CharField(db_column='Descripcion', max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'PermisoNivel'

class UsuarioCodigo(models.Model):
    ID = models.AutoField(primary_key=True)
    Codigo = models.CharField(db_column='Codigo', max_length=100, blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'UsuarioCodigo'        