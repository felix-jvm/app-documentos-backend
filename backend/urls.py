from rest_framework.renderers import JSONRenderer
from rest_framework.routers import DefaultRouter
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from django.conf.urls.static import static
from .serializer import ImageSerializer
from django.http import HttpResponse
from django.core import serializers
from rest_framework import viewsets
from django.conf import settings
from datetime import datetime
import api.models as M
import os
import json
import io

class ProcedimientoView(viewsets.ViewSet):

 fieldsSchema = {
  'fields':[{'name':'Codigo', 'null':False, 'maxLength':50, 'needsToBeUnique':False, 'type':'str'},
            {'name':'Objetivo', 'null':False, 'maxLength':9999, 'needsToBeUnique':True, 'type':'str'},
            {'name':'Alcance', 'null':False, 'maxLength':9999, 'needsToBeUnique':False, 'type':'str'},
            {'name':'Diagrama_Flujo', 'null':True, 'maxLength':500, 'needsToBeUnique':False, 'type':'str'}]
 }

 relations = {
   'any':False,
   'to':[{'name':'', 'column':'', 'from':''}]
  }

 def create(self,req):
  data = {}
  if req.data['mode'] == 'requestNonUsedCodes':
   codeData = {'procedimiento_Codigo':[]}
   procedMapping = {}
   procedRecords = list(M.Procedimiento.objects.values('Codigo','ID'))
   docsRecords = list(M.Documentos.objects.filter(Codigo__contains='PRO').values('ID','Codigo','Descripcion'))
   for procedObj in procedRecords:
    procedMapping[procedObj['Codigo']] = procedObj['ID']

   for docObj in docsRecords:
    if (docObj['Codigo'] not in procedMapping.keys()) or (docObj['Codigo'] in procedMapping.keys() and not procedMapping[docObj['Codigo']]) or (req.data['specificProcedCode'] and docObj['Codigo']==req.data['specificProcedCode']):
     codeData['procedimiento_Codigo'].append(docObj)

   return Response(codeData)    

  if req.data['mode'] == 'fillForm':
   data['DocumentosReferencias-IDDocumento'] = list(M.Documentos.objects.all().values('ID','Codigo','Descripcion').filter(Codigo__contains='PRO'))
   data['Responsabilidades-IDPuesto'] = list(M.Puestos.objects.all().values('ID','Descripcion'))
   data['Responsabilidades-Descripcion'] = list(M.Responsabilidades.objects.all().values('ID','Descripcion'))
   data['TerminologiasDef-IDTermino'] = list(M.Termino.objects.all().values('ID','Descripcion'))   
   data['TerminologiasDef-Descripcion'] = list(M.TerminologiasDef.objects.all().values('ID','Descripcion'))
   data['DescripcionesProcedimiento-Codigo'] = list(M.DescripcionesProcedimiento.objects.all().values('ID','Codigo'))
   data['DescripcionesProcedimiento-Descripcion'] = list(M.DescripcionesProcedimiento.objects.all().values('ID','Descripcion'))
   data['Puestos'] = list(M.Puestos.objects.all().values('ID','Descripcion'))   
   data['SubDescripciones-IDDescripcion'] = list(M.SubDescripciones.objects.all().values('ID','SubDescripcion'))
   data['Anexos-Nombre'] = list(M.Anexos.objects.all().values('ID','Nombre'))
   data['RevAprobacion-RevisadoPor'] = list(M.RevAprobacion.objects.all().values('ID','RevisadoPor'))
   if 'procedCodigo' in req.data.keys():
    specificData = {}
    relationsObj = list(M.Procedimiento.objects.filter(Codigo=req.data['procedCodigo']))
    procId = ''
    if not relationsObj:
     relationsObj = list(M.Procedimiento.objects.filter(Objetivo=req.data['procedCodigo']))     
    if not relationsObj:
     relationsObj = list(M.Procedimiento.objects.filter(Alcance=req.data['procedCodigo']))     
     
    if relationsObj:
     specificData['Procedimiento_Codigo'] = relationsObj[0].Codigo
     specificData['Procedimiento_Objetivo'] = relationsObj[0].Objetivo
     specificData['Procedimiento_Alcance'] = relationsObj[0].Alcance
    #  specificData['Diagrama_Flujo'] = ImageSerializer(relationsObj[0],many=False).data
     procId = relationsObj[0].ID
    else:
     return Response([])
    recordsIterator = lambda columns,toIterate,refTable=None,*userFriendlyColumn:[{prop:(list(eval('M.%s'%(refTable)).objects.filter(pk=record[prop]).values(*userFriendlyColumn))[:1] if 'ID' in prop and len(prop) > 2 else record[prop]) for prop in columns if type(record)==dict and prop in record.keys()} for record in toIterate]

    relationsObj = list(M.RevAprobacion.objects.filter(IDProcedimiento=procId).values('ID','ElaboradoPor','FirmaElaborado','PuestoElaborado','RevisadoPor','FirmaRevisado','PuestoRevisado','AprobadoPor','FirmaAprobado','PuestoAprobado'))
    if relationsObj:
     specificData['RevAprobacion'] = [[relationsObj[0]['ElaboradoPor'],relationsObj[0]['FirmaElaborado'],relationsObj[0]['PuestoElaborado']], [relationsObj[0]['RevisadoPor'],relationsObj[0]['FirmaRevisado'],relationsObj[0]['PuestoRevisado']], [relationsObj[0]['AprobadoPor'],relationsObj[0]['FirmaAprobado'],relationsObj[0]['PuestoAprobado']],relationsObj[0]['ID']]
    specificData['Anexos'] = list(M.Anexos.objects.filter(IDProcedimiento=procId).values('ID','Num','Nombre','Codigo'))

    relationsObj = list(M.DescripcionesProcedimiento.objects.filter(IDProcedimiento=procId).values('ID','Descripcion'))
    if relationsObj:
     specificData['DescripcionesProcedimiento'] = relationsObj
     specificData['SubDescripciones'] = {}
     for descripObj in relationsObj:
      subDescripRecords = list(M.SubDescripciones.objects.filter(IDDescripcion=descripObj['ID']).values('ID','Codigo','SubDescripcion'))
      if subDescripRecords:specificData['SubDescripciones'][descripObj['Descripcion']] = subDescripRecords

    relationsObj = list(M.TerminologiasDef.objects.filter(IDProcedimiento=procId).values('ID','IDTermino','Descripcion'))
    if relationsObj:specificData['TerminologiasDef'] = recordsIterator(['ID','IDTermino','Descripcion'],relationsObj,'Termino','Descripcion')

    relationsObj = list(M.Responsabilidades.objects.filter(IDProcedimiento=procId).values('ID','IDPuesto','Descripcion'))
    if relationsObj:specificData['Responsabilidades'] = recordsIterator(['ID','IDPuesto','Descripcion'],relationsObj,'Puestos','Descripcion')

    relationsObj = list(M.DocumentosReferencias.objects.filter(IDProcedimiento=procId).values('ID','IDDocumento')) 
    if relationsObj:specificData['DocumentosReferencias'] = recordsIterator(['ID','IDDocumento'],relationsObj,'Documentos','Codigo','Descripcion')

    specificData['HistorialCambios'] = list(M.HistorialCambios.objects.filter(IDProcedimiento=procId).values('ID','Fecha','Version','Descripcion'))    

    relationsObj = M.Documentos.objects.filter(Codigo=req.data['procedCodigo'].strip().replace(' ','')).values('Descripcion','Fecha','Version')
    if relationsObj:specificData['Documentos'] = relationsObj[0]

    data['specificData'] = specificData

  if req.data['mode'] == 'CREATE':
   columnsSchema = {'DocumentosReferencias':['IDDocumento'],'Responsabilidades':['Descripcion','IDPuesto'],'TerminologiasDef':['IDTermino','Descripcion'],'DescripcionesProcedimiento':['Descripcion'],'SubDescripciones':['SubDescripcion','IDDescripcion','Codigo'],'Anexos':['Codigo','Nombre','Num'],'RevAprobacion':[
    'ElaboradoPor',
    'FirmaElaborado',
    'PuestoElaborado',
    'RevisadoPor',
    'FirmaRevisado',
    'PuestoRevisado',
    'AprobadoPor',
    'FirmaAprobado',
    'PuestoAprobado',
    ],'HistorialCambios':['Descripcion','Version','Fecha']}
   dataToProcess = req.data['backenData']
   procId = ''
   if 'specificProced' in req.data['backenData'].keys():
    procedRecord = list(M.Procedimiento.objects.filter(Codigo=req.data['backenData']['specificProced']).filter(deleted=False))
    if not procedRecord:return Response({})
    procedRecord = procedRecord[0]
    procId = procedRecord.ID
    procedRecord.Codigo = req.data['backenData']['Procedimiento_CodigoSelect'].strip().replace(' ','')
    procedRecord.Objetivo = req.data['backenData']['Procedimiento_ObjetivoInput']
    procedRecord.Alcance = req.data['backenData']['Procedimiento_AlcanceInput']
    procedRecord.save()
   else:
    procData = {}
    procData['Codigo'] = req.data['backenData']['Procedimiento_CodigoSelect'].strip().replace(' ','')
    procData['Objetivo'] = req.data['backenData']['Procedimiento_ObjetivoInput']
    procData['Alcance'] = req.data['backenData']['Procedimiento_AlcanceInput']   
    procId = M.Procedimiento.objects.create(**procData).ID
   for tableColumnKey in dataToProcess.keys():
    tableName = tableColumnKey.split('_')[0]
    if tableName == 'Procedimiento' or tableName == 'Diagrama' or tableName == 'specificProced':continue
    if tableName == 'DescripcionesProcedimiento' or tableName == 'SubDescripciones':
     if tableName == 'DescripcionesProcedimiento':
      for descripcionProcData in dataToProcess['DescripcionesProcedimiento']:
       newDescripProc = {}
       newDescripProc['IDProcedimiento'] = procId
       newDescripProc['Descripcion'] = descripcionProcData['Descripcion']
       descipProcId = M.DescripcionesProcedimiento.objects.create(**newDescripProc).ID
       if descripcionProcData['Descripcion'] in dataToProcess['SubDescripciones']:
        for correspondingSubDescrip in dataToProcess['SubDescripciones'][descripcionProcData['Descripcion']]:
         newSubDescrip = {}
         newSubDescrip['Codigo'] = correspondingSubDescrip['Codigo']
         newSubDescrip['SubDescripcion'] = correspondingSubDescrip['SubDescripcion']
         newSubDescrip['IDDescripcion'] = descipProcId
        M.SubDescripciones.objects.create(**newSubDescrip)

     continue

    if tableName in columnsSchema.keys(): 
     for records in dataToProcess[tableName]:
      recordToCreate = {}
      for columnName in columnsSchema[tableName]:
       if columnName in records.keys():
        if 'ID' in columnName:
         recordToCreate[columnName] = int(records[columnName].strip().split('-')[0])
        else: 
         if records[columnName]:
          recordToCreate[columnName] = records[columnName]
      recordToCreate['IDProcedimiento'] = procId
      print('-------------------------->',tableName,recordToCreate) 
      eval('M.%s'%(tableName)).objects.create(**recordToCreate)

   for record in req.data['backenData']['recordsToDelete']:
     if record.keys():
      tableName = list(record.keys())[0]
      recordToDelete = eval('M.%s'%(tableName)).objects.filter(pk=record[tableName])
      if recordToDelete:
       recordToDelete[0].delete()

   return Response({'status':'ok'})
  
  if req.data['mode'] == 'save_diagrama_flujo_img':
   recordToUpdate = list(M.Procedimiento.objects.filter(Codigo=req.data['procedCode'].strip().replace(' ','')))
   if recordToUpdate and req.data['img']!='null':
    recordToUpdate[0].Diagrama_Flujo = req.data['img'].read()
    recordToUpdate[0].save()

  if req.data['mode'] == 'request_proced_diagrama_flujo':
   procedRecord = list(M.Procedimiento.objects.filter(Codigo=req.data['procedCode'].strip().replace(' ','')))   
   if procedRecord:return HttpResponse(procedRecord[0].Diagrama_Flujo,content_type='image/png')
   return Response([]) 

  if req.data['mode'] == 'deleteRecord':
   objtoDelete = list(M.Procedimiento.objects.filter(Codigo=req.data['procedCodigo'].strip().replace(' ','')))
   if objtoDelete:
    objtoDelete[0].deleted = True
    objtoDelete[0].save()
    return Response({'status':'ok'})
   else:
    return Response([])
   
  return Response(data)


 def list(self, req):
  data = list(M.Procedimiento.objects.all().filter(deleted=False).values('ID','Codigo','Objetivo'))
  proceData = {'fields':['Còdigo','Descripcion','Objetivo','Fecha','Version'],'data':[]}
  for procedRecord in data:
   jointRecord = {}
   jointRecord['Codigo'] = procedRecord['Codigo']
   jointRecord['Objetivo'] = procedRecord['Objetivo']
   if jointRecord['Codigo']:
    docRecord = list(M.Documentos.objects.filter(Codigo=jointRecord['Codigo']))
    if docRecord:
     jointRecord['Descripcion'] = docRecord[0].Descripcion
     jointRecord['Fecha'] = docRecord[0].Fecha
     jointRecord['Version'] = docRecord[0].Version
   proceData['data'].append(jointRecord)

  return Response(proceData)
  
  # data = serializers.serialize('json',M.Procedimiento.objects.all())
  # if data == '[]':
  #  data = M.Procedimiento.__doc__
  #  data = data.replace('','')
  #  data = data.replace('(','')
  #  data = data.replace(')','')
  #  data = data.replace('Procedimiento','')
  #  data = data.split(',')  
  #  data.append('statusEmpty')
  #  data.append({'route':'procedimiento'})

  # return Response(data)


