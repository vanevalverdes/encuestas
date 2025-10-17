def import_clazz(dict):
    from utils.methods import application
    def safe_int(val):
        try:
            return int(val)
        except (ValueError, TypeError):
            return None
    def safe_bool(val):
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.strip().lower() in ("true", "1", "yes", "si")
        return bool(val)
    # Crear la clase principal
    newClazz = application.createClazzRecord(
        name=dict['name'],
        label=dict['label'],
        tag=dict.get('tag', ''),
        plural=dict['plural'],
        sort_field_results=dict.get('sort_field_results', ''),
        table_fields=dict.get('table_fields', ''),
        search_fields=dict.get('search_fields', ''),
        clazz_representation=dict.get('clazz_representation', '')
    )
    # Crear los contenedores y campos
    for container_name, container_data in dict["containers"].items():
        container = application.createContainerRecord(
            name=container_name,
            title=container_data.get('title', None),
            extraclass=container_data.get('class', ''),
            type=container_data.get('type', ''),
            connected_table=safe_int(container_data.get('connected_table', 0)),
            connected_table_fields=container_data.get('connected_table_fields', ''),
            clazz_id=newClazz.id
        )
        for field_name, field_data in container_data['fields'].items():
            application.createFieldRecord(
                fieldname=field_name,
                clazz_id=safe_int(newClazz.id),
                field_type=field_data.get('type', ''),
                field_label=field_data.get('label', ''),
                field_input=field_data.get('input', ''),
                select_options=field_data.get('select_options', None),
                publicBlob=False,
                maxlength=safe_int(field_data.get('maxlength', 0)),
                connected_table=safe_int(field_data.get('connected_table', 0)),
                sort=None,
                required=safe_bool(field_data.get('required', False)),
                hidden=safe_bool(field_data.get('hidden', False)),
                default_value=field_data.get('defaultValue', None),
                extraclass=field_data.get('class', None),
                container_id=safe_int(container.id)
            )
    print(f"Created new class: {newClazz.name}")
    return True



def field_count(clazz,field, value, gender=None,county=None,state=None):
    from utils.methods import session
    query = session.newQuery(clazz)
    query.addFilter(field, "==", value)
    if gender:
        query.addFilter("gender", "==", gender)
    if county:
        query.addFilter("county", "==", county)
    if state:
        query.addFilter("state", "==", state)
    return query.count()

def field_count_user(clazz,field, value, user, gender=None, county=None,state=None):
    from utils.methods import session
    query = session.newQuery(clazz)
    query.addFilter(field, "==", value)
    query.addFilter("createdby_id", "==", user)
    query.filterByToday()
    if gender:
        query.addFilter("gender", "==", gender)
    if county:
        query.addFilter("county", "==", county)
    if state:
        query.addFilter("state", "==", state)
    return query.count()

