def field_count(field, value, gender=None):
    from utils.methods import session
    query = session.newQuery("survey")
    query.addFilter(field, "==", value)
    if gender:
        query.addFilter("gender", "==", gender)
    return query.count()

def field_count_user(field, value, user, gender=None):
    from utils.methods import session
    query = session.newQuery("survey")
    query.addFilter(field, "==", value)
    query.addFilter("createdby_id", "==", user)
    if gender:
        query.addFilter("gender", "==", gender)
    return query.count()

def countbygender(fieldname,values):
    
    ### Cuenta por campo y género
    counts = {
        field: [
            field_count(fieldname, field, "A. Masculino"),
            field_count(fieldname, field, "B. Femenino"),
            field_count(fieldname, field)
        ]
        for field in values
    }

    # Cuenta totales para calculo de porcentajes
    totalhombres = 0
    totalmujeres = 0
    totalfield = 0
    for item in counts.values():
        totalhombres += item[0]
        totalmujeres += item[1]
        totalfield += item[2]
    
    # Añade porcentajes para el campo
    for item in counts.values():
        hombresPorc = round((float(item[0]) / float(totalhombres) * 100.0), 2) if totalhombres > 0 else 0.0
        mujeresPorc = round((float(item[1]) / float(totalmujeres) * 100.0), 2) if totalmujeres > 0 else 0.0
        fieldPorc = round((float(item[2]) / float(totalfield) * 100.0), 2) if totalfield > 0 else 0.0

        item.extend([hombresPorc, mujeresPorc, fieldPorc])
    
    # Añade datos por usuario
    userCreation_groups = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15"]
    for field, values in counts.items():
        usersValues = {}
        for user in userCreation_groups:
            userArray = [
                field_count_user(fieldname, field, user, "A. Masculino"),
                field_count_user(fieldname, field, user, "B. Femenino"),
                field_count_user(fieldname, field, user)
            ]
            usersValues[user] = userArray
        values.append(usersValues)
    return counts
    