class DocumentoReferenciaView(viewsets.ViewSet):

 fieldsSchema = {
  'fields':[{'name':'IDDocumento', 'null':True, 'maxLength':False, 'needsToBeUnique':False, 'type':'select'},
            {'name':'IDProcedimiento', 'null':True, 'maxLength':False, 'needsToBeUnique':False, 'type':'select'}]
}

 relations = {
   'any':True,
   'to':[{'name':'Procedimiento', 'column':'Objetivo', 'from':'IDProcedimiento'},
         {'name':'Documentos', 'column':'Codigo', 'from':'IDDocumento'}]
  }

 def create(self,req):

  data = ''
  relationsData = []
  if req.data['mode'] == 'relations':
   if self.relations['any']:
    for relationDetails in self.relations['to']:
      relationRecords = list(eval('M.%s'%relationDetails['name']).objects.all().values(relationDetails['column']))
      if relationRecords:
       relationsData.append(relationRecords)
       relationsData[-1][0]['table'] = relationDetails['name']
   data = {'schema':self.fieldsSchema, 'relations':relationsData if relationsData else []}
  elif req.data['mode'] == 'create':
   fields = {}
   procedimientoChoice = req.data['data']['IDProcedimiento']
   documentoChoice = req.data['data']['IDDocumento']
   fields['IDDocumento'] = M.Documentos.objects.filter(Codigo=documentoChoice).values('ID')[0]['ID'] if req.data['data']['IDDocumento'] else None
   fields['IDProcedimiento'] = M.Procedimiento.objects.filter(Objetivo=procedimientoChoice).values('ID')[0]['ID'] if req.data['data']['IDProcedimiento'] else None
   M.DocumentosReferencias.objects.create(**fields)
  elif req.data['mode'] == 'update':
   fields = {}
   fields['IDProcedimiento'] = M.Procedimiento.objects.filter(Objetivo=req.data['data']['IDProcedimiento']).values('ID')[0]['ID'] if req.data['data']['IDProcedimiento'] else None   
   fields['IDDocumento'] = M.Documentos.objects.filter(Codigo=req.data['data']['IDDocumento']).values('ID')[0]['ID'] if req.data['data']['IDDocumento'] else None   
   updatedObj = M.DocumentosReferencias(pk=req.data['data']['ID'],**fields)
   updatedObj.save()

   
  return Response(json.dumps({'data':data}))
 
 def delete(self,req):
  print('--->',req.data['ID'])
  objToDelete = M.DocumentosReferencias.objects.get(pk=req.data['ID'])
  objToDelete.delete()
  return Response({'response':'ok'})

 def list(self, req):
  data = serializers.serialize('json',M.DocumentosReferencias.objects.all())
  if data == '[]':
   data = M.DocumentosReferencias.__doc__
   data = data.replace(' ','')
   data = data.replace('(','')
   data = data.replace(')','')
   data = data.replace('DocumentosReferencias','')
   data = data.split(',')  
   data.append('statusEmpty')
   data.append({'route':'documentosreferencias'})
  return Response(data)


