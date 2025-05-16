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
import bcrypt
import magic
import json
import os
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
  #  data['RevAprobacion-RevisadoPor'] = list(M.RevAprobacion.objects.all().values('ID','RevisadoPor'))
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
     procId = relationsObj[0].ID
    else:
     return Response([])
    recordsIterator = lambda columns,toIterate,refTable=None,*userFriendlyColumn:[{prop:(list(eval('M.%s'%(refTable)).objects.filter(pk=record[prop]).values(*userFriendlyColumn))[:1] if 'ID' in prop and len(prop) > 2 else record[prop]) for prop in columns if type(record)==dict and prop in record.keys()} for record in toIterate]

    # relationsObj = list(M.RevAprobacion.objects.filter(IDProcedimiento=procId).values('ID','ElaboradoPor','FirmaElaborado','PuestoElaborado','RevisadoPor','FirmaRevisado','PuestoRevisado','AprobadoPor','FirmaAprobado','PuestoAprobado'))
    # if relationsObj:
    #  specificData['RevAprobacion'] = [[relationsObj[0]['ElaboradoPor'],relationsObj[0]['FirmaElaborado'],relationsObj[0]['PuestoElaborado']], [relationsObj[0]['RevisadoPor'],relationsObj[0]['FirmaRevisado'],relationsObj[0]['PuestoRevisado']], [relationsObj[0]['AprobadoPor'],relationsObj[0]['FirmaAprobado'],relationsObj[0]['PuestoAprobado']],relationsObj[0]['ID']]
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

    relationsObj = M.Documentos.objects.filter(Codigo=req.data['procedCodigo'].strip().replace(' ','')).values('Descripcion','Fecha','Version')
    if relationsObj:specificData['Documentos'] = relationsObj[0]

    data['specificData'] = specificData

  if req.data['mode'] == 'CREATE':
   columnsSchema = {'DocumentosReferencias':['IDDocumento'],'Responsabilidades':['Descripcion','IDPuesto'],'TerminologiasDef':['IDTermino','Descripcion'],'DescripcionesProcedimiento':['Descripcion'],'SubDescripciones':['SubDescripcion','IDDescripcion'],'Anexos':['Codigo','Nombre','Num']}
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
        #  newSubDescrip['Codigo'] = correspondingSubDescrip['Codigo']
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
  proceData = {'columns':[{'title':'Código'},{'title':'Descripcion'},{'title':'Objetivo'},{'title':'Fecha'},{'title':'Version'}],'records':[]}
  for procedRecord in data:
   jointRecord = []
   jointRecord.append(procedRecord['Codigo'].strip().replace(' ',''))
   jointRecord.append(procedRecord['Objetivo'])
   if jointRecord[0]:
    docRecord = list(M.Documentos.objects.filter(Codigo=jointRecord[0]))
    print('----------------xxxxxxxx>',jointRecord[0],len(jointRecord[0]))
    if docRecord:
     jointRecord.append(docRecord[0].Descripcion)
     jointRecord.append(docRecord[0].Fecha)
     jointRecord.append(docRecord[0].Version)
   proceData['records'].append(jointRecord)
  print('----------------------->',proceData['records'])
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
   IDDepartamento = req.data['data']['sequence'].split('-')[1].strip().replace(' ','')
   IDTipoDocumento = req.data['data']['sequence'].split('-')[0].strip().replace(' ','')
   fields['Codigo'] = req.data['data']['Codigo'].strip().replace(' ','')
   fields['Descripcion'] = req.data['data']['Descripcion']
   fields['Version'] = req.data['data']['Version']
   fields['Fecha'] = req.data['data']['Fecha']
   IDTipoDocumento = list(M.TipoDocumento.objects.filter(Codificacion=IDTipoDocumento).values('ID'))
   IDDepartamento = list(M.Departamento.objects.filter(Codigo=IDDepartamento).values('ID'))
   if IDTipoDocumento:fields['IDTipoDocumento'] = IDTipoDocumento[0]['ID']
   if IDDepartamento:fields['IDDepartamento'] = IDDepartamento[0]['ID']

   fields['TipoDoc_Dep_Repr'] = req.data['data']['Codigo']   

   M.Documentos.objects.create(**fields)  
   
  elif req.data['mode'] == 'requestUpdateData':
   obj = M.Documentos.objects.get(Codigo=req.data['ID']['current'])
   data = {}
   data['Codigo'] = obj.Codigo
   data['Descripcion'] = obj.Descripcion
   data['Fecha'] = str(obj.Fecha)
   data['Version'] = obj.Version      
  elif req.data['mode'] == 'update':
   fields = {}
   fields['Codigo'] = req.data['data']['Codigo']
   fields['Descripcion'] = req.data['data']['Descripcion']   
   recordToUpdt = M.Documentos.objects.filter(Codigo=req.data['data']['ID'])
   if recordToUpdt:recordToUpdt.update(**fields) 
  elif req.data['mode'] == 'deleteRecord': 
   objToDel = M.Documentos.objects.filter(Codigo=req.data['documentCode'])
   dependentProced = M.Procedimiento.objects.filter(Codigo=req.data['documentCode'])
   if objToDel:objToDel[0].delete()
   if dependentProced:
    dependentProced = dependentProced[0]
    dependentProced.Codigo = ''
    dependentProced.deleted = True
    dependentProced.save()
    return Response({'status':'ok','message':'procedDependent'})
   return Response({'status':'ok','message':False})
  return Response(json.dumps({'data':data}))
 
 def delete(self,req):
  pass
  # print('------->',req.data['ID'])
  # objToDelete = M.Documentos.objects.get(pk=req.data['ID'])
  # objToDelete.delete()
  # return Response({'response':'ok'}) 
 
 def list(self, req):
  data = {'columns':[{'title':'Código'},{'title':'Descripcion'},{'title':'Fecha'},{'title':'Versión'}],'records':[]}
  unparsedData = list(M.Documentos.objects.all().values('Codigo','Descripcion','Fecha','Version'))
  for unparsedRecord in unparsedData:
   data['records'].append(unparsedRecord.values())
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
   createdObj = M.Puestos.objects.create(**fields)
   return Response({'msg':'ok','ID':createdObj.pk,'Descripcion':createdObj.Descripcion})
  elif req.data['mode'] == 'requestUpdateData':
   obj = M.Puestos.objects.get(Descripcion=req.data['ID']['current'])
   data = {}
   data['Descripcion'] = obj.Descripcion
   data['UnidadNegocio'] = obj.UnidadNegocio
   data['Actividad'] = obj.Actividad
  elif req.data['mode'] == 'update':
   fields = {}
   fields['UnidadNegocio'] = req.data['data']['UnidadNegocio']
   fields['Descripcion'] = req.data['data']['Descripcion']   
   fields['Actividad'] = req.data['data']['Actividad']
   recordToUpdt = M.Puestos.objects.filter(Descripcion=req.data['data']['ID'])
   if recordToUpdt:recordToUpdt.update(**fields)
  return Response(json.dumps({'data':data}))
 
 def delete(self,req):
  print('----->',req.data['ID'])
  objToDelete = M.Puestos.objects.get(pk=req.data['ID'])
  objToDelete.delete()
  return Response({'response':'ok'}) 

 def list(self, req):
  data = {'columns':[{'title':'Descripcion'},{'title':'Unidad Negocio'},{'title':'Actividad'}],'records':[]}
  unparsedData = list(M.Puestos.objects.all().values('Descripcion','UnidadNegocio','Actividad'))
  for unparsedRecord in unparsedData:
   data['records'].append(unparsedRecord.values())
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
   createdObj = M.Termino.objects.create(**fields)   
   return Response({'msg':'ok','ID':createdObj.pk,'Descripcion':createdObj.Descripcion})    
  elif req.data['mode'] == 'requestUpdateData':
   obj = M.Termino.objects.get(Descripcion=req.data['ID']['current'])
   data = {}
   data['Descripcion'] = obj.Descripcion
   data['DescripcionGeneral'] = obj.DescripcionGeneral   
  elif req.data['mode'] == 'update':
   fields = {}
   fields['Descripcion'] = req.data['data']['Descripcion']   
   fields['DescripcionGeneral'] = req.data['data']['DescripcionGeneral']
   recordToUpdt = M.Termino.objects.filter(Descripcion=req.data['data']['ID'])
   if recordToUpdt:recordToUpdt.update(**fields)
  return Response(json.dumps({'data':data}))
 
 def list(self, req):
  data = {'columns':[{'title':'Descripción'},{'title':'Descripción General'}],'records':[]}
  unparsedData = list(M.Termino.objects.all().values('Descripcion','DescripcionGeneral'))
  for unparsedRecord in unparsedData:
   data['records'].append(unparsedRecord.values())
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
  #  fields['Codigo'] = req.data['data']['Codigo']
   fields['Descripcion'] = req.data['data']['Descripcion']
   fields['IDProcedimiento'] = M.Procedimiento.objects.filter(Objetivo=req.data['data']['IDProcedimiento']).values('ID')[0]['ID'] if req.data['data']['IDProcedimiento'] else None
   M.DescripcionesProcedimiento.objects.create(**fields)   
  elif req.data['mode'] == 'requestUpdateData':
   obj = M.DescripcionesProcedimiento.objects.get(pk=req.data['ID']['current'])
   data = {}
  #  data['Codigo'] = obj.Codigo
   data['Descripcion'] = obj.Descripcion
   data['IDProcedimiento'] = obj.IDProcedimiento
  elif req.data['mode'] == 'update':
   fields = {}
  #  fields['Codigo'] = req.data['data']['Codigo']
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
  'fields':[{'name':'Codigo', 'null':True, 'maxLength':50, 'needsToBeUnique':False, 'type':'str'},
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
  #  fields['Codigo'] = req.data['data']['Codigo']
   fields['SubDescripcion'] = req.data['data']['SubDescripcion']
   fields['IDDescripcion'] = M.DescripcionesProcedimiento.objects.filter(Descripcion__iexact=req.data['data']['IDDescripcion'])
   fields['IDDescripcion'] = fields['IDDescripcion'].values()[0]['ID'] if req.data['data']['IDDescripcion'] and fields['IDDescripcion'] else None   
   M.SubDescripciones.objects.create(**fields)
  elif req.data['mode'] == 'requestUpdateData':
   obj = M.SubDescripciones.objects.get(pk=req.data['ID']['current'])
   data = {}
  #  data['Codigo'] = obj.Codigo
   data['SubDescripcion'] = obj.SubDescripcion
   data['IDDescripcion'] = obj.IDDescripcion   
  elif req.data['mode'] == 'update':
   fields = {}
  #  fields['Codigo'] = req.data['data']['Codigo']
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

 def list(self, req):
  pass

 def create(self,req):
  if req.data['mode'] == 'requestFirmaElaboradoFile':
   recToReqImage = M.RevAprobacion.objects.filter(DocumentKey=req.data['documentKey']).filter(FormName=req.data['formName'])
   files = []
   if recToReqImage:
    recToReqImage = recToReqImage[0]
    if recToReqImage.FirmaElaborado:
     return HttpResponse(recToReqImage.FirmaElaborado,content_type='image/png')
  if req.data['mode'] == 'requestFirmaRevisadoFile':
   recToReqImage = M.RevAprobacion.objects.filter(DocumentKey=req.data['documentKey']).filter(FormName=req.data['formName'])
   files = []
   if recToReqImage:
    recToReqImage = recToReqImage[0]
    if recToReqImage.FirmaRevisado:
     return HttpResponse(recToReqImage.FirmaRevisado,content_type='image/png')
  if req.data['mode'] == 'requestFirmaAprobadoFile':
   recToReqImage = M.RevAprobacion.objects.filter(DocumentKey=req.data['documentKey']).filter(FormName=req.data['formName'])
   files = []
   if recToReqImage:
    recToReqImage = recToReqImage[0]
    if recToReqImage.FirmaAprobado:
     return HttpResponse(recToReqImage.FirmaAprobado,content_type='image/png')       
  if req.data['mode'] == 'requestRecord':
   recToReq = {}
   recToReq['Puestos'] = list(M.Puestos.objects.all().values('ID','Descripcion'))
   recordsRenombrator = lambda newColumnNames=None, targetTable=None:[dict(zip(newColumnNames, record.values())) for record in targetTable]
   if 'documentKey' and 'formName' in req.data.keys():
    revAprobacionSpecRec = recordsRenombrator(
     targetTable=M.RevAprobacion.objects.filter(DocumentKey=req.data['documentKey']).filter(FormName=req.data['formName']).values(
    'ElaboradoPor',
    'PuestoElaborado',
    'RevisadoPor',
    'PuestoRevisado',
    'AprobadoPor',
    'PuestoAprobado'),newColumnNames=['Elaborado por','Elaborado Puesto','Revisado por','Revisado Puesto','Aprobado por','Aprobado Puesto'])
     
    if revAprobacionSpecRec:recToReq['revAprobacion'] = revAprobacionSpecRec[0]
   return Response({'msg':'ok','payload':recToReq})

  if req.data['mode'] == 'saveRecord':
   recToUpdt = M.RevAprobacion.objects.filter(DocumentKey=req.data['documentKey']).filter(FormName=req.data['formName'])
   if not recToUpdt:M.RevAprobacion.objects.create(**req.data['payload'])
   else:recToUpdt.update(**req.data['payload'])
  if req.data['mode'] == 'saveImageFile':  
   recordToUpdate = M.RevAprobacion.objects.filter(DocumentKey=req.data['documentKey']).filter(FormName=req.data['formName'])
   if recordToUpdate:
    recordToUpdate = recordToUpdate[0]
   for imageFileKey in req.data.keys():
    if imageFileKey in ['mode','documentKey','formName']:continue
    setattr(recordToUpdate,imageFileKey,req.data[imageFileKey].read())
    recordToUpdate.save()   
  return Response({'msg':'ok'})


class HistorialCambioView(viewsets.ViewSet):
 
 def create(self,req):
  if req.data['mode'] == 'saveRecord':
   formatedDescription = 'Registro/s añadido/s'
   for section in req.data['payload']:
    if type(req.data['payload'][section]) != dict:
     formatedDescription += '\n'
     formatedDescription += '* %s'%req.data['payload'][section]
     formatedDescription += '\n' 
     continue
    else:
     formatedDescription += '\n'
    if section == 'recordsToDelete' or req.data['payload'][section]=={}:continue
    formatedDescription += '%s'%section
    for recordTitle in req.data['payload'][section]:
     formatedRecordString = '*   '  
     for recordProp in req.data['payload'][section][recordTitle]:
      propValue = req.data['payload'][section][recordTitle][recordProp]
      formatedRecordString = formatedRecordString + ' ' + propValue
     formatedDescription = formatedDescription + '\n' + formatedRecordString
   formatedDescription += '\n'
   formatedDescription += 'Registro/s eliminados/s'
   formatedDescription += '\n'
   for section in req.data['payload']['recordsToDelete']:
    for recordDescription in req.data['payload']['recordsToDelete'][section]:
     formatedDescription += '\n'
     formatedDescription += '* %s'%recordDescription
     formatedDescription += '\n'

   newRecordToInsert = {'Version':'','Descripcion':'','FormName':'','DocumentKey':''}
   highestVersion = M.HistorialCambios.objects.filter(FormName=req.data['formName']).order_by('-Version').values('Version')
   if not highestVersion:
    newRecordToInsert['Version'] = '001'
    newRecordToInsert['Descripcion'] = 'Elaboración del documento.'
    newRecordToInsert['DocumentKey'] = req.data['documentKey']   
    newRecordToInsert['FormName'] = req.data['formName']
   else:
    highestVersion = highestVersion[0]['Version']
    highestVersion = int(highestVersion) + 1
    highestVersion = str(highestVersion).zfill(3)
    newRecordToInsert['Version'] = highestVersion
    newRecordToInsert['Descripcion'] = formatedDescription
    newRecordToInsert['DocumentKey'] = req.data['documentKey']
    newRecordToInsert['FormName'] = req.data['formName']
   M.HistorialCambios.objects.create(**newRecordToInsert) 
   return Response({'msg':'ok'})
  
  if req.data['mode'] == 'requestRecords':
   recordsRenombrator = lambda newColumnNames=None, targetTable=None:[dict(zip(newColumnNames, record.values())) for record in targetTable]
   records = recordsRenombrator(targetTable = M.HistorialCambios.objects.filter(FormName=req.data['formName']).filter(DocumentKey=req.data['documentKey']).values('Fecha','Version','Descripcion'),newColumnNames=['Fecha','Versión','Descripción de la creación o modificación del documento'])
   return Response({'msg':'ok','payload':records})
  

class UsuarioView(viewsets.ViewSet):
 def create(self,req):
  user = req.data['cred']['username']
  password = req.data['cred']['password']
  if req.data['mode'] == 'userCreation':
   permisonivel = req.data['cred']['permisonivel']
   readyPass = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
   M.Usuario.objects.create(**{'Nombre':user,'Contrasena':readyPass,'Activo':True,'PermisoNivel':permisonivel})
   return Response({'msg':'ok'})   
  elif req.data['mode'] == 'login': 
   recordsToFilter = list(M.Usuario.objects.filter(Nombre=user))
   for record in recordsToFilter:
    hashedPass = record.Contrasena.tobytes()
    if bcrypt.checkpw(password.encode('utf-8'),hashedPass):return Response({'Nombre':record.Nombre,'Activo':record.Activo,'PermisoNivel':record.PermisoNivel,'msg':'ok'})
  return Response([])
 
class PuestoDescripcionView(viewsets.ViewSet): 
 
 def list(self,req):
  puestoDescriModelRecords = M.DescripcionPuesto.objects.all().values('ID','CodigoPuesto','TituloPuesto','ReportaA','Departamento','Ubicacion')
  payload = {'columns':[{'title':'Codigo Puesto'},{'title':'Titulo Puesto'},{'title':'Reporta a'},{'title':'Departamento'},{'title':'Ubicacion'}],'records':[]}
  for record in puestoDescriModelRecords:
   puestoDescriModelRecord = []
   documentoRel = M.Documentos.objects.filter(pk=record['CodigoPuesto']).values('Codigo')
   puestoRel = M.Puestos.objects.filter(pk=record['TituloPuesto']).values('Descripcion')
   reportaAPuestoRel = M.Puestos.objects.filter(pk=record['ReportaA']).values('Descripcion')
   departamentoRel = M.Departamento.objects.filter(pk=record['Departamento']).values('Codigo','Descripcion')   
   puestoDescriModelRecord.append(documentoRel[0]['Codigo'] if documentoRel else '')
   puestoDescriModelRecord.append(puestoRel[0]['Descripcion'] if puestoRel else '')
   puestoDescriModelRecord.append(reportaAPuestoRel[0]['Descripcion'] if reportaAPuestoRel else '')
   puestoDescriModelRecord.append('%s - %s'%(departamentoRel[0]['Codigo'],departamentoRel[0]['Descripcion']) if departamentoRel else '')
   puestoDescriModelRecord.append(record['Ubicacion'])
   payload['records'].append(puestoDescriModelRecord)
  return Response(payload)

 def create(self,req): 
  if req.data['mode'] == 'savePuestoDescriRecord':
   puestoDescri = ''
   if 'puestoDescriCode' in req.data['payload'].keys():
    documentoPk = M.Documentos.objects.filter(Codigo=req.data['payload']['puestoDescriCode']).values('ID')
    puestoDescri = M.DescripcionPuesto.objects.filter(CodigoPuesto=documentoPk[0]['ID']) if documentoPk else ''
    puestoDescri.update(**req.data['payload']['DescripcionPuesto'])
   else:
    puestoDescri = M.DescripcionPuesto.objects.create(**req.data['payload']['DescripcionPuesto'])
   for dataTable in req.data['payload'].keys():    
    if dataTable in ['puestoDescriCode','DescripcionPuesto','RevAprobacion','historialCambios','Idiomas','recordsToDelete']:continue
    for dataTableRecord in req.data['payload'][dataTable]:
     cleanedRecord = dataTableRecord    
     if 'elementHtml' in cleanedRecord.keys():cleanedRecord.pop('elementHtml')
     cleanedRecord['DescripcionPuesto'] = puestoDescri[0].pk if 'puestoDescriCode' in req.data['payload'].keys() else puestoDescri.pk
     eval('M.%s'%(dataTable)).objects.create(**cleanedRecord)
    for record in req.data['payload']['recordsToDelete']:
     if record.keys():
      tableName = list(record.keys())[0]
      recordToDelete = eval('M.%s'%(tableName)).objects.filter(pk=record[tableName])
      print('----------------------------------xxxxx>',recordToDelete)           
      if recordToDelete:
       recordToDelete[0].delete() 
   if req.data['payload']['Idiomas']:
    puestoDescri = puestoDescri[0].pk if 'puestoDescriCode' in req.data['payload'].keys() else puestoDescri.pk    
    for idioma in req.data['payload']['Idiomas'].keys():
     dbStoredIdioma = M.Idiomas.objects.filter(Descri=idioma)
     if not dbStoredIdioma:
      dbStoredIdioma = {'Descri':idioma,'DescripcionPuesto':puestoDescri}
      dbStoredIdioma = M.Idiomas.objects.create(**dbStoredIdioma)
     else:
      dbStoredIdioma = dbStoredIdioma[0]
     idiomaLinkedSkills = M.IdiomasHabilidades.objects.filter(Idiomas=dbStoredIdioma.pk)
     if not idiomaLinkedSkills:
      M.IdiomasHabilidades.objects.create(**{'Descri':'Leer','Idiomas':dbStoredIdioma.pk})
      M.IdiomasHabilidades.objects.create(**{'Descri':'Hablar','Idiomas':dbStoredIdioma.pk})
      M.IdiomasHabilidades.objects.create(**{'Descri':'Escribir','Idiomas':dbStoredIdioma.pk})
     for idiomaSkills in req.data['payload']['Idiomas'][idioma].keys():
      idiomaLinkedSkills = M.IdiomasHabilidades.objects.filter(Idiomas=dbStoredIdioma.pk)
      for idiomaSkillsValues in req.data['payload']['Idiomas'][idioma][idiomaSkills]:
       specificSkillToUpdt = idiomaLinkedSkills.filter(Descri=idiomaSkills)
       updtData = req.data['payload']['Idiomas'][idioma][idiomaSkills]
       if specificSkillToUpdt:specificSkillToUpdt.update(**updtData)
       print('---------------------->',req.data['payload']['Idiomas'][idioma][idiomaSkills])
   return Response({'msg':'ok'})       
  if req.data['mode'] == 'save_ficha_tecnica':
   recordToUpdate = M.DescripcionPuesto.objects.filter(CodigoPuesto=req.data['puestoDescriCode'])
   if recordToUpdate and type(req.data['file']) != str:
    recordToUpdate[0].OrganigramaFile = req.data['file'].read()
    recordToUpdate[0].save()   
  if req.data['mode'] == 'request_ficha_tecnica':
   documentoPk = M.Documentos.objects.filter(Codigo=req.data['puestoDescriCode']).values('ID')
   puestoDescri = M.DescripcionPuesto.objects.filter(CodigoPuesto=documentoPk[0]['ID']) if documentoPk else ''
   if puestoDescri and puestoDescri[0].OrganigramaFile:
     file = bytes(puestoDescri[0].OrganigramaFile)
     mime = magic.Magic(mime=True)
     tipo_mime = mime.from_buffer(file)    
     return HttpResponse(file,content_type=tipo_mime)
   return Response([])  
  if req.data['mode'] == 'fillForm':
   puestoRecords = M.Puestos.objects.all().values('ID','Descripcion')
   departRecords = M.Departamento.objects.all().values('ID','Descripcion','Codigo')
   docuRecords = list(M.Documentos.objects.filter(Codigo__contains='PEP').exclude(
    Codigo__in=M.Documentos.objects.filter(pk__in=[M.DescripcionPuesto.objects.all().values('CodigoPuesto')]).values('Codigo')
    ).values('ID','Codigo','Descripcion'))
   payload = {}
   payload['Identificacion_CodigoPuesto'] = docuRecords
   payload['Identificacion_TituloPuesto'] = puestoRecords
   payload['Identificacion_ReportaA'] = puestoRecords
   payload['Identificacion_Departamento'] = departRecords
   payload['RelacionesInternas_PuestoSelectID'] = puestoRecords
   payload['RelacionesExternas_PuestoSelectID'] = puestoRecords
   if 'puestoDescriCode' in req.data.keys():   
    selfDocumentCode = list(M.Documentos.objects.filter(Codigo=req.data['puestoDescriCode']).values('ID','Codigo','Descripcion'))
    documentoPk = selfDocumentCode[0]['ID'] if selfDocumentCode else ''
    payload['Identificacion_CodigoPuesto'].extend(selfDocumentCode)
    if documentoPk:
     tempObj = {}
     descripcionPuestoPk = ''
     pkTranslator = lambda targetTable=None, fkTable=None, targetColumn=None, fkColumn=None, newColumnName=None: [
     {**record, newColumnName: fkRecord['Descripcion']}
     for record in targetTable
     for fkRecord in eval('M.%s' % fkTable).objects.filter(pk=record[targetColumn]).values(fkColumn)
     ]       
     recordsRenombrator = lambda newColumnNames=None, targetTable=None:[dict(zip(newColumnNames, record.values())) for record in targetTable]
     tempObj['DescripcionPuesto'] = M.DescripcionPuesto.objects.filter(CodigoPuesto=documentoPk).values('ID','CodigoPuesto','TituloPuesto','ReportaA',
     'Departamento','CodigoDepartamento','Ubicacion','ObjetivoPuesto','OrganigramaDescri','CompeteActituDescr','CompeteTecniIndisDescr')    
     descripcionPuestoPk = tempObj['DescripcionPuesto'][0]['ID']
     tempObj['ActividadesPeriodicasPuesto'] = recordsRenombrator(targetTable=M.ActividadesPeriodicasPuesto.objects.filter(DescripcionPuesto=descripcionPuestoPk).values('ID','ActividadesDescri','ResultadoFinalDescri'),newColumnNames=['ID','Actividad','Resultado final'])
     tempObj['CompeteActituLista'] = recordsRenombrator(targetTable=M.CompeteActituLista.objects.filter(DescripcionPuesto=descripcionPuestoPk).values('ID','Descri','Indispensable','Deseable'),newColumnNames=['ID','Competencias Actitudinales','Grado Indispensable','Deseable'])
     tempObj['CompeteTecniIndisLista'] = recordsRenombrator(targetTable=M.CompeteTecniIndisLista.objects.filter(DescripcionPuesto=descripcionPuestoPk).values('ID','Descri','BuenDominio','DominioBasico'),newColumnNames=['ID','Indispensables para ocupar la posición','Buen Dominio','Dominio Básico'])
     tempObj['Computacion'] = recordsRenombrator(targetTable=M.Computacion.objects.filter(DescripcionPuesto=descripcionPuestoPk).values('ID','Descri','Grado','Indispensable','Deseable'),newColumnNames=['ID','Programa Tecnológico','Grado','Indispensable','Deseable'])     
     tempObj['CondicionesFisicas'] = recordsRenombrator(targetTable=M.CondicionesFisicas.objects.filter(DescripcionPuesto=descripcionPuestoPk).values('ID','Descri'),newColumnNames=['ID','Descripción'])
     tempObj['DecisionesSinAprobacion'] = recordsRenombrator(targetTable=M.DecisionesSinAprobacion.objects.filter(DescripcionPuesto=descripcionPuestoPk).values('ID','Descri'),newColumnNames=['ID','Descripción'])
     tempObj['ExperienciaIdeal'] = recordsRenombrator(targetTable=M.ExperienciaIdeal.objects.filter(DescripcionPuesto=descripcionPuestoPk).values('ID','Descri','Indispensable','Deseable'),newColumnNames=['ID','Experiencia','Indispensable','Deseable'])
     tempObj['FormacionAcademica'] = recordsRenombrator(targetTable=M.FormacionAcademica.objects.filter(DescripcionPuesto=descripcionPuestoPk).values('ID','Descri','Indispensable','Deseable'),newColumnNames=['ID','Nivel educativo','Indispensable','Deseable'])
     tempObj['FuncionesPuesto'] = recordsRenombrator(targetTable=M.FuncionesPuesto.objects.filter(DescripcionPuesto=descripcionPuestoPk).values('ID','FuncionesDescri','ResultadoFinalDescri'),newColumnNames=['ID','Función','Resultado final'])
     tempObj['GradoAutoridadDecisiones'] = recordsRenombrator(targetTable=M.GradoAutoridadDecisiones.objects.filter(DescripcionPuesto=descripcionPuestoPk).values('ID','Descri'),newColumnNames=['ID','Descripción'])
     tempObj['RelacionesExternas'] = recordsRenombrator(targetTable=pkTranslator(targetTable=M.RelacionesExternas.objects.filter(DescripcionPuesto=descripcionPuestoPk).values('ID','Puesto','Descri'), fkTable='Puestos', targetColumn='Puesto', fkColumn='Descripcion', newColumnName='Puesto'),newColumnNames=['ID','Puesto','Descripción'])
     tempObj['RelacionesInternas'] = recordsRenombrator(targetTable=pkTranslator(targetTable=M.RelacionesInternas.objects.filter(DescripcionPuesto=descripcionPuestoPk).values('ID','Puesto','Descri'), fkTable='Puestos', targetColumn='Puesto', fkColumn='Descripcion', newColumnName='Puesto'),newColumnNames=['ID','Puesto','Descripción'])
     tempObj['ResponRecurYMateriales'] = recordsRenombrator(targetTable=M.ResponRecurYMateriales.objects.filter(DescripcionPuesto=descripcionPuestoPk).values('ID','Descri'),newColumnNames=['ID','Recurso o material'])
     tempObj['Riesgos'] = recordsRenombrator(targetTable=M.Riesgos.objects.filter(DescripcionPuesto=descripcionPuestoPk).values('ID','Descri'),newColumnNames=['ID','Descripción'])
     tempObj['Idiomas'] = {}

     puestoDescriIdiomas = M.Idiomas.objects.filter(DescripcionPuesto=descripcionPuestoPk).values('ID','Descri')
     for idioma in puestoDescriIdiomas:
      idiomaValue = idioma['Descri']
      tempObj['Idiomas'][idiomaValue] = {}
      idiomaLinkedSkills = M.IdiomasHabilidades.objects.filter(Idiomas=idioma['ID']).values('Grado','Indispensable','Deseable')
      if idiomaLinkedSkills:
       tempObj['Idiomas'][idiomaValue]['Leer'] = idiomaLinkedSkills.filter(Descri='Leer')[0]
       tempObj['Idiomas'][idiomaValue]['Hablar'] = idiomaLinkedSkills.filter(Descri='Hablar')[0]
       tempObj['Idiomas'][idiomaValue]['Escribir'] = idiomaLinkedSkills.filter(Descri='Escribir')[0]
     payload['specificData'] = {**tempObj}
   return Response({'msg':'ok','payload':payload})
  return Response({}) 

class ManualView(viewsets.ViewSet):
 
 def list(self,req):
  manualRecords = M.Manual.objects.all().values('CodigoManual','ObjetivoGeneralManualDescri','AlcanceDescri')
  parsedManualRecords = []
  for record in manualRecords:
   codigoManual = M.Documentos.objects.filter(pk=record['CodigoManual']).values('Codigo')
   codigoManual = codigoManual[0]['Codigo'] if codigoManual else ''
   parsedManualRecords.append([codigoManual,record['ObjetivoGeneralManualDescri'],record['AlcanceDescri']])
  return Response({'columns':[{'title':'Código manual'},{'title':'Objetivo general del manual'},{'title':'Alcance'}],'records':parsedManualRecords})

 def create(self,req):
  if req.data['mode'] == 'fillForm':
   docuRecords = list(M.Documentos.objects.filter(Codigo__contains='MAN').exclude(
    Codigo__in=M.Documentos.objects.filter(pk__in=[M.Manual.objects.all().values('CodigoManual')]).values('Codigo')
    ).values('ID','Codigo','Descripcion'))
   pkTranslator = lambda targetTable=None, fkTable=None, targetColumn=None, fkColumn=None, newColumnName=None: [
    {**record, newColumnName: fkRecord[fkColumn]}
    for record in targetTable
    for fkRecord in eval('M.%s' % fkTable).objects.filter(pk=record[targetColumn]).values(fkColumn)] 
   payload = {}
   parsedPuestoRecords = []   
   payload['ObjetivoGeneralManual_Codigo'] = docuRecords
   payload['BoundManualesManual'] = pkTranslator(targetTable=M.Manual.objects.all().values('ID','CodigoManual','ObjetivoGeneralManualDescri'),
     fkTable='Documentos',targetColumn='CodigoManual',fkColumn='Codigo',newColumnName='Codigo')
   payload['BoundProcedimiento'] = M.Procedimiento.objects.all().values('ID','Codigo','Objetivo')      
   payload['DescripcionesPuesto_puestoSelect'] = pkTranslator(targetTable=M.DescripcionPuesto.objects.all().values('ID','CodigoPuesto','TituloPuesto'),
     fkTable='Documentos',targetColumn='CodigoPuesto',fkColumn='Codigo',newColumnName='CodigoPuesto')
   for record in payload['DescripcionesPuesto_puestoSelect']:
    parsedPuestoRecords.extend(pkTranslator(targetTable=[record],fkTable='Puestos',targetColumn='TituloPuesto',fkColumn='Descripcion',newColumnName='TituloPuesto'))
   payload['DescripcionesPuesto_puestoSelect'] = parsedPuestoRecords 

   if 'manualCode' in req.data.keys():   
    selfDocumentCode = list(M.Documentos.objects.filter(Codigo=req.data['manualCode']).values('ID','Codigo','Descripcion'))
    documentoPk = selfDocumentCode[0]['ID'] if selfDocumentCode else ''
    payload['ObjetivoGeneralManual_Codigo'].extend(selfDocumentCode)
    if documentoPk:
     tempObj = {}
     manualPk = ''
     pkTranslator = lambda targetTable=None, fkTable=None, targetColumn=None, fkColumn=None, newColumnName=None: [
     {**record, newColumnName: fkRecord['Descripcion']}
     for record in targetTable
     for fkRecord in eval('M.%s' % fkTable).objects.filter(pk=record[targetColumn]).values(fkColumn)
     ]
     recordsRenombrator = lambda newColumnNames=None, targetTable=None:[dict(zip(newColumnNames, record.values())) for record in targetTable]
     tempObj['Manual'] = M.Manual.objects.filter(CodigoManual=documentoPk).values('ID','CodigoManual','ObjetivoGeneralManualDescri','ObjetivoEspecificoManualDescri','AlcanceDescri',
     'ObjetivoGeneralUnidadNegocio','MapaProcesoDescri','EstructuraProcesoDescri','OrganigramaEstructuralDescri','OrganigramaFuncionalDescri','PresupuestoDescri','PresupuestoSecondDescri',
     'RendicionCuentaDescri','IndicadorProcesoGestionRiesgoDescri')    
     tempObj['Manual'] = tempObj['Manual'][0] if tempObj['Manual'] else ''
     manualPk = tempObj['Manual']['ID']
     tempObj['ObjetivoEspecificoManualLista'] = recordsRenombrator(targetTable=M.ObjetivoEspecificoManualLista.objects.filter(Manual=manualPk).values('ID','Descri'),newColumnNames=['ID','Objetivo'])
     tempObj['MarcoLegal'] = recordsRenombrator(targetTable=M.MarcoLegal.objects.filter(Manual=manualPk).values('ID','Descri'),newColumnNames=['ID','Marco legal y regulatorio'])
     tempObj['ObjetivoEspecificoUnidadNegocio'] = recordsRenombrator(targetTable=M.ObjetivoEspecificoUnidadNegocio.objects.filter(Manual=manualPk).values('ID','Descri'),newColumnNames=['ID','Objetivo específico'])     
     tempObj['DescripcionPuestoManual'] = recordsRenombrator(targetTable=M.DescripcionPuestoManual.objects.filter(Manual=manualPk).values('ID','Codigo','Descri'),newColumnNames=['ID','Codificación Interna','Descripción de puesto'])
     tempObj['ClienteInterno'] = recordsRenombrator(targetTable=M.ClienteInterno.objects.filter(Manual=manualPk).values('ID','Cliente','Necesidad','Expectativa'),newColumnNames=['ID','Cliente','Necesidad','Expectativa'])
     tempObj['ClienteExterno'] = recordsRenombrator(targetTable=M.ClienteExterno.objects.filter(Manual=manualPk).values('ID','Cliente','Necesidad','Expectativa'),newColumnNames=['ID','Cliente','Necesidad','Expectativa'])
     tempObj['ComunicacionInterna'] = recordsRenombrator(targetTable=M.ComunicacionInterna.objects.filter(Manual=manualPk).values('ID','Periodicidad','TipoComunicacion'),newColumnNames=['ID','Periodicidad','Tipo de comunicación'])
     tempObj['ComunicacionExterna'] = recordsRenombrator(targetTable=M.ComunicacionExterna.objects.filter(Manual=manualPk).values('ID','Periodicidad','TipoComunicacion'),newColumnNames=['ID','Periodicidad','Tipo de comunicación'])
     tempObj['CategorizacionGasto'] = recordsRenombrator(targetTable=M.CategorizacionGasto.objects.filter(Manual=manualPk).values('ID','Descri','Sigla'),newColumnNames=['ID','Descripción','Sigla'])
     tempObj['CategorizacionGastoPartida'] = M.CategorizacionGastoPartida.objects.filter(Manual=manualPk).values('ID','Descri','Sigla')
     tempObj['BoundManual'] = recordsRenombrator(targetTable=M.BoundManual.objects.filter(Manual=manualPk).values('ID','Codigo','Descri'),newColumnNames=['ID','Nomenclatura','Referencia del documento'])
     tempObj['BoundProcedimiento'] = recordsRenombrator(targetTable=M.BoundProcedimiento.objects.filter(Manual=manualPk).values('ID','Codigo','Descri'),newColumnNames=['ID','Nomenclatura','Referencia del documento'])
     tempObj['RendicionCuentaLista'] = recordsRenombrator(targetTable=M.RendicionCuentaLista.objects.filter(Manual=manualPk).values('ID','Descri'),newColumnNames=['ID','Elemento'])

     associatedGastoPartidaRecords = []
     for record in tempObj['CategorizacionGasto']:
      associatedGastoPartidaRecords.extend(tempObj['CategorizacionGastoPartida'].filter(CategorizacionGasto=record['ID']))
     if associatedGastoPartidaRecords:
      tempObj['CategorizacionGastoPartida'] = recordsRenombrator(targetTable=associatedGastoPartidaRecords,newColumnNames=['ID','Descripción','Sigla'])

     payload['specificData'] = {**tempObj}
   return Response({'msg':'ok','payload':payload})

  if req.data['mode'] == 'saveManualRecord':
   manual = ''
   if 'CodigoManual' in req.data['payload'].keys():
    documentoPk = M.Documentos.objects.filter(Codigo=req.data['payload']['CodigoManual']).values('ID')
    manual = M.Manual.objects.filter(CodigoManual=documentoPk[0]['ID']) if documentoPk else ''
    manual.update(**req.data['payload']['Manual'])
   else:
    manual = M.Manual.objects.create(**req.data['payload']['Manual'])
   for dataTable in req.data['payload'].keys():    
    if dataTable in ['CodigoManual','Manual','CategorizacionGastoPartida','RevAprobacion','historialCambios','recordsToDelete']:continue
    for dataTableRecord in req.data['payload'][dataTable]:
     cleanedRecord = dataTableRecord
     print('----------------------------------xxxxx>',dataTableRecord)     
     if 'elementHtml' in cleanedRecord.keys():cleanedRecord.pop('elementHtml')
     cleanedRecord['Manual'] = manual[0].pk if 'CodigoManual' in req.data['payload'].keys() else manual.pk
     eval('M.%s'%(dataTable)).objects.create(**cleanedRecord)
    for record in req.data['payload']['recordsToDelete']:
     if record.keys():
      tableName = list(record.keys())[0]
      recordToDelete = eval('M.%s'%(tableName)).objects.filter(pk=record[tableName])
      print('----------------------------------xxxxx>',recordToDelete)           
      if recordToDelete:
       recordToDelete[0].delete() 
   
   if req.data['payload']['CategorizacionGastoPartida']:
    for record in req.data['payload']['CategorizacionGastoPartida']:        
     cleanedCategGastoPartRecord = dict(record)
     if 'elementHtml' in cleanedCategGastoPartRecord.keys():cleanedCategGastoPartRecord.pop('elementHtml')     
     if 'parentCategObj' in cleanedCategGastoPartRecord.keys():cleanedCategGastoPartRecord.pop('parentCategObj')     
     if 'parentCategObj' in record.keys():
      parentCategObjId = ''
      checkParentCategObjExists = M.CategorizacionGasto.objects.filter(Sigla=record['parentCategObj']['Sigla']).values('ID')
      if checkParentCategObjExists:
       parentCategObjId = checkParentCategObjExists[0]['ID']
      else:
       parentCategObj = {**record['parentCategObj'],'Manual':manual[0].pk if 'CodigoManual' in req.data['payload'].keys() else manual.pk}
       parentCategObjId = M.CategorizacionGasto.objects.create(**parentCategObj)
       parentCategObjId = parentCategObjId.ID
      cleanedCategGastoPartRecord['CategorizacionGasto'] = parentCategObjId
      cleanedCategGastoPartRecord['Manual'] = manual[0].pk if 'CodigoManual' in req.data['payload'].keys() else manual.pk
      M.CategorizacionGastoPartida.objects.create(**cleanedCategGastoPartRecord) 

  if req.data['mode'] == 'saveManualFiles':
   recordToUpdate = M.Manual.objects.filter(CodigoManual=req.data['manualCode'])
   if recordToUpdate:
    recordToUpdate = recordToUpdate[0]
    for imageFileKey in req.data.keys():
     if imageFileKey in ['mode','manualCode']:continue
     setattr(recordToUpdate,imageFileKey,req.data[imageFileKey].read())
    recordToUpdate.save()
  # if req.data['mode'] == 'save_mapaProcesoFile':   
  #  recordToUpdate = M.Manual.objects.filter(CodigoManual=req.data['manualCode'])
  #  if recordToUpdate and type(req.data['file']) != str:
  #   
  #   recordToUpdate[0].MapaProcesoFile = req.data['file'].read()
  #   recordToUpdate[0].save()
  if req.data['mode'] == 'request_mapaprocesoFile':   
   manual = M.Manual.objects.filter(pk=req.data['manualCode'])
   if manual and manual[0].MapaProcesoFile:
     file = bytes(manual[0].MapaProcesoFile)
     mime = magic.Magic(mime=True)
     tipo_mime = mime.from_buffer(file)    
     return HttpResponse(file,content_type=tipo_mime)
  if req.data['mode'] == 'request_estructuraprocesoFile':   
   manual = M.Manual.objects.filter(pk=req.data['manualCode'])
   if manual and manual[0].EstructuraProcesoFile:
     file = bytes(manual[0].EstructuraProcesoFile)
     mime = magic.Magic(mime=True)
     tipo_mime = mime.from_buffer(file)    
     return HttpResponse(file,content_type=tipo_mime)
  if req.data['mode'] == 'request_organigramaEstructuralFile':   
   manual = M.Manual.objects.filter(pk=req.data['manualCode'])
   if manual and manual[0].OrganigramaEstructuralFile:
     file = bytes(manual[0].OrganigramaEstructuralFile)
     mime = magic.Magic(mime=True)
     tipo_mime = mime.from_buffer(file)    
     return HttpResponse(file,content_type=tipo_mime)
  if req.data['mode'] == 'request_organigramaFuncionalFile':   
   manual = M.Manual.objects.filter(pk=req.data['manualCode'])
   if manual and manual[0].OrganigramaFuncionalFile:
     file = bytes(manual[0].OrganigramaFuncionalFile)
     mime = magic.Magic(mime=True)
     tipo_mime = mime.from_buffer(file)    
     return HttpResponse(file,content_type=tipo_mime)
  if req.data['mode'] == 'request_IndicadorProcesoGestionFile':   
   print('----------------------------->>...>>IndicadorProcesoGestionFile')   
   manual = M.Manual.objects.filter(pk=req.data['manualCode'])
   if manual and manual[0].IndicadorProcesoGestion:
     file = bytes(manual[0].IndicadorProcesoGestion)
     mime = magic.Magic(mime=True)
     tipo_mime = mime.from_buffer(file)    
     return HttpResponse(file,content_type=tipo_mime)
  if req.data['mode'] == 'request_IndicadorProcesoGestionRiesgoFile':   
   print('----------------------------->>...>>IndicadorProcesoGestionRiesgoFile')
   manual = M.Manual.objects.filter(pk=req.data['manualCode'])
   if manual and manual[0].IndicadorProcesoGestionRiesgoFile:
     file = bytes(manual[0].IndicadorProcesoGestionRiesgoFile)
     mime = magic.Magic(mime=True)
     tipo_mime = mime.from_buffer(file)    
     return HttpResponse(file,content_type=tipo_mime)             

  return Response({'msg':'ok'})
  
class PoliticaView(viewsets.ViewSet):
 
 def list(self,req):
  PoliticaRecords = M.Politica.objects.all().values('CodigoPolitica','ObjetivoDescri','AlcanceDescri')
  parsedPoliticaRecords = []
  for record in PoliticaRecords:
   codigoPolitica = M.Documentos.objects.filter(pk=record['CodigoPolitica']).values('Codigo')
   codigoPolitica = codigoPolitica[0]['Codigo'] if codigoPolitica else ''
   parsedPoliticaRecords.append([codigoPolitica,record['ObjetivoDescri'],record['AlcanceDescri']])
  return Response({'columns':[{'title':'Código politica'},{'title':'Objetivo general de la politica'},{'title':'Alcance de la politica'}],'records':parsedPoliticaRecords}) 
 
 def create(self,req): 
  if req.data['mode'] == 'fillForm':
   docuRecords = list(M.Documentos.objects.filter(Codigo__contains='POL').exclude(
    Codigo__in=M.Documentos.objects.filter(pk__in=[M.Politica.objects.all().values('CodigoPolitica')]).values('Codigo')
    ).values('ID','Codigo','Descripcion'))
   pkTranslator = lambda targetTable=None, fkTable=None, targetColumn=None, fkColumn=None, newColumnName=None: [
    {**record, newColumnName: fkRecord[fkColumn]}
    for record in targetTable
    for fkRecord in eval('M.%s' % fkTable).objects.filter(pk=record[targetColumn]).values(fkColumn)] 
   payload = {}
   payload['ObjetivoPolitica_CodigoPolitica'] = docuRecords
   payload['ObjetivoPolitica_DocumentosReferenciasPolitica'] = M.Documentos.objects.all().values('ID','Codigo','Descripcion')
   payload['ResponsabilidadesPolitica_Puesto'] = M.Puestos.objects.all().values('ID','Descripcion')      
   payload['TerminologiaDefinicionesPolitica_Termino'] = M.Termino.objects.all().values('ID','Descripcion')
   payload['Proveedores_Procedimientos'] = M.Procedimiento.objects.all().values('ID','Codigo','Objetivo')   

   if 'CodigoPolitica' in req.data.keys():   
    selfDocumentCode = list(M.Documentos.objects.filter(Codigo=req.data['CodigoPolitica']).values('ID','Codigo','Descripcion'))
    documentoPk = selfDocumentCode[0]['ID'] if selfDocumentCode else ''
    payload['ObjetivoPolitica_CodigoPolitica'].extend(selfDocumentCode)
    if documentoPk:
     tempObj = {}
     politicaPk = ''
     recordsRenombrator = lambda newColumnNames=None, targetTable=None:[dict(zip(newColumnNames, record.values())) for record in targetTable]
     tempObj['Politica'] = M.Politica.objects.filter(CodigoPolitica=documentoPk).values('ID','CodigoPolitica','ObjetivoDescri','AlcanceDescri','ClasificacionPoliticaDescri','PrecioCompra','HorarioRecibo','ProveedoresDescri','PagoDescri')    
     tempObj['Politica'] = tempObj['Politica'][0] if tempObj['Politica'] else ''
     politicaPk = tempObj['Politica']['ID']
     tempObj['DocumentosReferenciasPolitica'] = recordsRenombrator(targetTable=pkTranslator(targetTable=M.DocumentosReferenciasPolitica.objects.filter(Politica=politicaPk).values('ID','IDDocumento'), fkTable='Documentos', targetColumn='IDDocumento', fkColumn='Descripcion', newColumnName='Documentos'), newColumnNames=['ID','na','Documentos'])
     tempObj['ResponsabilidadesPolitica'] = recordsRenombrator(targetTable=pkTranslator(targetTable=M.ResponsabilidadesPolitica.objects.filter(Politica=politicaPk).values('ID','Indice','Puesto','Descri'), fkTable='Puestos', targetColumn='Puesto', fkColumn='Descripcion', newColumnName='Puesto'),newColumnNames=['ID','Indice','Puesto','Descripción'])
     tempObj['TerminologiasPolitica'] = recordsRenombrator(targetTable=pkTranslator(targetTable=M.TerminologiasPolitica.objects.filter(Politica=politicaPk).values('ID','Termino','Descri'), fkTable='Termino', targetColumn='Termino', fkColumn='Descripcion', newColumnName='Termino'),newColumnNames=['ID','Termino','Descripción'])
    #  tempObj['TerminologiasPolitica'] = M.TerminologiasPolitica.objects.filter(Politica=politicaPk).values('ID','Termino','Descri')
     tempObj['ClasificacionTipoMaterialPolitica'] = recordsRenombrator(targetTable=M.ClasificacionTipoMaterialPolitica.objects.filter(Politica=politicaPk).values('ID','Categoria','TipoMaterial','Descri'),newColumnNames=['ID','Categoria','TipoMaterial','Descripción'])
     tempObj['BoundProcedimientosPolitica'] = recordsRenombrator(targetTable=M.BoundProcedimientosPolitica.objects.filter(Politica=politicaPk).values('ID','Codigo','Descri'),newColumnNames=['ID','Código','Descripción'])
     tempObj['AnexoPolitica'] = recordsRenombrator(targetTable=M.AnexoPolitica.objects.filter(Politica=politicaPk).values('ID','Numero','Descri','Codigo'),newColumnNames=['ID','No.','Nombre','Código'])     
     payload['specificData'] = {**tempObj}
   return Response({'msg':'ok','payload':payload})
  if req.data['mode'] == 'savePoliticaRecord':
   politica = ''
   if 'CodigoPolitica' in req.data['payload'].keys():
    documentoPk = M.Documentos.objects.filter(Codigo=req.data['payload']['CodigoPolitica']).values('ID')
    politica = M.Politica.objects.filter(CodigoPolitica=documentoPk[0]['ID']) if documentoPk else ''
    politica.update(**req.data['payload']['Politica'])
   else:
    politica = M.Politica.objects.create(**req.data['payload']['Politica'])
   for dataTable in req.data['payload'].keys():    
    if dataTable in ['CodigoPolitica','Politica','RevAprobacion','historialCambios','recordsToDelete']:continue
    for dataTableRecord in req.data['payload'][dataTable]:
     cleanedRecord = dataTableRecord
     print('----------------------------------x>',dataTableRecord)     
     if 'elementHtml' in cleanedRecord.keys():cleanedRecord.pop('elementHtml')
     cleanedRecord['Politica'] = politica[0].pk if 'CodigoPolitica' in req.data['payload'].keys() else politica.pk
     eval('M.%s'%(dataTable)).objects.create(**cleanedRecord)
    for record in req.data['payload']['recordsToDelete']:
     if record.keys():
      tableName = list(record.keys())[0]
      recordToDelete = eval('M.%s'%(tableName)).objects.filter(pk=record[tableName])
      print('----------------------------------xxxxx>',recordToDelete)           
      if recordToDelete:
       recordToDelete[0].delete()  
  if req.data['mode'] == 'save_tipo_politica':
   recordToUpdate = M.Politica.objects.filter(CodigoPolitica=req.data['codigoPolitica'])
   if recordToUpdate and type(req.data['file']) != str:
    recordToUpdate[0].TipoPoliticaFile = req.data['file'].read()
    recordToUpdate[0].save()   
  if req.data['mode'] == 'request_tipo_politica':
   documentoPk = M.Documentos.objects.filter(Codigo=req.data['codigoPolitica']).values('ID')
   politica = M.Politica.objects.filter(CodigoPolitica=documentoPk[0]['ID']) if documentoPk else ''
   if politica and politica[0].TipoPoliticaFile:       
     file = bytes(politica[0].TipoPoliticaFile)
     mime = magic.Magic(mime=True)
     tipo_mime = mime.from_buffer(file)    
     return HttpResponse(file,content_type=tipo_mime)
   return Response([])
  return Response({'msg':'ok'})
 
class InstructivoView(viewsets.ViewSet):
 
 def list(self,req):
  InstructivoRecords = M.Instructivo.objects.all().values('CodigoInstructivo','ObjetivoDescri','AlcanceDescri')
  parsedInstructivoRecords = []
  for record in InstructivoRecords:
   codigoInstructivo = M.Documentos.objects.filter(pk=record['CodigoInstructivo']).values('Codigo')
   codigoInstructivo = codigoInstructivo[0]['Codigo'] if codigoInstructivo else ''
   parsedInstructivoRecords.append([codigoInstructivo,record['ObjetivoDescri'],record['AlcanceDescri']])
  return Response({'columns':[{'title':'Código del instructivo'},{'title':'Objetivo general del instructivo'},{'title':'Alcance del instructivo'}],'records':parsedInstructivoRecords})
 
 def create(self,req):
  if req.data['mode'] == 'fillForm':
   docuRecords = list(M.Documentos.objects.filter(Codigo__contains='INS').exclude(
    Codigo__in=M.Documentos.objects.filter(pk__in=[M.Instructivo.objects.all().values('CodigoInstructivo')]).values('Codigo')
    ).values('ID','Codigo','Descripcion'))
   pkTranslator = lambda targetTable=None, fkTable=None, targetColumn=None, fkColumn=None, newColumnName=None: [
    {**record, newColumnName: fkRecord[fkColumn]}
    for record in targetTable
    for fkRecord in eval('M.%s' % fkTable).objects.filter(pk=record[targetColumn]).values(fkColumn)] 
   payload = {}
   payload['Instructivo_CodigoInstructivo'] = docuRecords  

   if 'CodigoInstructivo' in req.data.keys():   
    selfDocumentCode = list(M.Documentos.objects.filter(Codigo=req.data['CodigoInstructivo']).values('ID','Codigo','Descripcion'))
    documentoPk = selfDocumentCode[0]['ID'] if selfDocumentCode else ''
    payload['Instructivo_CodigoInstructivo'].extend(selfDocumentCode)
    if documentoPk:
     tempObj = {}
     instructivoPk = ''
     recordsRenombrator = lambda newColumnNames=None, targetTable=None:[dict(zip(newColumnNames, record.values())) for record in targetTable]
     tempObj['Instructivo'] = M.Instructivo.objects.filter(CodigoInstructivo=documentoPk).values('ID','CodigoInstructivo','ObjetivoDescri','AlcanceDescri')    
     tempObj['Instructivo'] = tempObj['Instructivo'][0] if tempObj['Instructivo'] else ''
     instructivoPk = tempObj['Instructivo']['ID']
     tempObj['InstructivoInstrucciones'] = recordsRenombrator(targetTable=M.InstructivoInstrucciones.objects.filter(Instructivo=instructivoPk).values('ID','Indice','Descri'),newColumnNames=['ID','Indice','Descripción'])
     tempObj['InstructivoAnexo'] = recordsRenombrator(targetTable=M.InstructivoAnexo.objects.filter(Instructivo=instructivoPk).values('ID','Numero','Descri','Codigo'),newColumnNames=['ID','No.','Nombre','Código'])
     payload['specificData'] = {**tempObj}
   return Response({'msg':'ok','payload':payload})

  if req.data['mode'] == 'saveInstructivoRecord':
   instructivo = ''
   if 'CodigoInstructivo' in req.data['payload'].keys():
    documentoPk = M.Documentos.objects.filter(Codigo=req.data['payload']['CodigoInstructivo']).values('ID')
    instructivo = M.Instructivo.objects.filter(CodigoInstructivo=documentoPk[0]['ID']) if documentoPk else ''
    instructivo.update(**req.data['payload']['Instructivo'])
   else:
    instructivo = M.Instructivo.objects.create(**req.data['payload']['Instructivo'])
   for dataTable in req.data['payload'].keys():    
    if dataTable in ['CodigoInstructivo','Instructivo','RevAprobacion','historialCambios','recordsToDelete']:continue
    for dataTableRecord in req.data['payload'][dataTable]:
     cleanedRecord = dataTableRecord
     print('----------------------------------x>',dataTableRecord)     
     if 'elementHtml' in cleanedRecord.keys():cleanedRecord.pop('elementHtml')
     cleanedRecord['Instructivo'] = instructivo[0].pk if 'CodigoInstructivo' in req.data['payload'].keys() else instructivo.pk
     eval('M.%s'%(dataTable)).objects.create(**cleanedRecord)
    for record in req.data['payload']['recordsToDelete']:
     if record.keys():
      tableName = list(record.keys())[0]
      recordToDelete = eval('M.%s'%(tableName)).objects.filter(pk=record[tableName])
      print('----------------------------------xxxxx>',recordToDelete)           
      if recordToDelete:
       recordToDelete[0].delete()

  return Response({'msg':'ok'})
 

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

router.register(r'usuario', UsuarioView, basename='usuario')

router.register(r'puestodescripcion', PuestoDescripcionView, basename='puestodescripcion')

router.register(r'manual', ManualView, basename='manual')

router.register(r'politica', PoliticaView, basename='politica')

router.register(r'instructivo', InstructivoView, basename='instructivo')

urlpatterns = router.urls + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)