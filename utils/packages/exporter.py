def exportCSV(documents, headers, fields):
   from utils.packages import application, session
   from flask import Response
   import csv
   import io


 
   # Crear un archivo CSV en memoria
   output = io.StringIO()
   writer = csv.writer(output)

   # Escribir encabezados
   writer.writerow(headers)

   # Escribir los datos de cada registro
   for document in documents:
      document = document.getORMRecord()
      fieldsArray = []
      for fieldname in fields:
         # Obtener el valor del campo desde el objeto `document`
         value = getattr(document, fieldname, '')

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