class DocumentoView(viewsets.ViewSet):

 fieldsSchema = {
  'fields':[{'name':'Codigo', 'null':False, 'maxLength':50, 'needsToBeUnique':True, 'type':'str'},
            {'name':'Descripcion', 'null':True, 'maxLength':100, 'needsToBeUnique':False, 'type':'str'}]
 }

 relations = {
   'any':False,
   'to':[{'name':'', 'column':'', 'from':''},
         {'name':'', 'column':'', 'from':''}]
  } 

 def create(self,req):
  data = {}
  if req.data['mode'] == 'fillForm':
  #  recordsIterator = lambda columns,toIterate,refTable=None,*userFriendlyColumn:[{prop:(list(eval('M.%s'%(refTable)).objects.filter(pk=record[prop]).values(*userFriendlyColumn))[:1] if 'ID' in prop and len(prop) > 2 else record[prop]) for prop in columns if type(record)==dict and prop in record.keys()} for record in toIterate]              
   data['departamentoSelect'] = list(M.Departamento.objects.all().values('ID','Codigo','Descripcion'))
   data['tipoDocumentoSelect'] = list(M.TipoDocumento.objects.all().values('ID','Codificacion','Descripcion'))
   return Response(data)
  
  elif req.data['mode'] == 'requestCodeSequence':
   sequenceToLook = req.data['code'].strip().replace(' ','')
   highestSequence = list(M.Documentos.objects.filter(TipoDoc_Dep_Repr__contains=sequenceToLook).order_by('-TipoDoc_Dep_Repr'))
   if highestSequence and highestSequence[0].TipoDoc_Dep_Repr:
    highestSequence = int(highestSequence[0].TipoDoc_Dep_Repr.split('-')[2]) + 1
    highestSequence = str(highestSequence).zfill(3)
   else:
    highestSequence = '001' 
   return Response(highestSequence)

  elif req.data['mode'] == 'create':
   fields = {}
   IDDepartamento = req.data['data']['sequence'].split('-')[1]
   IDTipoDocumento = req.data['data']['sequence'].split('-')[0]
   fields['Codigo'] = req.data['data']['Codigo']
   fields['Descripcion'] = req.data['data']['Descripcion']
   fields['Version'] = req.data['data']['Version']
   fields['Fecha'] = req.data['data']['Fecha']
   IDTipoDocumento = list(M.TipoDocumento.objects.filter(Codificacion=IDTipoDocumento).values('ID'))
   IDDepartamento = list(M.Departamento.objects.filter(Codigo=IDDepartamento).values('ID'))
   print('------------->',IDDepartamento,IDTipoDocumento)
   if IDTipoDocumento:fields['IDTipoDocumento'] = IDTipoDocumento[0]['ID']
   if IDDepartamento:fields['IDDepartamento'] = IDDepartamento[0]['ID']

   fields['TipoDoc_Dep_Repr'] = req.data['data']['Codigo']   

   M.Documentos.objects.create(**fields)  
   
  elif req.data['mode'] == 'requestUpdateData':
   obj = M.Documentos.objects.get(pk=req.data['ID']['current'])
   data = {}
   data['Codigo'] = obj.Codigo
   data['Descripcion'] = obj.Descripcion
  elif req.data['mode'] == 'update':
   fields = {}
   fields['Codigo'] = req.data['data']['Codigo']
   fields['Descripcion'] = req.data['data']['Descripcion']   
   updatedObj = M.Documentos(pk=req.data['data']['ID'],**fields)
   updatedObj.save()  
  return Response(json.dumps({'data':data}))
 
 def delete(self,req):
  print('------->',req.data['ID'])
  objToDelete = M.Documentos.objects.get(pk=req.data['ID'])
  objToDelete.delete()
  return Response({'response':'ok'}) 
 
 def list(self, req):
  data = serializers.serialize('json',M.Documentos.objects.all())
  if data == '[]':
   data = M.Documentos.__doc__
   data = data.replace(' ','')
   data = data.replace('(','')
   data = data.replace(')','')
   data = data.replace('Documentos','')
   data = data.split(',')  
   data.append('statusEmpty')
   data.append({'route':'documentos'})
  return Response(data)