def countbygender(clazz,fieldname,values, county=None, state=None):
    
    ### Cuenta por campo y género
    counts = {
        field: [
            field_count(clazz,fieldname, field, "A. Masculino", county=county, state=state),
            field_count(clazz,fieldname, field, "B. Femenino", county=county, state=state),
            field_count(clazz,fieldname, field, county=county, state=state)
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
    userCreation_groups = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20"]
    for field, values in counts.items():
        usersValues = {}
        for user in userCreation_groups:
            userArray = [
                field_count_user(clazz,fieldname, field, user, "A. Masculino", county=county, state=state),
                field_count_user(clazz,fieldname, field, user, "B. Femenino", county=county, state=state),
                field_count_user(clazz,fieldname, field, user, county=county, state=state)
            ]
            usersValues[user] = userArray
        values.append(usersValues)
    return counts

def simpleStat(dict,clazzname,fieldname,values, county=None, state=None):
    groups = values
    fieldStat = countbygender(clazzname,fieldname,groups, county=county, state=state)
    dict[fieldname] = fieldStat
    return True

def multipleOpinionStat(dict,clazzname,values, county=None, state=None):
        statsVariables = {}
        for key, value in values.items():
            ### Conoce conoceMauricioBatalla groups
            groups = ["a. Sí","b. No","c. NS/NR"]
            conoce = countbygender(clazzname,value[0],groups, county=county, state=state)
            statsVariables[value[0]] = conoce

            ### Opinión opinionMauricioBatalla groups
            opinion_groups = ["a. Positiva","b. Negativa","c. NS/NR"]
            opinion = countbygender(clazzname,value[1],opinion_groups, county=county, state=state)
            statsVariables[value[1]] = opinion
        dict.update(statsVariables)

        return True

def multipleStat(dict,clazzname,values, county=None, state=None):
        statsVariables = {}

        for key, value in values.items():
            result = countbygender(clazzname,key,value[1], county=county, state=state)
            statsVariables[key] = result
        dict.update(statsVariables)

def generateReport(clazzname,record_id, county=None, state=None):
    from utils.methods.stats import field_count, countbygender
    print(clazzname)
    if record_id == 1:
        ### Age groups
        age_groups = [
        "a. 18 -20", "b. 21 - 24", "c. 25 - 29", "d. 30 - 34",
        "e. 35 - 39", "f. 40 - 44", "g. 45 - 49", "h. 50 - 54",
        "i. 55 - 59", "j. 60 - 64", "k. 65 - 69", "l. 70 - 79",
        "m. + 80"
        ]
        age = countbygender(clazzname,"age",age_groups)

        ### gender groups
        masc = field_count(clazzname,"gender", "A. Masculino")
        fem = field_count(clazzname,"gender", "B. Femenino")
        tot = masc + fem
        gender = {
                "Hombres":masc,
                "Mujeres":fem,
                "Total":tot
        }

        ### State groups
        state_groups = ["1. San José","2. Alajuela","3. Cartago","4. Heredia","5. Guanacaste","6. Puntarenas","7. Limón"]
        state = countbygender(clazzname,"state",state_groups)
        
        ### User groups
        userCreation_groups = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15"]
        userCreation = countbygender(clazzname,"createdby_id",userCreation_groups)

        ### party groups
        party_groups = ["a. Partido Liberación Nacional","b. Partido Unidad Social Cristiana","c. Partido Nueva República","d. Partido Progreso Social Democrático","e. Frente Amplio","f. Partido Liberal Progresista","g. PAC","h. PNG","i. Pueblo Soberano","j. Unidos Podemos","k. Otro","l. Ninguno","m. NS/NR"]
        party = countbygender(clazzname,"party",party_groups)

        ### PartyAndChaves groups
        partyandchaves_groups = ["a. Partido Liberación Nacional","b. Partido Unidad Social Cristiana","c. Partido Nueva República","d. Partido Progreso Social Democrático","e. Frente Amplio","f. Partido Liberal Progresista","g. PAC","h. PNG","i. Pueblo Soberano","j. Unidos Podemos","k. Partido de Chaves","l. Otro","m. Ninguno","n. NS/NR"]
        partyAndChaves = countbygender(clazzname,"partyAndChaves",partyandchaves_groups)

        ### Conoce Chaves groups
        conoceRodrigoChaves_groups = ["a. Sí","b. No","c. NS/NR"]
        conoceRodrigoChaves = countbygender(clazzname,"conoceRodrigoChaves",conoceRodrigoChaves_groups)

        ### Opinión Chaves groups
        opinionRodrigoChaves_groups = ["a. Positiva","b. Negativa","c. NS/NR"]
        opinionRodrigoChaves = countbygender(clazzname,"opinionRodrigoChaves",opinionRodrigoChaves_groups)

        ### Conoce conoceMauricioBatalla groups
        conoceMauricioBatalla_groups = ["a. Sí","b. No","c. NS/NR"]
        conoceMauricioBatalla = countbygender(clazzname,"conoceMauricioBatalla",conoceMauricioBatalla_groups)

        ### Opinión opinionMauricioBatalla groups
        opinionMauricioBatalla_groups = ["a. Positiva","b. Negativa","c. NS/NR"]
        opinionMauricioBatalla = countbygender(clazzname,"opinionMauricioBatalla",opinionMauricioBatalla_groups)

        ### Conoce conoceLauraFernandez groups
        conoceLauraFernandez_groups = ["a. Sí","b. No","c. NS/NR"]
        conoceLauraFernandez = countbygender(clazzname,"conoceLauraFernandez",conoceLauraFernandez_groups)

        ### Opinión opinionLauraFernandez groups
        opinionLauraFernandez_groups = ["a. Positiva","b. Negativa","c. NS/NR"]
        opinionLauraFernandez = countbygender(clazzname,"opinionLauraFernandez",opinionLauraFernandez_groups)

        ### Conoce conoceAlvaroRamos groups
        conoceAlvaroRamos_groups = ["a. Sí","b. No","c. NS/NR"]
        conoceAlvaroRamos = countbygender(clazzname,"conoceAlvaroRamos",conoceAlvaroRamos_groups)

        ### Opinión opinionAlvaroRamos groups
        opinionAlvaroRamos_groups = ["a. Positiva","b. Negativa","c. NS/NR"]
        opinionAlvaroRamos = countbygender(clazzname,"opinionAlvaroRamos",opinionAlvaroRamos_groups)

        ### Conoce conoceGilbertJimenez groups
        conoceGilbertJimenez_groups = ["a. Sí","b. No","c. NS/NR"]
        conoceGilbertJimenez = countbygender(clazzname,"conoceGilbertJimenez",conoceGilbertJimenez_groups)

        ### Opinión opinionGilbertJimenez groups
        opinionGilbertJimenez_groups = ["a. Positiva","b. Negativa","c. NS/NR"]
        opinionGilbertJimenez = countbygender(clazzname,"opinionGilbertJimenez",opinionGilbertJimenez_groups)

        ### Conoce conoceCarolinaDelgado groups
        conoceCarolinaDelgado_groups = ["a. Sí","b. No","c. NS/NR"]
        conoceCarolinaDelgado = countbygender(clazzname,"conoceCarolinaDelgado",conoceCarolinaDelgado_groups)

        ### Opinión opinionCarolinaDelgado groups
        opinionCarolinaDelgado_groups = ["a. Positiva","b. Negativa","c. NS/NR"]
        opinionCarolinaDelgado = countbygender(clazzname,"opinionCarolinaDelgado",opinionCarolinaDelgado_groups)

        ### Conoce conoceMarvinTaylor groups
        conoceMarvinTaylor_groups = ["a. Sí","b. No","c. NS/NR"]
        conoceMarvinTaylor = countbygender(clazzname,"conoceMarvinTaylor",conoceMarvinTaylor_groups)

        ### Opinión opinionMarvinTaylor groups
        opinionMarvinTaylor_groups = ["a. Positiva","b. Negativa","c. NS/NR"]
        opinionMarvinTaylor = countbygender(clazzname,"opinionMarvinTaylor",opinionMarvinTaylor_groups)

        ### Conoce conoceRolandoArayaMonge groups
        conoceRolandoArayaMonge_groups = ["a. Sí","b. No","c. NS/NR"]
        conoceRolandoArayaMonge = countbygender(clazzname,"conoceRolandoArayaMonge",conoceRolandoArayaMonge_groups)

        ### Opinión opinionRolandoArayaMonge groups
        opinionRolandoArayaMonge_groups = ["a. Positiva","b. Negativa","c. NS/NR"]
        opinionRolandoArayaMonge = countbygender(clazzname,"opinionRolandoArayaMonge",opinionRolandoArayaMonge_groups)

        ############ Apoyos Políticos ############

        ### Partido Presidente
        chavesParty_groups = ["a. Sí","b. No","c. NS/NR"]
        chavesParty = countbygender(clazzname,"chavesParty",chavesParty_groups)

        ### chavesCandidate groups
        chavesCandidate_groups = ["a. Mauricio Batalla","b. Laura Fernandez","c. Otro","d. NS/NR"]
        chavesCandidate = countbygender(clazzname,"chavesCandidate",chavesCandidate_groups)
        
        ### plnElections
        plnElections_groups = ["a. Sí","b. No","c. NS/NR"]
        plnElections = countbygender(clazzname,"plnElections",plnElections_groups)

        ### plnCandidate groups
        plnCandidate_groups = ["a. Gilbert Jiménez","b. Carolina Delgado","c. Alvaro Ramos","d. Marvin Taylor","e. NS/NR"]
        plnCandidate = countbygender(clazzname,"plnCandidate",plnCandidate_groups)

        ### generalElections
        generalElections_groups = ["Mauricio Batalla","Laura Fernandez","Álvaro Ramos","Fabricio Alvarado","Eliécer Feinzaig","Gilbert Jiménez","Carolina Delgado","Claudia Dobles","Sofia Guillen","Juan Carlos Hidalgo","Rolando Araya Monge","Luis Amador","Marvin Taylor","Natalia Diaz","Claudio Alpizar","Fernando Zamora","Ninguno","NS/NR"]
        generalElections = countbygender(clazzname,"generalElections",generalElections_groups)

        ### chavesSupport
        chavesSupport_groups = ["a. Sí","b. No","c. NS/NR"]
        chavesSupport = countbygender(clazzname,"chavesSupport",chavesSupport_groups)

        ### chavesScale
        chavesScale_groups = ["1","2","3","4","5","6","7","8","9","10"]
        chavesScale = countbygender(clazzname,"chavesScale",chavesScale_groups)

        stats = {
            "age":age,
            "gender":gender,
            "state":state,
            "party":party,
            "partyAndChaves":partyAndChaves,
            "conoceRodrigoChaves":conoceRodrigoChaves,
            "opinionRodrigoChaves":opinionRodrigoChaves,
            "conoceMauricioBatalla":conoceMauricioBatalla,
            "opinionMauricioBatalla":opinionMauricioBatalla,
            "conoceLauraFernandez":conoceLauraFernandez,
            "opinionLauraFernandez":opinionLauraFernandez,
            "conoceAlvaroRamos":conoceAlvaroRamos,
            "opinionAlvaroRamos":opinionAlvaroRamos,
            "conoceGilbertJimenez":conoceGilbertJimenez,
            "opinionGilbertJimenez":opinionGilbertJimenez,
            "conoceCarolinaDelgado":conoceCarolinaDelgado,
            "opinionCarolinaDelgado":opinionCarolinaDelgado,
            "conoceMarvinTaylor":conoceMarvinTaylor,
            "opinionMarvinTaylor":opinionMarvinTaylor,
            "conoceRolandoArayaMonge":conoceRolandoArayaMonge,
            "opinionRolandoArayaMonge":opinionRolandoArayaMonge,
            "chavesParty":chavesParty,
            "chavesCandidate":chavesCandidate,
            "plnElections":plnElections,
            "plnCandidate":plnCandidate,
            "generalElections":generalElections,
            "chavesSupport":chavesSupport,
            "chavesScale":chavesScale,
            "userCreation":userCreation
        }
        return stats
    elif record_id == 2:
        ### Age groups
        age_groups = [
        "a. 18 -20", "b. 21 - 24", "c. 25 - 29", "d. 30 - 34",
        "e. 35 - 39", "f. 40 - 44", "g. 45 - 49", "h. 50 - 54",
        "i. 55 - 59", "j. 60 - 64", "k. 65 - 69", "l. 70 - 79",
        "m. + 80"
        ]
        age = countbygender(clazzname,"age",age_groups)

        ### gender groups
        masc = field_count(clazzname,"gender", "A. Masculino")
        fem = field_count(clazzname,"gender", "B. Femenino")
        tot = masc + fem
        gender = {
                "Hombres":masc,
                "Mujeres":fem,
                "Total":tot
        }
        ### User groups
        userCreation_groups = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15"]
        userCreation = countbygender(clazzname,"createdby_id",userCreation_groups)

        ### party groups
        party_groups = [
            "a. Partido Liberación Nacional",
            "b. Partido Unidad Social Cristiana",
            "c. Partido Nueva República",
            "d. Partido Progreso Social Democrático",
            "e. Frente Amplio",
            "f. Partido Liberal Progresista",
            "g. PAC",
            "h. PNG",
            "i. Pueblo Soberano",
            "j. Partido Unidos Podemos",
            "k. Partido Motiva",
            "l. Partido de Rodrigo Chaves",
            "m. Otro",
            "n. Ninguno",
            "o. NS/NR"
            ]
        party = countbygender(clazzname,"party",party_groups)

        ############ Apoyos Políticos ############

        ### Partido Presidente
        chavesParty_groups = ["a. Sí","b. No","c. NS/NR"]
        chavesParty = countbygender(clazzname,"chavesParty",chavesParty_groups)
        
        ### plnElections
        plnElections_groups = ["a. Sí","b. No","c. NS/NR"]
        plnElections = countbygender(clazzname,"plnElections",plnElections_groups)

        ### plnCandidate groups
        plnCandidate_groups = ["a. Gilbert Jiménez","b. Carolina Delgado","c. Alvaro Ramos","d. Marvin Taylor","e. NS/NR","f. Ninguno"]
        plnCandidate = countbygender(clazzname,"plnCandidate",plnCandidate_groups)

        ### generalElections
        generalElections_groups = [
            "Mauricio Batalla",
            "Laura Fernandez",
            "Álvaro Ramos",
            "Fabricio Alvarado",
            "Eliécer Feinzaig",
            "Gilbert Jiménez",
            "Carolina Delgado",
            "Claudia Dobles",
            "Sofia Guillen",
            "Juan Carlos Hidalgo",
            "Rolando Araya Monge",
            "Luis Amador",
            "Marvin Taylor",
            "Natalia Diaz",
            "Claudio Alpizar",
            "Fernando Zamora",
            "Ninguno",
            "NS/NR"
            ]
        generalElections = countbygender(clazzname,"generalElections",generalElections_groups)

        ### chavesSupport
        chavesSupport_groups = ["a. Sí","b. No","c. NS/NR"]
        chavesSupport = countbygender(clazzname,"chavesSupport",chavesSupport_groups)


        stats = {
            "age":age,
            "gender":gender,
            "party":party,
            "chavesParty":chavesParty,
            "plnElections":plnElections,
            "plnCandidate":plnCandidate,
            "generalElections":generalElections,
            "chavesSupport":chavesSupport,
            "userCreation":userCreation
        }
        #session.putVariable("stats",stats)
        return stats
    elif record_id == 3:
        ### Age groups
        age_groups = [
        "a. 18 -20", "b. 21 - 24", "c. 25 - 29", "d. 30 - 34",
        "e. 35 - 39", "f. 40 - 44", "g. 45 - 49", "h. 50 - 54",
        "i. 55 - 59", "j. 60 - 64", "k. 65 - 69", "l. 70 - 79",
        "m. + 80"
        ]
        age = countbygender(clazzname,"age",age_groups)

        ### gender groups
        masc = field_count(clazzname,"gender", "A. Masculino")
        fem = field_count(clazzname,"gender", "B. Femenino")
        tot = masc + fem
        gender = {
                "Hombres":masc,
                "Mujeres":fem,
                "Total":tot
        }
        ### State groups
        state_groups = ["1. San José","2. Alajuela","3. Cartago","4. Heredia","5. Guanacaste","6. Puntarenas","7. Limón"]
        state = countbygender(clazzname,"state",state_groups)
        ### User groups
        userCreation_groups = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20"]
        userCreation = countbygender(clazzname,"createdby_id",userCreation_groups)

        ### party groups
        party_groups = [
            "a. Partido Liberación Nacional",
            "b. Partido Unidad Social Cristiana",
            "c. Partido Nueva República",
            "d. Partido Progreso Social Democrático",
            "e. Frente Amplio",
            "f. Partido Liberal Progresista",
            "g. PAC",
            "h. PNG",
            "i. Pueblo Soberano",
            "j. Partido Unidos Podemos",
            "k. Partido de Rodrigo Chaves",
            "l. Otro",
            "m. Ninguno",
            "n. NS/NR"
            ]
        party = countbygender(clazzname,"party",party_groups)

        ############ Apoyos Políticos ############
        
        ### plnElections
        plnElections_groups = ["a. Sí","b. No","c. NS/NR"]
        plnElections = countbygender(clazzname,"plnElections",plnElections_groups)

        ### chavesScale
        plnScale_groups = ["1","2","3","4","5","6","7","8","9","10"]
        plnScale = countbygender(clazzname,"plnScale",plnScale_groups)

        ### plnCandidate groups
        plnCandidate_groups = ["a. Gilbert Jiménez","b. Carolina Delgado","c. Alvaro Ramos","d. Marvin Taylor","e. Ninguno","f. NS/NR"]
        plnCandidate = countbygender(clazzname,"plnCandidate",plnCandidate_groups)

        ### generalElections
        generalElections_groups = [
            "Laura Fernandez",
            "Álvaro Ramos",
            "Fabricio Alvarado",
            "Eliécer Feinzaig",
            "Gilbert Jiménez",
            "Carolina Delgado",
            "Claudia Dobles",
            "Sofia Guillen",
            "Juan Carlos Hidalgo",
            "Rolando Araya Monge",
            "Luis Amador",
            "Marvin Taylor",
            "Natalia Diaz",
            "Claudio Alpizar",
            "Fernando Zamora",
            "Ninguno",
            "NS/NR"
            ]
        generalElections = countbygender(clazzname,"generalElections",generalElections_groups)

        ### chavesSupport
        chavesSupport_groups = ["a. Sí","b. No","c. NS/NR"]
        chavesSupport = countbygender(clazzname,"chavesSupport",chavesSupport_groups)


        stats = {
            "age":age,
            "gender":gender,
            "state":state,
            "party":party,
            "plnElections":plnElections,
            "plnScale":plnScale,
            "plnCandidate":plnCandidate,
            "generalElections":generalElections,
            "chavesSupport":chavesSupport,
            "userCreation":userCreation
        }
        #session.putVariable("stats",stats)
        print(stats)
        return stats
    elif record_id == 4:
        from utils.methods import session
        query = session.newQuery(clazzname)
        stats = {}

        alvaroramos = query.getSum("alvaroramos")
        carolinadelgado = query.getSum("carolinadelgado")
        gilberthjimenez = query.getSum("gilberthjimenez")
        marvintaylor = query.getSum("marvintaylor")
        nulled = query.getSum("nulled")
        blank = query.getSum("blank")
        total = alvaroramos + carolinadelgado + gilberthjimenez + marvintaylor + nulled + blank
        if total > 0:
            alvaroramos = round((float(alvaroramos) / float(total) * 100.0), 2)
            carolinadelgado = round((float(carolinadelgado) / float(total) * 100.0), 2)
            gilberthjimenez = round((float(gilberthjimenez) / float(total) * 100.0), 2)
            marvintaylor = round((float(marvintaylor) / float(total) * 100.0), 2)
            nulled = round((float(nulled) / float(total) * 100.0), 2)
            blank = round((float(blank) / float(total) * 100.0), 2)
        else:
            alvaroramos = 0
            carolinadelgado = 0
            gilberthjimenez = 0
            marvintaylor = 0
            nulled = 0
            blank = 0

        stats["total"] = {
            "alvaroramos":alvaroramos,
            "carolinadelgado":carolinadelgado,
            "gilberthjimenez":gilberthjimenez,
            "marvintaylor":marvintaylor,
            "nulled":nulled,
            "blank":blank
        }

        state_groups = ["1. San José","2. Alajuela","3. Cartago","4. Heredia","5. Guanacaste","6. Puntarenas","7. Limón"]
        for state in state_groups:
            query = session.newQuery(clazzname)
            query = query.addFilter("state", "==", state)
            alvaroramos_state = query.getSum("alvaroramos")
            carolinadelgado_state = query.getSum("carolinadelgado")
            gilberthjimenez_state = query.getSum("gilberthjimenez")
            marvintaylor_state = query.getSum("marvintaylor")
            nulled_state = query.getSum("nulled")
            blank_state = query.getSum("blank")
            total = alvaroramos_state + carolinadelgado_state + gilberthjimenez_state + marvintaylor_state + nulled_state + blank_state
            if total > 0:
                alvaroramos_state = round((float(alvaroramos_state) / float(total) * 100.0), 2)
                carolinadelgado_state = round((float(carolinadelgado_state) / float(total) * 100.0), 2)
                gilberthjimenez_state = round((float(gilberthjimenez_state) / float(total) * 100.0), 2)
                marvintaylor_state = round((float(marvintaylor_state) / float(total) * 100.0), 2)
                nulled_state = round((float(nulled_state) / float(total) * 100.0), 2)
                blank_state = round((float(blank_state) / float(total) * 100.0), 2)
            else:
                alvaroramos_state = 0
                carolinadelgado_state = 0
                gilberthjimenez_state = 0
                marvintaylor_state = 0
                nulled_state = 0
                blank_state = 0
            stats[state] = {
                "alvaroramos":alvaroramos_state,
                "carolinadelgado":carolinadelgado_state,
                "gilberthjimenez":gilberthjimenez_state,
                "marvintaylor":marvintaylor_state,
                "nulled":nulled_state,
                "blank":blank_state
            }

        #session.putVariable("stats",stats)
        print(stats)
        return stats
    elif record_id == 5:
        from utils.methods import session

        stats = {}


        ### Age groups
        age_groups = [
        "a. 18 -20", "b. 21 - 24", "c. 25 - 29", "d. 30 - 34",
        "e. 35 - 39", "f. 40 - 44", "g. 45 - 49", "h. 50 - 54",
        "i. 55 - 59", "j. 60 - 64", "k. 65 - 69", "l. 70 - 79",
        "m. + 80"
        ]
        age = countbygender(clazzname,"age",age_groups)
        stats["age"] = age

        ### gender groups
        masc = field_count(clazzname,"gender", "A. Masculino")
        fem = field_count(clazzname,"gender", "B. Femenino")
        tot = masc + fem
        gender = {
                "Hombres":masc,
                "Mujeres":fem,
                "Total":tot
        }
        stats["gender"] = gender

        ### State groups
        state_groups = ["1. San José","2. Alajuela","3. Cartago","4. Heredia","5. Guanacaste","6. Puntarenas","7. Limón"]
        state = countbygender(clazzname,"state",state_groups)
        stats["state"] = state

        ### User groups
        userCreation_groups = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20"]
        userCreation = countbygender(clazzname,"createdby_id",userCreation_groups)
        stats["userCreation"] = userCreation

        ### party groups
        party_groups = [
            "a. Partido Liberación Nacional",
            "b. Partido Unidad Social Cristiana",
            "c. Partido Nueva República",
            "d. Partido Progreso Social Democrático",
            "e. Frente Amplio",
            "f. Partido Liberal Progresista",
            "g. PAC",
            "h. PNG",
            "i. Pueblo Soberano",
            "j. Partido Unidos Podemos",
            "k. Partido de Rodrigo Chaves",
            "l. Otro",
            "m. Ninguno",
            "n. NS/NR"
            ]
        party = countbygender(clazzname,"party",party_groups)
        stats["party"] = party

        ### laboral groups
        laboral_groups = [
            "a. Contrato Permanente",
            "b. Contrato Temporal",
            "c. Independiente",
            "d. Desempleado",
            "e. Pensionado",
            "f. Estudiante",
            "g. Ama de casa",
            "h. Trabajador informal",
            "Otro",
            "NS/NR"
            ]
        laboralCondition = countbygender(clazzname,"laboralCondition",laboral_groups)
        stats["laboralCondition"] = laboralCondition

        ### studies groups
        studies_groups = [
            "a. Primaria Incompleta",
            "b. Primaria Completa",
            "c. Secundaria Incompleta",
            "d. Secundaria Completa",
            "e. Universitaria Incompleta",
            "f. Universitaria Completa",
            "g. Técnica Incompleta",
            "h. Técnica Completa",
            "Otro",
            "NS/NR"
            ]
        studies = countbygender(clazzname,"studies",studies_groups)
        stats["studies"] = studies

        ### religion groups
        religion_groups = [
            "a. Católico",
            "b. Evangélico",
            "c. Testigo de Jehová",
            "d. Judío",
            "e. Musulmán",
            "f. Budista",
            "g. Ortodoxo",
            "h. Ateo",
            "i. Agnóstico",
            "Ninguna",
            "Otra",
            "NS/NR"
            ]
        religion = countbygender(clazzname,"religion",religion_groups)
        stats["religion"] = religion

        ### problems_groups groups
        problems_groups = [
            "Seguridad ciudadana",
            "Migración",
            "Educación",
            "Salud",
            "Costo de vida",
            "Desempleo",
            "Corrupción",
            "Estado de infraestructura vial",
            "Otro",
            "NS/NR"
            ]
        nationalProblems = countbygender(clazzname,"nationalProblems",problems_groups)
        stats["nationalProblems"] = nationalProblems

        ### roadCR groups
        roadCR = [
                        "a. Buen camino",
                        "b. Mal Camino",
                        "c. NS/NR"
            ]
        roadCR = countbygender(clazzname,"roadCR",roadCR)
        stats["roadCR"] = roadCR

        ### optimist groups
        optimist = [
                        "a. Optimista",
                        "b. Pesimista",
                        "c. NS/NR"
            ]
        optimist = countbygender(clazzname,"optimist",optimist)
        stats["optimist"] = optimist

        multipleOpinionStat(stats, clazzname,{"Natalia Diaz":["nataliaConoce","nataliaOpinion"],
                "Alvaro Ramos":["conoceAlvaro","opinionAlvaro"],
                "Laura Fernandez":["conoceLaura","opinionLaura"],
                "Claudia Dobles":["conoceClaudia","opinionClaudia"],
                "Fabricio Alvarado":["conoceFabricio","opinionFabricio"],
                "Carlos Valenciano":["conoceCarlos","opinionCarlos"],
                "Ariel Robles":["conoceAriel","opinionAriel"],
                "Luis Amador":["conoceLuis","opinionLuis"],
                "Juan Carlos Hidalgo":["conoceJuan","opinionJuan"],
                "Eli Feinzaig":["conoceEli","opinionEli"],
                "Rolando Araya":["conoceRolando","opinionRolando"],
                "Jose Maria Villalta":["conoceJose","opinionJose"]})
        
        variables =  {
                    "chavesSupport":["¿Apoya la gestión del presidente Rodrigo Chaves?",["a. Sí","b. No","c. NS/NR"]],
                    "chavesScale":["Del 0 al 10, ¿Cuánto apoya la gestión de Rodrigo Chaves?",["0","1","2","3","4","5","6","7","8","9","10"]],
                    "govermentSupport":["¿Apoya la gestion del gobierno?",["a. Sí","b. No","c. NS/NR"]],
                    "asambleaOpinion":["¿Cómo calificaría la labor de la Asamblea Legislativa?",["a. Muy buena","b. Buena","c. Regular","d. Mala","e. Muy mala","f. NS/NR"]],
                    "poderOpinion":["¿Cómo calificaría la labor del Poder Judicial?",["a. Muy buena","b. Buena","c. Regular","d. Mala","e. Muy mala","f. NS/NR"]],
                    "cajaOpinion":["¿Cómo calificaría la labor de la CCSS?",["a. Muy buena","b. Buena","c. Regular","d. Mala","e. Muy mala","f. NS/NR"]],
                    "mediosOpinion":["¿Cómo calificaría la labor de los medios de comunicación?",["a. Muy buena","b. Buena","c. Regular","d. Mala","e. Muy mala","f. NS/NR"]],
                    "universidadesOpinion":["¿Cómo calificaría la labor de las Universidades Públicas?",["a. Muy buena","b. Buena","c. Regular","d. Mala","e. Muy mala","f. NS/NR"]],
                    "oijOpinion":["¿Cómo calificaría la labor del OIJ?",["a. Muy buena","b. Buena","c. Regular","d. Mala","e. Muy mala","f. NS/NR"]],
                    "fuerzaOpinion":["¿Cómo calificaría la labor de la Fuerza Pública?",["a. Muy buena","b. Buena","c. Regular","d. Mala","e. Muy mala","f. NS/NR"]],
                    "contraloriaOpinion":["¿Cómo calificaría la labor de la Contraloría General de la República?",["a. Muy buena","b. Buena","c. Regular","d. Mala","e. Muy mala","f. NS/NR"]],
                    "ayaOpinion":["¿Cómo calificaría la labor del AyA?",["a. Muy buena","b. Buena","c. Regular","d. Mala","e. Muy mala","f. NS/NR"]]
        }
        statsVariables = {}

        for key, value in variables.items():
            result = countbygender(clazzname,key,value[1])
            statsVariables[key] = result
        stats.update(statsVariables)

        ### womanPresident
        womanPresident_groups = [
                    "Igual",
                    "Mejor",
                    "Peor",
                    "NS/NR"
                    ]
        womanPresident = countbygender(clazzname,"womanPresident",womanPresident_groups)
        stats["womanPresident"] = womanPresident
        
        ### generalElections
        generalElections_groups = [
                        "Laura Fernandez",
                        "Claudia Dobles",
                        "Luis Amador",
                        "Eliécer Feinzaig",
                        "Natalia Díaz ",
                        "Sofia Guillen",
                        "Alvaro Ramos",
                        "Juan Carlos Hidalgo",
                        "Fabricio Alvarado",
                        "Rolando Araya",
                        "Francisco Gamboa",
                        "Carlos Valenciano Kamer",
                        "Douglas Soto",
                        "Claudio Alpízar",
                        "Fernando Zamora",
                        "Ninguno",
                        "NS/NR"
                    ]
        generalElections = countbygender(clazzname,"generalElections",generalElections_groups)
        stats["generalElections"] = generalElections

        ### generalElectionsSecond
        secondNationalElections_groups = [
                        "Laura Fernandez",
                        "Claudia Dobles",
                        "Luis Amador",
                        "Natalia Díaz ",
                        "Alvaro Ramos",
                        "Juan Carlos Hidalgo",
                        "Fabricio Alvarado",
                        "Rolando Araya",
                        "Ninguno",
                        "NS/NR"
                    ]
        secondNationalElections = countbygender(clazzname,"secondNationalElections",secondNationalElections_groups)
        stats["secondNationalElections"] = secondNationalElections


        ### chavesSupport
        chavesSupport_groups = ["a. Sí","b. No","c. NS/NR"]
        chavesSupport = countbygender(clazzname,"chavesSupport",chavesSupport_groups)
        stats["chavesSupport"] = chavesSupport

        simpleStat(stats, clazzname,"lastElections",["a. Sí","b. No","c. NS/NR"])

        simpleStat(stats, clazzname,"lastCandidate",["Carmen Quesada Santamaría",
                                                    "Christian Rivera Paniagua",
                                                    "Eduardo Cruickshank Smith",
                                                    "Eliécer Feinzaig Mintz",
                                                    "Fabricio Alvarado Muñoz",
                                                    "Federico Malavassi Calvo",
                                                    "Greivin Moya Carpio",
                                                    "Jhonn Vega Masís",
                                                    "José María Figueres Olsen",
                                                    "José María Villalta Flórez-Estrada",
                                                    "Lineth Saborío Chaverri",
                                                    "Luis Alberto Cordero Arias",
                                                    "Maricela Morales Mora",
                                                    "Martín Chinchilla Castro",
                                                    "Natalia Díaz Quintana",
                                                    "Óscar Andrés López Arias",
                                                    "Óscar Campos Chavarría",
                                                    "Rodrigo Chaves Robles",
                                                    "Rodolfo Hernández Gómez",
                                                    "Rodolfo Piza Rocafort",
                                                    "Rolando Araya Monge",
                                                    "Roulan Jiménez Chavarría",
                                                    "Sergio Mena Díaz",
                                                    "Walter Muñoz Céspedes",
                                                    "Welmer Ramos González",
                                                    "Nullo",
                                                    "En blanco",
                                                    "NS/NR"])
        
        simpleStat(stats, clazzname,"voteScale",["0","1","2","3","4","5","6","7","8","9","10"])

        multipleStat(stats, clazzname,{"personOrParty":["¿Está de acuerdo con la siguiente frase? Hoy votaría más por una persona que por un partido",["a. Sí","b. No","c. NS/NR"]],
                                                    "nextGoverment":["¿Con cuál de las siguientes opciones se identifica: Me gustaría que el próximo gobierno sea...",["a. Igual al gobierno de Chaves", "b. Totalmente diferente al gobierno de Chaves", "c.Parecido, pero con otra forma de comunicar", "d. Ninguna de las anteriores", "e. NS/NR"]],
                                                    "chavesCandidate":["¿Votaría por cualquier candidato que diga Cháves?",["a. Sí","b. No","c. NS/NR"]]})
        
        multipleStat(stats, clazzname,{"security":["Seguridad ciudadana",["a. Cumplió","b. No cumplió","c. NS/NR"]],
                    "migration":["Migración",["a. Cumplió","b. No cumplió","c. NS/NR"]],
                    "education":["Educación",["a. Cumplió","b. No cumplió","c. NS/NR"]],
                    "health":["Salud",["a. Cumplió","b. No cumplió","c. NS/NR"]],
                    "cost":["Costo de vida",["a. Cumplió","b. No cumplió","c. NS/NR"]],
                    "jobs":["Empleo",["a. Cumplió","b. No cumplió","c. NS/NR"]],
                    "corrupt":["Combate a Corrupción",["a. Cumplió","b. No cumplió","c. NS/NR"]]})
        
        multipleStat(stats, clazzname,{
                    "trabajoCarceles":["Trabajo obligatorio en las cárceles",["a. Completamente de Acuerdo", "b. De Acuerdo", "c. En Desacuerdo", "d. Completamente en Desacuerdo", "e. NS/NR"]],
                    "migrationDeport":["Migración regulada con deportación inmediata de extranjeros que comentan crímenes en CR, después de cumplir su condena",["a. Completamente de Acuerdo", "b. De Acuerdo", "c. En Desacuerdo", "d. Completamente en Desacuerdo", "e. NS/NR"]],
                    "finalcialEducation":["Educación financiera y habilidades blandas desde primaria",["a. Completamente de Acuerdo", "b. De Acuerdo", "c. En Desacuerdo", "d. Completamente en Desacuerdo", "e. NS/NR"]],
                    "independentWorkers":["Estado más flexible para trabajadores independientes",["a. Completamente de Acuerdo", "b. De Acuerdo", "c. En Desacuerdo", "d. Completamente en Desacuerdo", "e. NS/NR"]],
                    "abort":["Aborto libre, en caso de violación",["a. Completamente de Acuerdo", "b. De Acuerdo", "c. En Desacuerdo", "d. Completamente en Desacuerdo", "e. NS/NR"]],
                    "childJudge":["Niños juzgados como adultos en casos de homicidio",["a. Completamente de Acuerdo", "b. De Acuerdo", "c. En Desacuerdo", "d. Completamente en Desacuerdo", "e. NS/NR"]],
                    "sexualGuides":["Uso de las Guías sexuales en la educación",["a. Completamente de Acuerdo", "b. De Acuerdo", "c. En Desacuerdo", "d. Completamente en Desacuerdo", "e. NS/NR"]],
                    "mine":["Que Costa Rica explore y aproveche sus recursos mineros para generar ingresos y empleo (siempre que se haga bajo normas ambientales estrictas)",["a. Completamente de Acuerdo", "b. De Acuerdo", "c. En Desacuerdo", "d. Completamente en Desacuerdo", "e. NS/NR"]],
                    "secularState":["Costa Rica debería ser un Estado laico (es decir, sin una religión oficial. Actualmente la religión católica es reconocida como la religión del Estado)",["a. Completamente de Acuerdo", "b. De Acuerdo", "c. En Desacuerdo", "d. Completamente en Desacuerdo", "e. NS/NR"]],
                    "weed":["Que las personas adultas puedan consumir marihuana de forma legal y regulada en Costa Rica (actualmente eso está permitido en otros países)",["a. Completamente de Acuerdo", "b. De Acuerdo", "c. En Desacuerdo", "d. Completamente en Desacuerdo", "e. NS/NR"]],
                    "sellInstitutions":["Que el Estado venda algunas instituciones o empresas públicas para reducir la deuda o financiar proyectos prioritarios",["a. Completamente de Acuerdo", "b. De Acuerdo", "c. En Desacuerdo", "d. Completamente en Desacuerdo", "e. NS/NR"]]
                })
        
        simpleStat(stats, clazzname,"phrases",["Costa Rica necesita mano firme",
                                        "Costa Rica necesita un gobierno que escuche",
                                        "Costa Rica necesita orden y empatía",
                                        "Costa Rica necesita que la dejen trabajar",
                                        "Costa Rica necesita recuperar el valor de la familia",
                                        "Ninguna",
                                        "NS/NR"])
        
        simpleStat(stats, clazzname,"aboutNatalia",["a. Sí",
                                        "b. No",
                                        "c. NS/NR"])
        
        simpleStat(stats, clazzname,"aboutNataliaScale",["a. La conoce bien",
                                        "b. La ha escuchado mencionar, pero no la conoce bien",
                                        "c. No la conoce"])
                                                       
        simpleStat(stats, clazzname,"whereAboutNatalia",["a. Televisión",
                                                    "b. Redes sociales",
                                                    "c. Radio",
                                                    "d. Periódico",
                                                    "e. Evento público",
                                                    "f. Conversación con amigos o familiares",
                                                    "g. Otro",
                                                    "No la ha visto o escuchado recientemente",
                                                    "NS/NR"])

        simpleStat(stats, clazzname,"presidentAboutNatalia",["a. Sí",
                                                    "b. No",
                                                    "c. NS/NR"])
        simpleStat(stats, clazzname,"crimeCandidates",["Natalia Díaz",
                                                    "Álvaro Ramos",
                                                    "Laura Fernández",
                                                    "Fabricio Alvarado",
                                                    "Claudia Dobles",
                                                    "Carlos Valenciano",
                                                    "Ariel Robles",
                                                    "Luis Amador",
                                                    "Rolando Araya",
                                                    "Juan Carlos Hidalgo",
                                                    "Otro",
                                                    "Ninguno",
                                                    "NS/NR"])
        
        simpleStat(stats, clazzname,"supportReasons",["Que proponga soluciones firmes a la inseguridad",
                                                    "Que no esté ligado a partidos tradicionales",
                                                    "Que tenga experiencia en gobierno",
                                                    "Que defienda al trabajador independiente y al emprendedor",
                                                    "Que represente una nueva generación",
                                                    "Que sea del partido del presidente",
                                                    "Otra",
                                                    "NS/NR"])


        print(stats)
        return stats
    elif record_id == 6:
        from utils.methods import session

        stats = {}


        ### gender groups
        masc = field_count(clazzname,"gender", "A. Masculino")
        fem = field_count(clazzname,"gender", "B. Femenino")
        tot = masc + fem
        gender = {
                "Hombres":masc,
                "Mujeres":fem,
                "Total":tot
        }
        stats["gender"] = gender

        ### Age groups
        age_groups = [
        "a. 18 -20", "b. 21 - 24", "c. 25 - 29", "d. 30 - 34",
        "e. 35 - 39", "f. 40 - 44", "g. 45 - 49", "h. 50 - 54",
        "i. 55 - 59", "j. 60 - 64", "k. 65 - 69", "l. 70 - 79",
        "m. + 80"
        ]
        age = countbygender(clazzname,"age",age_groups)
        stats["age"] = age
        ### User groups
        userCreation_groups = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20"]
        userCreation = countbygender(clazzname,"createdby_id",userCreation_groups)
        stats["userCreation"] = userCreation



        ### party groups
        party_groups = [
            "a. Partido Liberación Nacional",
            "b. Partido Unidad Social Cristiana",
            "c. Partido Nueva República",
            "d. Partido Progreso Social Democrático",
            "e. Frente Amplio",
            "f. Partido Liberal Progresista",
            "g. PAC",
            "h. PNG",
            "i. Pueblo Soberano",
            "j. Partido Unidos Podemos",
            "k. Partido de Rodrigo Chaves",
            "l. Otro",
            "m. Ninguno",
            "n. NS/NR"
            ]
        party = countbygender(clazzname,"party",party_groups)
        stats["party"] = party

        multipleStat(stats, clazzname,{
                    "barvaSupport":["Apoya la gestión al frente del Municipalidad de Barva del alcalde, Jorge Acuña?",["a. Sí","b. No","c. NS/NR"]],
                    "barvaScale":["Del 1 al 10 como califica la labor de la Municipalidad de Barva.",["0","1","2","3","4","5","6","7","8","9","10"]],
                })
        multipleOpinionStat(stats, clazzname,{"Rodrigo Chaves":["chavesConoce","chavesOpinion"],
                "Jorge Acuña":["jorgeConoce","jorgeOpinion"]})
        print(stats)
        return stats
    elif record_id == 7:
        from utils.methods import session

        stats = {}


        ### gender groups
        masc = field_count(clazzname,"gender", "A. Masculino")
        fem = field_count(clazzname,"gender", "B. Femenino")
        tot = masc + fem
        gender = {
                "Hombres":masc,
                "Mujeres":fem,
                "Total":tot
        }
        stats["gender"] = gender

        ### Age groups
        age_groups = [
        "a. 18 -20", "b. 21 - 24", "c. 25 - 29", "d. 30 - 34",
        "e. 35 - 39", "f. 40 - 44", "g. 45 - 49", "h. 50 - 54",
        "i. 55 - 59", "j. 60 - 64", "k. 65 - 69", "l. 70 - 79",
        "m. + 80"
        ]
        age = countbygender(clazzname,"age",age_groups)
        stats["age"] = age
        ### User groups
        userCreation_groups = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20"]
        userCreation = countbygender(clazzname,"createdby_id",userCreation_groups)
        stats["userCreation"] = userCreation

        multipleStat(stats, clazzname,{
                    "apoyaAlcalde":["Apoya usted la gestión del alcalde, Carlos Hidalgo?",["a. Sí","b. No","c. NS/NR"]],
                    "muniScale":["7. Del 1 al 10 como califica la labor de la Municipalidad de Barva.",["0","1","2","3","4","5","6","7","8","9","10"]],
                    "apoyaRodrigoChaves":["¿Apoya usted la gestión del presidente Rodrigo Chaves?",["a. Sí","b. No","c. NS/NR"]],
                    "chavesParty":["¿Apoyaría usted un partido impulsado por el presidente, Rodrigo Chaves?",["a. Sí","b. No","c. NS/NR"]],
                })
        multipleOpinionStat(stats, clazzname,{
                "Carlos Hidalgo":["conoceCarlos","opinionCarlos"],
                "Rodrigo Chaves":["conoceRodrigoChaves","opinionRodrigoChaves"]
                })
        print(stats)
    elif record_id == 15:
        from utils.methods import session

        stats = {}


        ### gender groups
        masc = field_count(clazzname,"gender", "A. Masculino", county=county)
        fem = field_count(clazzname,"gender", "B. Femenino", county=county)
        tot = masc + fem
        gender = {
                "Hombres":masc,
                "Mujeres":fem,
                "Total":tot
        }
        stats["gender"] = gender

        ### Age groups
        age_groups = [
        "a. 18 -20", "b. 21 - 24", "c. 25 - 29", "d. 30 - 34",
        "e. 35 - 39", "f. 40 - 44", "g. 45 - 49", "h. 50 - 54",
        "i. 55 - 59", "j. 60 - 64", "k. 65 - 69", "l. 70 - 79",
        "m. + 80"
        ]
        age = countbygender(clazzname,"age",age_groups, county=county)
        stats["age"] = age
        ### User groups
        userCreation_groups = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20"]
        userCreation = countbygender(clazzname,"createdby_id",userCreation_groups, county=county)
        stats["userCreation"] = userCreation

        multipleStat(stats, clazzname,{
                    "county":["Distrito",["San José",
                        "Curridabat",
                        "Goicoechea",
                        "Moravia",
                        "Tibas",
                        "Alajuelita",
                        "Desamparados",
                        "Escazú",
                        "Mora",
                        "Pérez Zeledón",
                        "Grecia",
                        "Naranjo",
                        "Palmares",
                        "San Ramón",
                        "San Carlos",
                        "Upala",
                        "Tres Ríos",
                        "Cartago",
                        "Oreamuno",
                        "Paraíso",
                        "Turrialba",
                        "Sarapiquí",
                        "Heredia",
                        "San Rafael",
                        "Santo Domingo",
                        "Cañas",
                        "Liberia",
                        "Nicoya",
                        "Guapiles",
                        "Guacimo",
                        "Siquirres",
                        "Limón",
                        "Puntarenas",
                        "Quepos",
                        "Buenos Aires",
                        "Osa"]],
                    "party":["Partido político con el que se identifica",["Liberación Nacional",
                        "Unidad Social Cristiano",
                        "Liberal Progresista",
                        "Nueva República",
                        "Pueblo Soberano",
                        "Unidos Podemos",
                        "Frente Amplio",
                        "PAC",
                        "Aquí Costa Rica Manda",
                        "Progreso Social Democrático",
                        "Nueva Generación",
                        "Justicia Social",
                        "Costa Rica Primero",
                        "Republicano",
                        "Otro",
                        "Ninguno",
                        "NS/NR"]],
                    "apoyaAlcalde":["Apoya usted la gestión del alcalde, Carlos Hidalgo?",["a. Sí","b. No","c. NS/NR"]],
                    "apoyaAlcalde":["Apoya usted la gestión del actual alcalde / alcaldesa de su cantón?",["a. Sí","b. No","c. NS/NR"]],
                    "chavesSupport":["Apoya usted la gestión del presidente Rodrigo Chaves?",["a. Sí","b. No","c. NS/NR"]],
                    "nationalElection":["¿Si las elecciones fueran hoy, por quién votaría?",[
                        "Rolando Araya",
                        "Fabricio Alvarado",
                        "Álvaro Ramos",
                        "Laura Fernández",
                        "Natalia Díaz",
                        "Luis Amador",
                        "José Aguilar Berrocal",
                        "Douglas Soto",
                        "Ariel Robles",
                        "Claudio Alpízar",
                        "Fernando Zamora",
                        "Claudia Dobles",
                        "Eliécer Feinzaig",
                        "Juan Carlos Hidalgo",
                        "Otro",
                        "Ninguno",
                        "NS/NR"
                    ]]
                }, county=county)
        multipleOpinionStat(stats, clazzname,{
                "José Aguilar Berrocal":["aguilarConoce","aguilarOpinion"],
                "Ariel Robles":["arielConoce","arielOpinion"],
                }, county=county)
        print(stats)
        return stats
    elif record_id == 16:
        from utils.methods import session

        stats = {}


        ### gender groups
        masc = field_count(clazzname,"gender", "A. Masculino", county=county, state=state)
        fem = field_count(clazzname,"gender", "B. Femenino", county=county, state=state)
        tot = masc + fem
        gender = {
                "Hombres":masc,
                "Mujeres":fem,
                "Total":tot
        }
        stats["gender"] = gender

        ### Age groups
        age_groups = [
        "a. 18 -20", "b. 21 - 24", "c. 25 - 29", "d. 30 - 34",
        "e. 35 - 39", "f. 40 - 44", "g. 45 - 49", "h. 50 - 54",
        "i. 55 - 59", "j. 60 - 64", "k. 65 - 69", "l. 70 - 79",
        "m. + 80"
        ]
        age = countbygender(clazzname,"age",age_groups, county=county, state=state)
        stats["age"] = age
        ### User groups
        userCreation_groups = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20"]
        userCreation = countbygender(clazzname,"createdby_id",userCreation_groups, county=county, state=state)
        stats["userCreation"] = userCreation

        multipleStat(stats, clazzname,{
                    "county":["Distrito",[
                        "san-jose",
                        "escazu",
                        "desamparados",
                        "puriscal",
                        "tarrazu",
                        "aserri",
                        "mora",
                        "goicoechea",
                        "santa-ana",
                        "alajuelita",
                        "vazquez-de-coronado",
                        "acosta",
                        "tibas",
                        "moravia",
                        "montes-de-oca",
                        "turrubares",
                        "dota",
                        "curridabat",
                        "perez-zeledon",
                        "leon-cortes-castro",
                        "alajuela",
                        "san-ramon",
                        "grecia",
                        "san-mateo",
                        "atenas",
                        "naranjo",
                        "palmares",
                        "poas",
                        "orotina",
                        "san-carlos",
                        "zarcero",
                        "valverde-vega",
                        "upala",
                        "los-chiles",
                        "guatuso",
                        "rio-cuarto",
                        "cartago",
                        "paraiso",
                        "la-union",
                        "jimenez",
                        "turrialba",
                        "alvarado",
                        "oreamuno",
                        "el-guarco",
                        "heredia",
                        "barva",
                        "santo-domingo",
                        "santa-barbara",
                        "san-rafael",
                        "san-isidro",
                        "belen",
                        "flores",
                        "san-pablo",
                        "sarapiqui",
                        "liberia",
                        "nicoya",
                        "santa-cruz",
                        "bagaces",
                        "carrillo",
                        "cañas",
                        "abangares",
                        "tilaran",
                        "nandayure",
                        "la-cruz",
                        "hojancha",
                        "puntarenas",
                        "esparza",
                        "buenos-aires",
                        "montes-de-oro",
                        "osa",
                        "quepos",
                        "golfito",
                        "coto-brus",
                        "parrita",
                        "corredores",
                        "garabito",
                        "monteverde",
                        "puerto-jimenez",
                        "limon",
                        "pococí",
                        "siquirres",
                        "talamanca",
                        "matina",
                        "guacimo"
                    ]],
                    "party":["Partido político con el que se identifica",["Liberación Nacional",
                        "Unidad Social Cristiano",
                        "Liberal Progresista",
                        "Nueva República",
                        "Pueblo Soberano",
                        "Unidos Podemos",
                        "Frente Amplio",
                        "PAC",
                        "Aquí Costa Rica Manda",
                        "Progreso Social Democrático",
                        "Nueva Generación",
                        "Justicia Social",
                        "Costa Rica Primero",
                        "Republicano",
                        "Otro",
                        "Ninguno",
                        "NS/NR"]],
                    "chavesSupport":["Apoya usted la gestión del presidente Rodrigo Chaves?",["a. Sí","b. No","c. NS/NR"]],
                    "nationalElection":["¿Si las elecciones fueran hoy, por quién votaría?",[
                        "Laura Fernández PPS",
                        "Fabricio Alvarado NR",
                        "Fernando Zamora PNG",
                        "Álvaro Ramos PLN",
                        "Natalia Díaz UP",
                        "Eliécer Feinzaig PLP",
                        "Ariel Robles Frente Amplio",
                        "Claudia Dobles PAC",
                        "Claudio Alpízar Esperanza Nacional",
                        "Jorge Acuña PRSC",
                        "Luz Mary Alpízar PSD",
                        "José Aguilar Berrocal Avance",
                        "Juan Carlos Hidalgo PUSC",
                        "Luis Amador CR1",
                        "Otro",
                        "Ninguno",
                        "NS/NR"
                    ]]
                }, county=county, state=state)
        print(stats)
        return stats
    elif record_id == 17:
        from utils.methods import session

        stats = {}


        ### gender groups
        masc = field_count(clazzname,"gender", "A. Masculino", county=county, state=state)
        fem = field_count(clazzname,"gender", "B. Femenino", county=county, state=state)
        tot = masc + fem
        gender = {
                "Hombres":masc,
                "Mujeres":fem,
                "Total":tot
        }
        stats["gender"] = gender

        ### Age groups
        age_groups = [
        "a. 18 -20", "b. 21 - 24", "c. 25 - 29", "d. 30 - 34",
        "e. 35 - 39", "f. 40 - 44", "g. 45 - 49", "h. 50 - 54",
        "i. 55 - 59", "j. 60 - 64", "k. 65 - 69", "l. 70 - 79",
        "m. + 80"
        ]
        age = countbygender(clazzname,"age",age_groups, county=county, state=state)
        stats["age"] = age
        ### User groups
        userCreation_groups = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20"]
        userCreation = countbygender(clazzname,"createdby_id",userCreation_groups, county=county, state=state)
        stats["userCreation"] = userCreation

        multipleStat(stats, clazzname,{
                    "county":["Distrito",[
                        "san-jose",
                        "escazu",
                        "desamparados",
                        "puriscal",
                        "tarrazu",
                        "aserri",
                        "mora",
                        "goicoechea",
                        "santa-ana",
                        "alajuelita",
                        "vazquez-de-coronado",
                        "acosta",
                        "tibas",
                        "moravia",
                        "montes-de-oca",
                        "turrubares",
                        "dota",
                        "curridabat",
                        "perez-zeledon",
                        "leon-cortes-castro",
                        "alajuela",
                        "san-ramon",
                        "grecia",
                        "san-mateo",
                        "atenas",
                        "naranjo",
                        "palmares",
                        "poas",
                        "orotina",
                        "san-carlos",
                        "zarcero",
                        "valverde-vega",
                        "upala",
                        "los-chiles",
                        "guatuso",
                        "rio-cuarto",
                        "cartago",
                        "paraiso",
                        "la-union",
                        "jimenez",
                        "turrialba",
                        "alvarado",
                        "oreamuno",
                        "el-guarco",
                        "heredia",
                        "barva",
                        "santo-domingo",
                        "santa-barbara",
                        "san-rafael",
                        "san-isidro",
                        "belen",
                        "flores",
                        "san-pablo",
                        "sarapiqui",
                        "liberia",
                        "nicoya",
                        "santa-cruz",
                        "bagaces",
                        "carrillo",
                        "cañas",
                        "abangares",
                        "tilaran",
                        "nandayure",
                        "la-cruz",
                        "hojancha",
                        "puntarenas",
                        "esparza",
                        "buenos-aires",
                        "montes-de-oro",
                        "osa",
                        "quepos",
                        "golfito",
                        "coto-brus",
                        "parrita",
                        "corredores",
                        "garabito",
                        "monteverde",
                        "puerto-jimenez",
                        "limon",
                        "pococí",
                        "siquirres",
                        "talamanca",
                        "matina",
                        "guacimo"
                    ]],
                    "religion":["Religión",["Católico",
                        "Cristiano / Evangélico (todas las demás)",
                        "Ateo",
                        "No religioso",
                        "Otro",
                        "NS/NR"]],
                    "education":["Nivel educativo (último concluido)",["Sin estudios",
                        "Primaria",
                        "Secundaria",
                        "Técnico",
                        "Universitaria",
                        "Posgrados",
                        "NS/NR"]],
                    "party":["Partido político con el que se identifica",[
                        "Acción Ciudadana",
                        "Aquí Costa Rica Manda",
                        "Avanza",
                        "Frente Amplio",
                        "Liberación Nacional",
                        "Liberal Progresista",
                        "Nueva Generación",
                        "Nueva República",
                        "Progreso Social Democrático",
                        "Pueblo Soberano",
                        "Unidad Social Cristiano",
                        "Unidos Podemos",
                        "Otro",
                        "Ninguno",
                        "NS/NR"]],
                    "chavesSupport":["Apoya usted la gestión del presidente Rodrigo Chaves?",["a. Sí","b. No","c. NS/NR"]],
                    "willvote":["¿Votará en las próximas elecciones nacionales?",["Sí","No","NS/NR"]],
                    "congressParty":["Si las elecciones fueran hoy ¿Por cuál partido votaría para diputados?",[
                        "Partido Pueblo Soberano",
                        "Nueva República",
                        "Partido Nueva Generación",
                        "PLN",
                        "Unidos Podemos",
                        "Partido Liberal Progresista",
                        "Frente Amplio",
                        "PAC",
                        "Esperanza Nacional",
                        "Partido Social Democrático",
                        "Avanza",
                        "PUSC",
                        "Nuestro Pueblo",
                        "Aquí CR Manda",
                        "Partido Centro Social Democrático",
                        "Partido Unión Costarricense Democrática",
                        "Otro",
                        "Ninguno",
                        "NS/NR"]],
                    "nationalElection":["¿Si las elecciones fueran hoy, por quién votaría?",[
                        "Laura Fernández PPS",
                        "Fabricio Alvarado NR",
                        "Fernando Zamora PNG",
                        "Álvaro Ramos PLN",
                        "Natalia Díaz UP",
                        "Eliécer Feinzaig PLP",
                        "Ariel Robles Frente Amplio",
                        "Claudia Dobles PAC",
                        "Claudio Alpízar Esperanza Nacional",
                        "Luz Mary Alpízar PSD",
                        "José Aguilar Berrocal Avance",
                        "Juan Carlos Hidalgo PUSC",
                        "Luis Amador Nuestro Pueblo",
                        "Ronny Castillo ACRM",
                        "Ana Virginia Calzada",
                        "Boris Molina",
                        "Otro",
                        "Ninguno",
                        "NS/NR"
                    ]]
                }, county=county, state=state)
        print(stats)
        return stats
    
    elif record_id == 18:
        from utils.methods import session

        stats = {}


        ### gender groups
        masc = field_count(clazzname,"gender", "A. Masculino", county=county, state=state)
        fem = field_count(clazzname,"gender", "B. Femenino", county=county, state=state)
        tot = masc + fem
        gender = {
                "Hombres":masc,
                "Mujeres":fem,
                "Total":tot
        }
        stats["gender"] = gender

        ### Age groups
        age_groups = [
        "a. 18 -20", "b. 21 - 24", "c. 25 - 29", "d. 30 - 34",
        "e. 35 - 39", "f. 40 - 44", "g. 45 - 49", "h. 50 - 54",
        "i. 55 - 59", "j. 60 - 64", "k. 65 - 69", "l. 70 - 79",
        "m. + 80"
        ]
        age = countbygender(clazzname,"age",age_groups, county=county, state=state)
        stats["age"] = age
        ### User groups
        userCreation_groups = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20"]
        userCreation = countbygender(clazzname,"createdby_id",userCreation_groups, county=county, state=state)
        stats["userCreation"] = userCreation

        multipleStat(stats, clazzname,{
                    "county":["Distrito",[
                        "san-jose",
                        "escazu",
                        "desamparados",
                        "puriscal",
                        "tarrazu",
                        "aserri",
                        "mora",
                        "goicoechea",
                        "santa-ana",
                        "alajuelita",
                        "vazquez-de-coronado",
                        "acosta",
                        "tibas",
                        "moravia",
                        "montes-de-oca",
                        "turrubares",
                        "dota",
                        "curridabat",
                        "perez-zeledon",
                        "leon-cortes-castro",
                        "alajuela",
                        "san-ramon",
                        "grecia",
                        "san-mateo",
                        "atenas",
                        "naranjo",
                        "palmares",
                        "poas",
                        "orotina",
                        "san-carlos",
                        "zarcero",
                        "valverde-vega",
                        "upala",
                        "los-chiles",
                        "guatuso",
                        "rio-cuarto",
                        "cartago",
                        "paraiso",
                        "la-union",
                        "jimenez",
                        "turrialba",
                        "alvarado",
                        "oreamuno",
                        "el-guarco",
                        "heredia",
                        "barva",
                        "santo-domingo",
                        "santa-barbara",
                        "san-rafael",
                        "san-isidro",
                        "belen",
                        "flores",
                        "san-pablo",
                        "sarapiqui",
                        "liberia",
                        "nicoya",
                        "santa-cruz",
                        "bagaces",
                        "carrillo",
                        "cañas",
                        "abangares",
                        "tilaran",
                        "nandayure",
                        "la-cruz",
                        "hojancha",
                        "puntarenas",
                        "esparza",
                        "buenos-aires",
                        "montes-de-oro",
                        "osa",
                        "quepos",
                        "golfito",
                        "coto-brus",
                        "parrita",
                        "corredores",
                        "garabito",
                        "monteverde",
                        "puerto-jimenez",
                        "limon",
                        "pococí",
                        "siquirres",
                        "talamanca",
                        "matina",
                        "guacimo"
                    ]],
                    "religion":["Religión",["Católico",
                        "Cristiano / Evangélico (todas las demás)",
                        "Ateo",
                        "No religioso",
                        "Otro",
                        "NS/NR"]],
                    "education":["Nivel educativo (último concluido)",["Sin estudios",
                        "Primaria",
                        "Secundaria",
                        "Técnico",
                        "Universitaria",
                        "Posgrados",
                        "NS/NR"]],
                    "party":["Partido político con el que se identifica",[
                        "Acción Ciudadana",
                        "Aquí Costa Rica Manda",
                        "Avanza",
                        "Frente Amplio",
                        "Liberación Nacional",
                        "Liberal Progresista",
                        "Nueva Generación",
                        "Nueva República",
                        "Progreso Social Democrático",
                        "Pueblo Soberano",
                        "Unidad Social Cristiano",
                        "Unidos Podemos",
                        "Otro",
                        "Ninguno",
                        "NS/NR"]],
                    "chavesSupport":["Apoya usted la gestión del presidente Rodrigo Chaves?",["a. Sí","b. No","c. NS/NR"]],
                    "chavesScale":["Del 1 al 10, como califica la labor de Rodrigo Chaves?",["1","2","3","4","5","6","7","8","9","10"]],
                    "congressParty":["Si las elecciones fueran hoy ¿Por cuál partido votaría para diputados?",[
                        "Partido Pueblo Soberano",
                        "Nueva República",
                        "Partido Nueva Generación",
                        "PLN",
                        "Unidos Podemos",
                        "Partido Liberal Progresista",
                        "Frente Amplio",
                        "PAC",
                        "Esperanza Nacional",
                        "Partido Social Democrático",
                        "Partido Integración Nacional",
                        "Avanza",
                        "PUSC",
                        "Aquí CR Manda",
                        "Partido Centro Social Democrático",
                        "Partido Unión Costarricense Democrática",
                        "Partido Justicia Social Costarricense",
                        "Costa Rica Primero",
                        "Otro",
                        "Ninguno",
                        "NS/NR"]],
                    "nationalElection":["¿Si las elecciones fueran hoy, por quién votaría?",[
                        "Laura Fernández PPS",
                            "Fabricio Alvarado NR",
                            "Fernando Zamora PNG",
                            "Álvaro Ramos PLN",
                            "Natalia Díaz UP",
                            "Eliécer Feinzaig PLP",
                            "Ariel Robles Frente Amplio",
                            "Claudia Dobles Coalición Agenda Ciudadana",
                            "Claudio Alpízar Esperanza Nacional",
                            "Luz Mary Alpízar PSD",
                            "José Aguilar Berrocal Avance",
                            "Juan Carlos Hidalgo PUSC",
                            "Luis Amador PIN",
                            "Ronny Castillo ACRM",
                            "Ana Virginia Calzada",
                            "Boris Molina",
                            "Otro",
                            "Ninguno",
                            "NS/NR"
                    ]],
                    "nationalElectionSecond":["¿Si las elecciones fueran hoy, por quién votaría?",[
                        "Laura Fernández PPS",
                            "Fabricio Alvarado NR",
                            "Fernando Zamora PNG",
                            "Álvaro Ramos PLN",
                            "Natalia Díaz UP",
                            "Eliécer Feinzaig PLP",
                            "Ariel Robles Frente Amplio",
                            "Claudia Dobles Coalición Agenda Ciudadana",
                            "Claudio Alpízar Esperanza Nacional",
                            "Luz Mary Alpízar PSD",
                            "José Aguilar Berrocal Avance",
                            "Juan Carlos Hidalgo PUSC",
                            "Luis Amador PIN",
                            "Ronny Castillo ACRM",
                            "Ana Virginia Calzada",
                            "Boris Molina",
                            "Otro",
                            "Ninguno",
                            "NS/NR"
                    ]]
                }, county=county, state=state)
        multipleOpinionStat(stats, clazzname,{
            "Juan Carlos Hidalgo":["conoceJuanCarlos","opinionJuanCarlos"],
            "Walter Rubén Hernández":["conoceWalter","opinionWalter"],
            "Laura Fernández ":["conoceLauraFernandez","opinionLauraFernandez"],
            "Natalia Diaz":["conoceNataliaDiaz","opinionNataliaDiaz"],
            "Ariel Robles":["conoceArielRobles","opinionArielRobles"]
        }, county=county, state=state)
        print(stats)
        return stats
    