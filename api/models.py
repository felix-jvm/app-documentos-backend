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
   UnidadNegocio = models.CharField(db_column='UnidadNegocio', max_length=10, blank=True, null=True)
   Actividad = models.CharField(db_column='Actividad',max_length=10, blank=True, null=True)

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


#############################################DESCRIP_PUESTO###################################


class DescripcionPuesto(models.Model):
    ID = models.AutoField(primary_key=True)
    CodigoPuesto = models.IntegerField(db_column='CodigoPuesto', blank=True, null=True)
    TituloPuesto = models.IntegerField(db_column='TituloPuesto', blank=True, null=True)
    ReportaA = models.IntegerField(db_column='ReportaA', blank=True, null=True)
    Departamento = models.IntegerField(db_column='Departamento', blank=True, null=True)
    CodigoDepartamento = models.CharField(db_column='CodigoDepartamento', max_length=50, blank=True, null=True)
    Ubicacion = models.CharField(db_column='Ubicacion', max_length=50, blank=True, null=True)
    ObjetivoPuesto = models.CharField(db_column='ObjetivoPuesto', max_length=500, blank=True, null=True)
    OrganigramaDescri = models.CharField(db_column='OrganigramaDescri', max_length=500, blank=True, null=True)
    OrganigramaFile = models.BinaryField(db_column='OrganigramaFile', blank=True, null=True)
    CompeteActituDescr = models.CharField(db_column='CompeteActituDescr', max_length=500, blank=True, null=True)
    CompeteTecniIndisDescr = models.CharField(db_column='CompeteTecniIndisDescr', max_length=500, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'DescripcionPuesto'

class FuncionesPuesto(models.Model):
    ID = models.AutoField(primary_key=True)
    FuncionesDescri = models.CharField(db_column='FuncionesDescri', max_length=500, blank=True, null=True)
    ResultadoFinalDescri = models.CharField(db_column='ResultadoFinalDescri', max_length=500, blank=True, null=True)
    DescripcionPuesto = models.IntegerField(db_column='DescripcionPuesto', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'FuncionesPuesto'

class ActividadesPeriodicasPuesto(models.Model):
    ID = models.AutoField(primary_key=True)
    ActividadesDescri = models.CharField(db_column='ActividadesDescri', max_length=500, blank=True, null=True)
    ResultadoFinalDescri = models.CharField(db_column='ResultadoFinalDescri', max_length=500, blank=True, null=True)
    DescripcionPuesto = models.IntegerField(db_column='DescripcionPuesto', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ActividadesPeriodicasPuesto'

class RelacionesInternas(models.Model):
    ID = models.AutoField(primary_key=True)
    Puesto = models.IntegerField(db_column='Puesto', blank=True, null=True)
    Descri = models.CharField(db_column='Descri', max_length=500, blank=True, null=True)
    DescripcionPuesto = models.IntegerField(db_column='DescripcionPuesto', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'RelacionesInternas'        

class RelacionesExternas(models.Model):
    ID = models.AutoField(primary_key=True)
    Puesto = models.IntegerField(db_column='Puesto', blank=True, null=True)
    Descri = models.CharField(db_column='Descri', max_length=500, blank=True, null=True)
    DescripcionPuesto = models.IntegerField(db_column='DescripcionPuesto', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'RelacionesExternas'        

class ResponRecurYMateriales(models.Model):
    ID = models.AutoField(primary_key=True)
    Descri = models.CharField(db_column='Descri', max_length=500, blank=True, null=True)
    DescripcionPuesto = models.IntegerField(db_column='DescripcionPuesto', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ResponRecurYMateriales'        

class DecisionesSinAprobacion(models.Model):
    ID = models.AutoField(primary_key=True)
    Descri = models.CharField(db_column='Descri', max_length=500, blank=True, null=True)
    DescripcionPuesto = models.IntegerField(db_column='DescripcionPuesto', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'DecisionesSinAprobacion'

class GradoAutoridadDecisiones(models.Model):
    ID = models.AutoField(primary_key=True)
    Descri = models.CharField(db_column='Descri', max_length=500, blank=True, null=True)
    DescripcionPuesto = models.IntegerField(db_column='DescripcionPuesto', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'GradoAutoridadDecisiones'

class FormacionAcademica(models.Model):
    ID = models.AutoField(primary_key=True)
    Descri = models.CharField(db_column='Descri', max_length=300, blank=True, null=True)
    Indispensable = models.BooleanField(db_column='Indispensable', default=False, blank=True, null=True)  
    Deseable = models.BooleanField(db_column='Deseable', default=False, blank=True, null=True)
    DescripcionPuesto = models.IntegerField(db_column='DescripcionPuesto', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'FormacionAcademica'

class Idiomas(models.Model):
    ID = models.AutoField(primary_key=True)
    Descri = models.CharField(db_column='Descri', max_length=300, blank=True, null=True)
    DescripcionPuesto = models.IntegerField(db_column='DescripcionPuesto', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Idiomas'        

class IdiomasHabilidades(models.Model):
    ID = models.AutoField(primary_key=True)
    Descri = models.CharField(db_column='Descri', max_length=50, blank=True, null=True)
    Grado =  models.CharField(db_column='Grado', max_length=10, blank=True, null=True)
    Indispensable = models.BooleanField(db_column='Indispensable', default=False, blank=True, null=True)  
    Deseable = models.BooleanField(db_column='Deseable', default=False, blank=True, null=True)
    Idiomas = models.IntegerField(db_column='Idiomas', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'IdiomasHabilidades'

class Computacion(models.Model):
    ID = models.AutoField(primary_key=True)
    Descri = models.CharField(db_column='Descri', max_length=300, blank=True, null=True)
    Grado =  models.CharField(db_column='Grado', max_length=10, blank=True, null=True)
    Indispensable = models.BooleanField(db_column='Indispensable', default=False, blank=True, null=True)  
    Deseable = models.BooleanField(db_column='Deseable', default=False, blank=True, null=True)
    DescripcionPuesto = models.IntegerField(db_column='DescripcionPuesto', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Computacion'        

class ExperienciaIdeal(models.Model):
    ID = models.AutoField(primary_key=True)
    Descri = models.CharField(db_column='Descri', max_length=300, blank=True, null=True)
    Indispensable = models.BooleanField(db_column='Indispensable', default=False, blank=True, null=True)  
    Deseable = models.BooleanField(db_column='Deseable', default=False, blank=True, null=True)
    DescripcionPuesto = models.IntegerField(db_column='DescripcionPuesto', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ExperienciaIdeal'        

class CompeteActituLista(models.Model):
    ID = models.AutoField(primary_key=True)
    Descri = models.CharField(db_column='Descri', max_length=300, blank=True, null=True)
    Indispensable = models.BooleanField(db_column='Indispensable', default=False, blank=True, null=True)  
    Deseable = models.BooleanField(db_column='Deseable', default=False, blank=True, null=True)
    DescripcionPuesto = models.IntegerField(db_column='DescripcionPuesto', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'CompeteActituLista'

class CompeteTecniIndisLista(models.Model):
    ID = models.AutoField(primary_key=True)
    Descri = models.CharField(db_column='Descri', max_length=300, blank=True, null=True)
    BuenDominio = models.BooleanField(db_column='BuenDominio', default=False, blank=True, null=True)  
    DominioBasico = models.BooleanField(db_column='DominioBasico', default=False, blank=True, null=True)
    DescripcionPuesto = models.IntegerField(db_column='DescripcionPuesto', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'CompeteTecniIndisLista'    

class CondicionesFisicas(models.Model):
    ID = models.AutoField(primary_key=True)
    Descri = models.CharField(db_column='Descri', max_length=300, blank=True, null=True)
    DescripcionPuesto = models.IntegerField(db_column='DescripcionPuesto', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'CondicionesFisicas'

class Riesgos(models.Model):
    ID = models.AutoField(primary_key=True)
    Descri = models.CharField(db_column='Descri', max_length=300, blank=True, null=True)
    DescripcionPuesto = models.IntegerField(db_column='DescripcionPuesto', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Riesgos'


#############################################MANUAL####################################         


class Manual(models.Model):
    ID = models.AutoField(primary_key=True)
    CodigoManual = models.IntegerField(db_column='CodigoManual', blank=True, null=True)
    ObjetivoGeneralManualDescri = models.CharField(db_column='ObjetivoGeneralManualDescri', max_length=500, blank=True, null=True)
    ObjetivoEspecificoManualDescri = models.CharField(db_column='ObjetivoEspecificoManualDescri', max_length=500, blank=True, null=True)
    AlcanceDescri = models.CharField(db_column='AlcanceDescri', max_length=300, blank=True, null=True)
    ObjetivoGeneralUnidadNegocio = models.CharField(db_column='ObjetivoGeneralUnidadNegocio', max_length=500, blank=True, null=True)
    MapaProcesoDescri = models.CharField(db_column='MapaProcesoDescri', max_length=500, blank=True, null=True)
    MapaProcesoFile = models.BinaryField(db_column='MapaProcesoFile', blank=True, null=True)
    EstructuraProcesoDescri = models.CharField(db_column='EstructuraProcesoDescri', max_length=500, blank=True, null=True)
    EstructuraProcesoFile = models.BinaryField(db_column='EstructuraProcesoFile', blank=True, null=True)
    OrganigramaEstructuralDescri = models.CharField(db_column='OrganigramaEstructuralDescri', max_length=500, blank=True, null=True)
    OrganigramaEstructuralFile = models.BinaryField(db_column='OrganigramaEstructuralFile', blank=True, null=True)
    OrganigramaFuncionalDescri = models.CharField(db_column='OrganigramaFuncionalDescri', max_length=500, blank=True, null=True)
    OrganigramaFuncionalFile = models.BinaryField(db_column='OrganigramaFuncionalFile', blank=True, null=True)
    PresupuestoDescri = models.CharField(db_column='PresupuestoDescri', max_length=800, blank=True, null=True)
    PresupuestoSecondDescri = models.CharField(db_column='PresupuestoSecondDescri', max_length=800, blank=True, null=True)
    RendicionCuentaDescri = models.CharField(db_column='RendicionCuentaDescri', max_length=800, blank=True, null=True)
    IndicadorProcesoGestion = models.BinaryField(db_column='IndicadorProcesoGestion', blank=True, null=True)
    IndicadorProcesoGestionRiesgoDescri = models.CharField(db_column='IndicadorProcesoGestionRiesgoDescri', max_length=800, blank=True, null=True)
    IndicadorProcesoGestionRiesgoFile = models.BinaryField(db_column='IndicadorProcesoGestionRiesgoFile', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Manual'    

class ObjetivoEspecificoManualLista(models.Model):
    ID = models.AutoField(primary_key=True)
    Descri = models.CharField(db_column='Descri', max_length=500, blank=True, null=True)
    Manual = models.IntegerField(db_column='Manual', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ObjetivoEspecificoManualLista'

class MarcoLegal(models.Model):
    ID = models.AutoField(primary_key=True)
    Descri = models.CharField(db_column='Descri', max_length=500, blank=True, null=True)
    Manual = models.IntegerField(db_column='Manual', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'MarcoLegal'        

class ObjetivoEspecificoUnidadNegocio(models.Model):
    ID = models.AutoField(primary_key=True)
    Descri = models.CharField(db_column='Descri', max_length=500, blank=True, null=True)
    Manual = models.IntegerField(db_column='Manual', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ObjetivoEspecificoUnidadNegocio'      

class DescripcionPuestoManual(models.Model):
    ID = models.AutoField(primary_key=True)
    Codigo = models.CharField(db_column='Codigo', max_length=200, blank=True, null=True)    
    Descri = models.CharField(db_column='Descri', max_length=500, blank=True, null=True)
    Manual = models.IntegerField(db_column='Manual', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'DescripcionPuestoManual'

class ClienteInterno(models.Model):
    ID = models.AutoField(primary_key=True)
    Cliente = models.CharField(db_column='Cliente', max_length=200, blank=True, null=True)    
    Necesidad = models.CharField(db_column='Necesidad', max_length=800, blank=True, null=True)
    Expectativa = models.CharField(db_column='Expectativa', max_length=800, blank=True, null=True)
    Manual = models.IntegerField(db_column='Manual', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ClienteInterno'

class ClienteExterno(models.Model):
    ID = models.AutoField(primary_key=True)
    Cliente = models.CharField(db_column='Cliente', max_length=200, blank=True, null=True)    
    Necesidad = models.CharField(db_column='Necesidad', max_length=800, blank=True, null=True)
    Expectativa = models.CharField(db_column='Expectativa', max_length=800, blank=True, null=True)
    Manual = models.IntegerField(db_column='Manual', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ClienteExterno'        

class ComunicacionInterna(models.Model):
    ID = models.AutoField(primary_key=True)
    TipoComunicacion = models.CharField(db_column='TipoComunicacion', max_length=500, blank=True, null=True)    
    Periodicidad = models.CharField(db_column='Periodicidad', max_length=500, blank=True, null=True)
    Manual = models.IntegerField(db_column='Manual', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ComunicacionInterna'        

class ComunicacionExterna(models.Model):
    ID = models.AutoField(primary_key=True)
    TipoComunicacion = models.CharField(db_column='TipoComunicacion', max_length=500, blank=True, null=True)    
    Periodicidad = models.CharField(db_column='Periodicidad', max_length=500, blank=True, null=True)
    Manual = models.IntegerField(db_column='Manual', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ComunicacionExterna'        

class CategorizacionGasto(models.Model):
    ID = models.AutoField(primary_key=True)
    Descri = models.CharField(db_column='Descri', max_length=500, blank=True, null=True)    
    Sigla = models.CharField(db_column='Sigla', max_length=50, blank=True, null=True)
    Manual = models.IntegerField(db_column='Manual', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'CategorizacionGasto'       

class CategorizacionGastoPartida(models.Model):
    ID = models.AutoField(primary_key=True)
    Descri = models.CharField(db_column='Descri', max_length=500, blank=True, null=True)    
    Sigla = models.CharField(db_column='Sigla', max_length=50, blank=True, null=True)
    CategorizacionGasto = models.IntegerField(db_column='CategorizacionGasto', blank=True, null=True)
    Manual = models.IntegerField(db_column='Manual', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'CategorizacionGastoPartida'         

class BoundManual(models.Model):
    ID = models.AutoField(primary_key=True)
    Codigo = models.CharField(db_column='Codigo', max_length=200, blank=True, null=True)    
    Descri = models.CharField(db_column='Descri', max_length=500, blank=True, null=True)
    Manual = models.IntegerField(db_column='Manual', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'BoundManual'        

class BoundProcedimiento(models.Model):
    ID = models.AutoField(primary_key=True)
    Codigo = models.CharField(db_column='Codigo', max_length=200, blank=True, null=True)    
    Descri = models.CharField(db_column='Descri', max_length=500, blank=True, null=True)
    Manual = models.IntegerField(db_column='Manual', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'BoundProcedimiento'        

class RendicionCuentaLista(models.Model):
    ID = models.AutoField(primary_key=True)    
    Descri = models.CharField(db_column='Descri', max_length=500, blank=True, null=True)
    Manual = models.IntegerField(db_column='Manual', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'RendicionCuentaLista'        