class ResponsabilidadesView(viewsets.ViewSet):
 
 fieldsSchema = {
  'fields':[{'name':'IDProcedimiento', 'null':False, 'maxLength':False, 'needsToBeUnique':False, 'type':'select'},
            {'name':'IDPuesto', 'null':False, 'maxLength':False, 'needsToBeUnique':False, 'type':'select'},
            {'name':'Descripcion', 'null':False, 'maxLength':500, 'needsToBeUnique':False, 'type':'str'}]
 }

 relations = {
   'any':True,
   'to':[{'name':'Procedimiento', 'column':'Objetivo', 'from':'IDProcedimiento'},
         {'name':'Puestos', 'column':'Descripcion', 'from':'IDPuesto'}]
  } 

 def create(self,req):
  data = ''
  relationsData = []
  
  if req.data['mode'] == 'relations':
   if self.relations['any']:
    for relationDetails in self.relations['to']:
      relationRecords = list(eval('M.%s'%relationDetails['name']).objects.all().values(relationDetails['column']))
      if relationRecords:
       relationsData.append(relationRecords)
       relationsData[-1][0]['table'] = relationDetails['name']
   data = {'schema':self.fieldsSchema, 'relations':relationsData if relationsData else []}
  elif req.data['mode'] == 'create':
   fields = {}
   fields['Descripcion'] = req.data['data']['Descripcion']
   fields['IDProcedimiento'] = M.Procedimiento.objects.filter(Objetivo=req.data['data']['IDProcedimiento']).values('ID')[0]['ID'] if req.data['data']['IDProcedimiento'] else None
   fields['IDPuesto'] = M.Puestos.objects.filter(Descripcion=req.data['data']['IDPuesto']).values('ID')[0]['ID'] if req.data['data']['IDPuesto'] else None
   M.Responsabilidades.objects.create(**fields)
  elif req.data['mode'] == 'requestUpdateData':
   obj = M.Responsabilidades.objects.get(pk=req.data['ID']['current'])
   data = {}
   data['IDPuesto'] = obj.IDPuesto
   data['Descripcion'] = obj.Descripcion
   data['IDProcedimiento'] = obj.IDProcedimiento   
  elif req.data['mode'] == 'update':
   fields = {}
   fields['Descripcion'] = req.data['data']['Descripcion']   
   fields['IDProcedimiento'] = M.Procedimiento.objects.filter(Objetivo=req.data['data']['IDProcedimiento']).values('ID')[0]['ID'] if req.data['data']['IDProcedimiento'] else None   
   fields['IDPuesto'] = M.Puestos.objects.filter(Descripcion=req.data['data']['IDPuesto']).values('ID')[0]['ID'] if req.data['data']['IDPuesto'] else None
   updatedObj = M.Responsabilidades(pk=req.data['data']['ID'],**fields)
   updatedObj.save()   
  return Response(json.dumps({'data':data}))
 
 def delete(self,req):
  print('---->',req.data['ID'])
  objToDelete = M.Responsabilidades.objects.get(pk=req.data['ID'])
  objToDelete.delete()
  return Response({'response':'ok'}) 

 def list(self, req):
  data = serializers.serialize('json',M.Responsabilidades.objects.all())
  if data == '[]':
   data = M.Responsabilidades.__doc__
   data = data.replace(' ','')
   data = data.replace('(','')
   data = data.replace(')','')
   data = data.replace('Responsabilidades','')
   data = data.split(',')
   data.append('statusEmpty')
   data.append({'route':'responsabilidades'})
  return Response(data)


class PuestoView(viewsets.ViewSet):
 
 fieldsSchema = {
  'fields':[{'name':'Descripcion', 'null':False, 'maxLength':50, 'needsToBeUnique':True, 'type':'str'},
            {'name':'UnidadNegocio', 'null':True, 'maxLength':False, 'needsToBeUnique':False, 'type':'int'},
            {'name':'Actividad', 'null':True, 'maxLength':False, 'needsToBeUnique':False, 'type':'int'}]
 }
 
 relations = {
   'any':False,
   'to':[{'name':'', 'column':'', 'from':''},
         {'name':'', 'column':'', 'from':''}]
  }

 def create(self,req):
  data = ''
  relationsData = []
  if req.data['mode'] == 'relations':
   if self.relations['any']:
    for relationDetails in self.relations['to']:
      relationRecords = list(eval('M.%s'%relationDetails['name']).objects.all().values(relationDetails['column']))
      if relationRecords:
       relationsData.append(relationRecords)
       relationsData[-1][0]['table'] = relationDetails['name']
   data = {'schema':self.fieldsSchema, 'relations':relationsData if relationsData else []}
  elif req.data['mode'] == 'create':
   fields = {}
   if req.data['data']['Descripcion']:fields['Descripcion'] = req.data['data']['Descripcion']
   if req.data['data']['UnidadNegocio']:fields['UnidadNegocio'] = req.data['data']['UnidadNegocio']
   if req.data['data']['Actividad']:fields['Actividad'] = req.data['data']['Actividad']
   M.Puestos.objects.create(**fields)
   data = fields
  elif req.data['mode'] == 'requestUpdateData':
   obj = M.Puestos.objects.get(pk=req.data['ID']['current'])
   data = {}
   data['Descripcion'] = obj.Descripcion
   data['UnidadNegocio'] = obj.UnidadNegocio
   data['Actividad'] = obj.Actividad
  elif req.data['mode'] == 'update':
   fields = {}
   fields['UnidadNegocio'] = req.data['data']['UnidadNegocio']
   fields['Descripcion'] = req.data['data']['Descripcion']   
   fields['Actividad'] = req.data['data']['Actividad']
   updatedObj = M.Puestos(pk=req.data['data']['ID'],**fields)
   updatedObj.save()
  return Response(json.dumps({'data':data}))
 
 def delete(self,req):
  print('----->',req.data['ID'])
  objToDelete = M.Puestos.objects.get(pk=req.data['ID'])
  objToDelete.delete()
  return Response({'response':'ok'}) 

 def list(self, req):
  data = serializers.serialize('json',M.Puestos.objects.all())
  if data == '[]':
   data = M.Puestos.__doc__
   data = data.replace(' ','')
   data = data.replace('(','')
   data = data.replace(')','')
   data = data.replace('Puestos','')
   data = data.split(',')  
   data.append('statusEmpty')
   data.append({'route':'puestos'})
  return Response(data)


