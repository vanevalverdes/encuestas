
def field_count(clazz,field, value, gender=None,county=None,state=None):
    from utils.packages import session
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

def getOptions(fieldclass,fieldname):
    return fieldclass[fieldname]["select_options"]


def generateReport(clazzname,record_id, county=None, state=None):
    stats = {}
    from utils.packages import session
    from utils.view_class_container_fields import get_clazz_fields
    fieldclass =   get_clazz_fields(clazzname)
    

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
