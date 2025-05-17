def field_count(clazz,field, value, gender=None):
    from utils.methods import session
    query = session.newQuery(clazz)
    query.addFilter(field, "==", value)
    if gender:
        query.addFilter("gender", "==", gender)
    return query.count()

def field_count_user(clazz,field, value, user, gender=None):
    from utils.methods import session
    query = session.newQuery(clazz)
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
    userCreation_groups = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20"]
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


def generateReport(clazzname,record_id):
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
        query = None

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

        ### chavesSupport
        chavesSupport_groups = ["a. Sí","b. No","c. NS/NR"]
        chavesSupport = countbygender(clazzname,"chavesSupport",chavesSupport_groups)

        stats = {
            "age":age,
            "gender":gender,
            "userCreation":userCreation,
            "state":state,
            "party":party,
            "generalElections":generalElections,
            "secondNationalElections":secondNationalElections,
            "chavesSupport":chavesSupport
        }
        print(stats)
        return stats