class TerminologiaDefView(viewsets.ViewSet):
 
 fieldsSchema = {
  'fields':[{'name':'IDProcedimiento', 'null':False, 'maxLength':False, 'needsToBeUnique':False, 'type':'select'},
            {'name':'IDTermino', 'null':False, 'maxLength':False, 'needsToBeUnique':False, 'type':'select'},
            {'name':'Descripcion', 'null':False, 'maxLength':500, 'needsToBeUnique':False, 'type':'str'}]
 }

 relations = {
   'any':True,
   'to':[{'name':'Procedimiento', 'column':'Objetivo', 'from':'IDProcedimiento'},
         {'name':'Termino', 'column':'Descripcion', 'from':'IDTermino'}]
  } 

 def create(self,req):
  data = ''
  relationsData = []
  
  if req.data['mode'] == 'relations':
   if self.relations['any']:
    for relationDetails in self.relations['to']:
      relationRecords = list(eval('M.%s'%relationDetails['name']).objects.all().values(relationDetails['column']))
      if relationRecords:
       relationsData.append(relationRecords)
       relationsData[-1][0]['table'] = relationDetails['name']
   data = {'schema':self.fieldsSchema, 'relations':relationsData if relationsData else []}
  elif req.data['mode'] == 'create':
   fields = {}
   fields['Descripcion'] = req.data['data']['Descripcion']
   fields['IDProcedimiento'] = M.Procedimiento.objects.filter(Objetivo=req.data['data']['IDProcedimiento']).values('ID')[0]['ID'] if req.data['data']['IDProcedimiento'] else None
   fields['IDTermino'] = M.Termino.objects.filter(Descripcion=req.data['data']['IDTermino']).values('ID')[0]['ID'] if req.data['data']['IDTermino'] else None   
   M.TerminologiasDef.objects.create(**fields)
  elif req.data['mode'] == 'requestUpdateData':
   obj = M.TerminologiasDef.objects.get(pk=req.data['ID']['current'])
   data = {}
   data['Descripcion'] = obj.Descripcion
   data['IDProcedimiento'] = obj.IDProcedimiento  
   data['IDTermino'] = obj.IDTermino 
  elif req.data['mode'] == 'update':
   fields = {}
   fields['Descripcion'] = req.data['data']['Descripcion']   
   fields['IDProcedimiento'] = M.Procedimiento.objects.filter(Objetivo=req.data['data']['IDProcedimiento']).values('ID')[0]['ID'] if req.data['data']['IDProcedimiento'] else None   
   fields['IDTermino'] = M.Termino.objects.filter(Descripcion=req.data['data']['IDTermino']).values('ID')[0]['ID'] if req.data['data']['IDTermino'] else None   
   updatedObj = M.TerminologiasDef(pk=req.data['data']['ID'],**fields)
   updatedObj.save()   
  return Response(json.dumps({'data':data}))
 
 def delete(self,req):
  print('------->',req.data['ID'])
  objToDelete = M.TerminologiasDef.objects.get(pk=req.data['ID'])
  objToDelete.delete()
  return Response({'response':'ok'}) 

 def list(self, req):
  data = serializers.serialize('json',M.TerminologiasDef.objects.all())
  if data == '[]':
   data = M.TerminologiasDef.__doc__
   data = data.replace(' ','')
   data = data.replace('(','')
   data = data.replace(')','')
   data = data.replace('TerminologiasDef','')
   data = data.split(',')  
   data.append('statusEmpty')  
   data.append({'route':'terminologiasdef'})
  return Response(data)


class TerminoView(viewsets.ViewSet):
 
 fieldsSchema = {
  'fields':[{'name':'Descripcion', 'null':False, 'maxLength':50, 'needsToBeUnique':True, 'type':'str'},
            {'name':'DescripcionGeneral', 'null':True, 'maxLength':500, 'needsToBeUnique':False, 'type':'str'}]
 }

 relations = {
   'any':False,
   'to':[{'name':'', 'column':'', 'from':''},
         {'name':'', 'column':'', 'from':''}]
  } 

 def create(self,req):
  data = ''
  relationsData = []

  if req.data['mode'] == 'relations':
   if self.relations['any']:
    for relationDetails in self.relations['to']:
      relationRecords = list(eval('M.%s'%relationDetails['name']).objects.all().values(relationDetails['column']))
      if relationRecords:
       relationsData.append(relationRecords)
       relationsData[-1][0]['table'] = relationDetails['name']
   data = {'schema':self.fieldsSchema, 'relations':relationsData if relationsData else []}  
  elif req.data['mode'] == 'create':
   fields = {}
   fields['Descripcion'] = req.data['data']['Descripcion']
   fields['DescripcionGeneral'] = req.data['data']['DescripcionGeneral']
   M.Termino.objects.create(**fields)    
  elif req.data['mode'] == 'requestUpdateData':
   obj = M.Termino.objects.get(pk=req.data['ID']['current'])
   data = {}
   data['Descripcion'] = obj.Descripcion
   data['DescripcionGeneral'] = obj.DescripcionGeneral   
  elif req.data['mode'] == 'update':
   fields = {}
   fields['Descripcion'] = req.data['data']['Descripcion']   
   fields['DescripcionGeneral'] = req.data['data']['DescripcionGeneral']
   updatedObj = M.Termino(pk=req.data['data']['ID'],**fields)
   updatedObj.save()
  return Response(json.dumps({'data':data}))
 
 def list(self, req):
  data = serializers.serialize('json',M.Termino.objects.all())
  if data == '[]':
   data = M.Termino.__doc__
   data = data.replace(' ','')
   data = data.replace('(','')
   data = data.replace(')','')
   data = data.replace('Termino','')
   data = data.split(',')  
   data.append('statusEmpty')
   data.append({'route':'termino'})  
  return Response(data)

 def delete(self,req):
  print('---->',req.data['ID'])
  objToDelete = M.Termino.objects.get(pk=req.data['ID'])
  objToDelete.delete()
  return Response({'response':'ok'}) 

