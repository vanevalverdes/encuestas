def field_count(clazz,field, value, gender=None):
    from utils.methods import session
    query = session.newQuery(clazz)
    query.addFilter(field, "==", value)
    if gender:
        query.addFilter("gender", "==", gender)
    return query.count()

def field_count_user(clazz,field, value, user, gender=None):
    from utils.methods import session
    query = session.newQuery("survey")
    query.addFilter(field, "==", value)
    query.addFilter("createdby_id", "==", user)
    query.filterByToday()
    if gender:
        query.addFilter("gender", "==", gender)
    return query.count()

def countbygender(clazz,fieldname,values):
    
    ### Cuenta por campo y género
    counts = {
        field: [
            field_count(clazz,fieldname, field, "A. Masculino"),
            field_count(clazz,fieldname, field, "B. Femenino"),
            field_count(clazz,fieldname, field)
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
                field_count_user(clazz,fieldname, field, user, "A. Masculino"),
                field_count_user(clazz,fieldname, field, user, "B. Femenino"),
                field_count_user(clazz,fieldname, field, user)
            ]
            usersValues[user] = userArray
        values.append(usersValues)
    return counts


def generateReport():
    from utils.methods.stats import field_count, countbygender
    clazzname = "surveymarchtwo"
    """
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
    """
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
    plnCandidate_groups = ["a. Gilbert Jiménez","b. Carolina Delgado","c. Alvaro Ramos","d. Marvin Taylor","e. NS/NR","f. Ninguno"]
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