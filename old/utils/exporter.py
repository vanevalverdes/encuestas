def exportCSV(classid, headers, fields):
   from utils.methods import application, session
   from flask import Response
   import csv
   import io

   # Obtener el nombre de la clase y la consulta
   classname = application.get_class_name(classid)
   query = session.filterTableView(classname)
   tableFieldDict = application.getClazzFields(classname)
   moneyFields = application.getClazzMoneyFields(classname)
   dateFields = application.getClazzDateFields(classname)

   # Obtener los datos de la tabla
   documents = query.getTable()

   # Crear un archivo CSV en memoria
   output = io.StringIO()
   writer = csv.writer(output)

   # Escribir encabezados
   writer.writerow(headers)

   # Escribir los datos de cada registro
   for document in documents:
      fieldsArray = []
      for fieldname in fields:
         # Obtener el valor del campo desde el objeto `document`
         value = getattr(document, fieldname, '')

         # Procesar si el campo es de tipo monetario
         if fieldname in moneyFields:
            value = int(value) / 100.00 if value else 0.00

         # Procesar si el campo es de tipo fecha
         elif fieldname in dateFields:
            value = value.strftime('%Y-%m-%d') if value else ''

         # Agregar el valor procesado al array de campos
         fieldsArray.append(value)

      # Escribir la fila en el archivo CSV
      writer.writerow(fieldsArray)

   # Regresar al inicio del archivo en memoria
   output.seek(0)

   # Enviar el archivo CSV como respuesta para su descarga
   return Response(
      output.getvalue(),
      mimetype='text/csv',
      headers={'Content-Disposition': 'attachment; filename=documents.csv'}
   )