class DescripcionProcedimientoView(viewsets.ViewSet):
 
 fieldsSchema = {
  'fields':[{'name':'Codigo', 'null':False, 'maxLength':50, 'needsToBeUnique':False, 'type':'str'},
            {'name':'IDProcedimiento', 'null':False, 'maxLength':False, 'needsToBeUnique':False, 'type':'select'},
            {'name':'Descripcion', 'null':False, 'maxLength':9999, 'needsToBeUnique':True, 'type':'str'}]
 }

 relations = {
   'any':True,
   'to':[{'name':'Procedimiento', 'column':'Objetivo', 'from':'IDProcedimiento'}]
  } 

 def create(self,req):
  data = ''
  relationsData = []
  
  if req.data['mode'] == 'relations':
   if self.relations['any']:
    for relationDetails in self.relations['to']:
      relationRecords = list(eval('M.%s'%relationDetails['name']).objects.all().values(relationDetails['column']))
      if relationRecords:
       relationsData.append(relationRecords)
       relationsData[-1][0]['table'] = relationDetails['name']
   data = {'schema':self.fieldsSchema, 'relations':relationsData if relationsData else []}
  elif req.data['mode'] == 'create':
   fields = {}
   fields['Codigo'] = req.data['data']['Codigo']
   fields['Descripcion'] = req.data['data']['Descripcion']
   fields['IDProcedimiento'] = M.Procedimiento.objects.filter(Objetivo=req.data['data']['IDProcedimiento']).values('ID')[0]['ID'] if req.data['data']['IDProcedimiento'] else None
   M.DescripcionesProcedimiento.objects.create(**fields)   
  elif req.data['mode'] == 'requestUpdateData':
   obj = M.DescripcionesProcedimiento.objects.get(pk=req.data['ID']['current'])
   data = {}
   data['Codigo'] = obj.Codigo
   data['Descripcion'] = obj.Descripcion
   data['IDProcedimiento'] = obj.IDProcedimiento
  elif req.data['mode'] == 'update':
   fields = {}
   fields['Codigo'] = req.data['data']['Codigo']
   fields['Descripcion'] = req.data['data']['Descripcion']   
   fields['IDProcedimiento'] = M.Procedimiento.objects.filter(Objetivo=req.data['data']['IDProcedimiento']).values('ID')[0]['ID'] if req.data['data']['IDProcedimiento'] else None   
   updatedObj = M.DescripcionesProcedimiento(pk=req.data['data']['ID'],**fields)
   updatedObj.save()
  return Response(json.dumps({'data':data}))
 
 def delete(self,req):
  print('---->',req.data['ID'])
  objToDelete = M.DescripcionesProcedimiento.objects.get(pk=req.data['ID'])
  objToDelete.delete()
  return Response({'response':'ok'}) 

 def list(self, req):
  data = serializers.serialize('json',M.DescripcionesProcedimiento.objects.all())
  if data == '[]':
   data = M.DescripcionesProcedimiento.__doc__
   data = data.replace(' ','')
   data = data.replace('(','')
   data = data.replace(')','')
   data = data.replace('DescripcionesProcedimiento','')
   data = data.split(',')  
   data.append('statusEmpty')
   data.append({'route':'descripcionesprocedimiento'})  
  return Response(data)

class SubDescripcionView(viewsets.ViewSet):
 
 fieldsSchema = {
  'fields':[{'name':'Codigo', 'null':False, 'maxLength':50, 'needsToBeUnique':False, 'type':'str'},
            {'name':'IDDescripcion', 'null':True, 'maxLength':False, 'needsToBeUnique':False, 'type':'select'},
            {'name':'SubDescripcion', 'null':True, 'maxLength':9999, 'needsToBeUnique':False, 'type':'str'}]
 }

 relations = {
   'any':True,
   'to':[{'name':'DescripcionesProcedimiento', 'column':'Descripcion', 'from':'IDDescripcion'}]
  } 

 def create(self,req):
  data = ''
  relationsData = []
  
  if req.data['mode'] == 'relations':
   if self.relations['any']:
    for relationDetails in self.relations['to']:
      relationRecords = list(eval('M.%s'%relationDetails['name']).objects.all().values(relationDetails['column']))
      if relationRecords:
       relationsData.append(relationRecords)
       relationsData[-1][0]['table'] = relationDetails['name']
   data = {'schema':self.fieldsSchema, 'relations':relationsData if relationsData else []}
  elif req.data['mode'] == 'create':
   fields = {}
   fields['Codigo'] = req.data['data']['Codigo']
   fields['SubDescripcion'] = req.data['data']['SubDescripcion']
   fields['IDDescripcion'] = M.DescripcionesProcedimiento.objects.filter(Descripcion__iexact=req.data['data']['IDDescripcion'])
   fields['IDDescripcion'] = fields['IDDescripcion'].values()[0]['ID'] if req.data['data']['IDDescripcion'] and fields['IDDescripcion'] else None   
   M.SubDescripciones.objects.create(**fields)
  elif req.data['mode'] == 'requestUpdateData':
   obj = M.SubDescripciones.objects.get(pk=req.data['ID']['current'])
   data = {}
   data['Codigo'] = obj.Codigo
   data['SubDescripcion'] = obj.SubDescripcion
   data['IDDescripcion'] = obj.IDDescripcion   
  elif req.data['mode'] == 'update':
   fields = {}
   fields['Codigo'] = req.data['data']['Codigo']
   fields['SubDescripcion'] = req.data['data']['SubDescripcion']   
   fields['IDDescripcion'] = M.DescripcionesProcedimiento.objects.filter(Descripcion=req.data['data']['IDDescripcion']).values('ID')[0]['ID'] if req.data['data']['IDDescripcion'] else None   
   updatedObj = M.SubDescripciones(pk=req.data['data']['ID'],**fields)
   updatedObj.save()   
  return Response(json.dumps({'data':data})) 
 
 def delete(self,req):
  print('---->',req.data['ID'])
  objToDelete = M.SubDescripciones.objects.get(pk=req.data['ID'])
  objToDelete.delete()
  return Response({'response':'ok'}) 

 def list(self, req):
  data = serializers.serialize('json',M.SubDescripciones.objects.all())
  if data == '[]':
   data = M.SubDescripciones.__doc__
   data = data.replace(' ','')
   data = data.replace('(','')
   data = data.replace(')','')
   data = data.replace('SubDescripciones','')
   data = data.split(',')  
   data.append('statusEmpty')
   data.append({'route':'subdescripciones'})  
  return Response(data)


class AnexoView(viewsets.ViewSet):
 
 fieldsSchema = {
  'fields':[{'name':'Num', 'null':True, 'maxLength':False, 'needsToBeUnique':False, 'type':'int'},
            {'name':'Nombre', 'null':True, 'maxLength':50, 'needsToBeUnique':False, 'type':'str'},
            {'name':'Codigo', 'null':True, 'maxLength':50, 'needsToBeUnique':False, 'type':'str'},
            {'name':'IDProcedimiento', 'null':True, 'maxLength':False, 'needsToBeUnique':False, 'type':'select'}]
 }

 relations = {
   'any':True,
   'to':[{'name':'Procedimiento', 'column':'Objetivo', 'from':'IDProcedimiento'}]
  } 

 def create(self,req):
  data = ''
  relationsData = []
  
  if req.data['mode'] == 'relations':
   if self.relations['any']:
    for relationDetails in self.relations['to']:
      relationRecords = list(eval('M.%s'%relationDetails['name']).objects.all().values(relationDetails['column']))
      if relationRecords:
       relationsData.append(relationRecords)
       relationsData[-1][0]['table'] = relationDetails['name']
   data = {'schema':self.fieldsSchema, 'relations':relationsData if relationsData else []}
  elif req.data['mode'] == 'create':
   fields = {}
   fields['Num'] = req.data['data']['Num']
   fields['Nombre'] = req.data['data']['Nombre']
   fields['Codigo'] = req.data['data']['Codigo']
   fields['IDProcedimiento'] = M.Procedimiento.objects.filter(Objetivo=req.data['data']['IDProcedimiento']).values('ID')[0]['ID'] if req.data['data']['IDProcedimiento'] else None
   M.Anexos.objects.create(**fields)
  elif req.data['mode'] == 'requestUpdateData':
   obj = M.Anexos.objects.get(pk=req.data['ID']['current'])
   data = {}
   data['Num'] = obj.Num
   data['Nombre'] = obj.Nombre
   data['Codigo'] = obj.Codigo
  elif req.data['mode'] == 'update':
   fields = {}
   fields['Num'] = req.data['data']['Num']
   fields['Nombre'] = req.data['data']['Nombre']   
   fields['Codigo'] = req.data['data']['Codigo']   
   fields['IDProcedimiento'] = M.Procedimiento.objects.filter(Objetivo=req.data['data']['IDProcedimiento']).values('ID')[0]['ID'] if req.data['data']['IDProcedimiento'] else None   
   updatedObj = M.Anexos(pk=req.data['data']['ID'],**fields)
   updatedObj.save()   
  return Response(json.dumps({'data':data}))
 
 def delete(self,req):
  objToDelete = M.Anexos.objects.get(pk=req.data['ID'])
  objToDelete.delete()
  return Response({'response':'ok'}) 

 def list(self, req):
  data = serializers.serialize('json',M.Anexos.objects.all())
  if data == '[]':
   data = M.Anexos.__doc__
   data = data.replace(' ','')
   data = data.replace('(','')
   data = data.replace(')','')
   data = data.replace('Anexos','')
   data = data.split(',')  
   data.append('statusEmpty')
   data.append({'route':'anexos'})  
  return Response(data)
 

class RevAprobacionView(viewsets.ViewSet):
 
 fieldsSchema = {
  'fields':[{'name':'IDProcedimiento', 'null':False, 'maxLength':False, 'needsToBeUnique':False, 'type':'select'},
            {'name':'ElaboradoPor', 'null':True, 'maxLength':50, 'needsToBeUnique':False, 'type':'str'},
            {'name':'FirmaElaborado', 'null':True, 'maxLength':50, 'needsToBeUnique':False, 'type':'str'},
            {'name':'PuestoElaborado', 'null':True, 'maxLength':50, 'needsToBeUnique':False, 'type':'str'},
            {'name':'RevisadoPor', 'null':True, 'maxLength':50, 'needsToBeUnique':False, 'type':'str'},
            {'name':'FirmaRevisado', 'null':True, 'maxLength':50, 'needsToBeUnique':False, 'type':'str'},
            {'name':'PuestoRevisado', 'null':True, 'maxLength':50, 'needsToBeUnique':False, 'type':'str'},
            {'name':'AprobadoPor', 'null':True, 'maxLength':50, 'needsToBeUnique':False, 'type':'str'},
            {'name':'FirmaAprobado', 'null':True, 'maxLength':50, 'needsToBeUnique':False, 'type':'str'},
            {'name':'PuestoAprobado', 'null':True, 'maxLength':50, 'needsToBeUnique':False, 'type':'str'}]
 }

 relations ={
   'any':True,
   'to':[{'name':'Procedimiento', 'column':'Objetivo', 'from':'IDProcedimiento'}]
  } 

 def create(self,req):
  data = ''
  relationsData = []
  
  if req.data['mode'] == 'relations':
   if self.relations['any']:
    for relationDetails in self.relations['to']:
      relationRecords = list(eval('M.%s'%relationDetails['name']).objects.all().values(relationDetails['column']))
      if relationRecords:
       relationsData.append(relationRecords)
       relationsData[-1][0]['table'] = relationDetails['name']
   data = {'schema':self.fieldsSchema, 'relations':relationsData if relationsData else []}
  elif req.data['mode'] == 'create':
   fields = {}
   fields['ElaboradoPor'] = req.data['data']['ElaboradoPor']
   fields['FirmaElaborado'] = req.data['data']['FirmaElaborado']
   fields['PuestoElaborado'] = req.data['data']['PuestoElaborado']
   fields['RevisadoPor'] = req.data['data']['RevisadoPor']
   fields['FirmaRevisado'] = req.data['data']['FirmaRevisado']
   fields['PuestoRevisado'] = req.data['data']['PuestoRevisado']
   fields['AprobadoPor'] = req.data['data']['AprobadoPor']
   fields['FirmaAprobado'] = req.data['data']['FirmaAprobado']
   fields['PuestoAprobado'] = req.data['data']['PuestoAprobado']
   fields['IDProcedimiento'] = M.Procedimiento.objects.filter(Objetivo=req.data['data']['IDProcedimiento']).values('ID')[0]['ID'] if req.data['data']['IDProcedimiento'] else None
   M.RevAprobacion.objects.create(**fields)
  elif req.data['mode'] == 'requestUpdateData':
   obj = M.RevAprobacion.objects.get(pk=req.data['ID']['current'])
   data = {}
   data['ElaboradoPor'] = obj.ElaboradoPor
   data['FirmaElaborado'] = obj.FirmaElaborado
   data['PuestoElaborado'] = obj.PuestoElaborado   
   data['RevisadoPor'] = obj.RevisadoPor
   data['FirmaRevisado'] = obj.FirmaRevisado
   data['PuestoRevisado'] = obj.PuestoRevisado
   data['AprobadoPor'] = obj.AprobadoPor
   data['FirmaAprobado'] = obj.FirmaAprobado
   data['PuestoAprobado'] = obj.PuestoAprobado
   data['IDProcedimiento'] = obj.IDProcedimiento    
  elif req.data['mode'] == 'update':
   fields = {}
   fields['ElaboradoPor'] = req.data['data']['ElaboradoPor']
   fields['FirmaElaborado'] = req.data['data']['FirmaElaborado']
   fields['PuestoElaborado'] = req.data['data']['PuestoElaborado']
   fields['RevisadoPor'] = req.data['data']['RevisadoPor']
   fields['FirmaRevisado'] = req.data['data']['FirmaRevisado']
   fields['PuestoRevisado'] = req.data['data']['PuestoRevisado']
   fields['AprobadoPor'] = req.data['data']['AprobadoPor']
   fields['FirmaAprobado'] = req.data['data']['FirmaAprobado']
   fields['PuestoAprobado'] = req.data['data']['PuestoAprobado']  
   fields['IDProcedimiento'] = M.Procedimiento.objects.filter(Objetivo=req.data['data']['IDProcedimiento']).values('ID')[0]['ID'] if req.data['data']['IDProcedimiento'] else None   
   updatedObj = M.RevAprobacion(pk=req.data['data']['ID'],**fields)
   updatedObj.save()                    
  return Response(json.dumps({'data':data}))
 
 def delete(self,req):
  print('---->',req.data['ID'])
  objToDelete = M.RevAprobacion.objects.get(pk=req.data['ID'])
  objToDelete.delete()
  return Response({'response':'ok'}) 

 def list(self, req):
  data = serializers.serialize('json',M.RevAprobacion.objects.all())
  if data == '[]':
   data = M.RevAprobacion.__doc__
   data = data.replace(' ','')
   data = data.replace('(','')
   data = data.replace(')','')
   data = data.replace('Rev_Aprobacion','')
   data = data.split(',')  
   data.append('statusEmpty')
   data.append({'route':'revaprobacion'})  
  return Response(data)


class HistorialCambioView(viewsets.ViewSet):
 
 fieldsSchema = {
  'fields':[{'name':'Version', 'null':True, 'maxLength':4, 'needsToBeUnique':False, 'type':'decimal'},
            {'name':'Descripcion', 'null':True, 'maxLength':500, 'needsToBeUnique':False, 'type':'str'},
            {'name':'IDProcedimiento', 'null':True, 'maxLength':False, 'needsToBeUnique':False, 'type':'select'}]
 }

 relations = {
   'any':True,
   'to':[{'name':'Procedimiento', 'column':'Objetivo', 'from':'IDProcedimiento'}]
  } 
 
 def create(self,req):
  data = ''
  relationsData = []
  
  if req.data['mode'] == 'relations':
   if self.relations['any']:
    for relationDetails in self.relations['to']:
      relationRecords = list(eval('M.%s'%relationDetails['name']).objects.all().values(relationDetails['column']))
      if relationRecords:
       relationsData.append(relationRecords)
       relationsData[-1][0]['table'] = relationDetails['name']
   data = {'schema':self.fieldsSchema, 'relations':relationsData if relationsData else []}
  elif req.data['mode'] == 'create':
   fields = {}
   fields['Version'] = req.data['data']['Version']
   fields['Descripcion'] = req.data['data']['Descripcion']
   fields['IDProcedimiento'] = M.Procedimiento.objects.filter(Objetivo=req.data['data']['IDProcedimiento']).values('ID')[0]['ID'] if req.data['data']['IDProcedimiento'] else None
   M.HistorialCambios.objects.create(**fields)
  elif req.data['mode'] == 'requestUpdateData':
   obj = M.HistorialCambios.objects.get(pk=req.data['ID']['current'])
   data = {}
   data['Version'] = str(obj.Version)
   data['Descripcion'] = obj.Descripcion
   data['Fecha'] = str(obj.Fecha)
   data['IDProcedimiento'] = obj.IDProcedimiento   
  elif req.data['mode'] == 'update':
   pass
   fields = {}
   fields['Version'] = req.data['data']['Version']
   fields['Descripcion'] = req.data['data']['Descripcion'] 
   fields['Fecha'] = datetime.strptime(req.data['data']['Fecha'], "%Y-%m-%d").date()     
   fields['IDProcedimiento'] = M.Procedimiento.objects.filter(Objetivo=req.data['data']['IDProcedimiento']).values('ID')[0]['ID'] if req.data['data']['IDProcedimiento'] else None   
   updatedObj = M.HistorialCambios(pk=req.data['data']['ID'],**fields)
   updatedObj.save()   
  return Response(json.dumps({'data':data}))
 
 def delete(self,req):
  print('---->',req.data['ID'])
  objToDelete = M.HistorialCambios.objects.get(pk=req.data['ID'])
  objToDelete.delete()
  return Response({'response':'ok'}) 

 def list(self, req):
  data = serializers.serialize('json',M.HistorialCambios.objects.all())
  if data == '[]':
   data = M.HistorialCambios.__doc__
   data = data.replace(' ','')
   data = data.replace('(','')
   data = data.replace(')','')
   data = data.replace('HistorialCambios','')
   data = data.split(',')  
   data.append('statusEmpty')
   data.append({'route':'historialcambios'})  
  return Response(data)


router = DefaultRouter()

router.register(r'procedimiento', ProcedimientoView, basename='procedimiento')

router.register(r'documentosreferencias', DocumentoReferenciaView, basename='referencia')

router.register(r'documentos', DocumentoView, basename='documento')

router.register(r'responsabilidades', ResponsabilidadesView, basename='responsabilidad')

router.register(r'puestos', PuestoView, basename='puesto')

router.register(r'terminologiasdef', TerminologiaDefView, basename='terminologiasdef')

router.register(r'termino', TerminoView, basename='termino')

router.register(r'descripcionesprocedimiento', DescripcionProcedimientoView, basename='descripcionprocedimiento')

router.register(r'subdescripciones', SubDescripcionView, basename='subdescripcion')

router.register(r'anexos', AnexoView, basename='anexo')

router.register(r'revaprobacion', RevAprobacionView, basename='revaprobacion')

router.register(r'historialcambios', HistorialCambioView, basename='historialcambio')

urlpatterns = router.urls + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)