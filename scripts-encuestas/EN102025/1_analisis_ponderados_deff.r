# ==============================================================================
# PROCESO CONSOLIDADO: PONDERACIÓN, DISEÑO COMPLEJO Y CÁLCULO DEFF (TSE)
# ==============================================================================

# 1. CARGA DE LIBRERÍAS Y CONFIGURACIÓN
# -------------------------------------
library(dplyr)
library(readr)
library(survey) 

# Permite que el paquete survey ajuste la varianza cuando un estrato solo tiene una UPM
options(survey.lonely.psu = "adjust") 

# 2. DEFINICIÓN DE DATOS POBLACIONALES (PADRÓN ELECTORAL)
# --------------------------------------------------------

# 2.A. Tabla de Proporciones (P_j) para PONDERACIÓN (ACTUALIZADA con Edad)
# 7 Provincias * 2 Sexos * 3 Edades = 42 celdas.

# 1. Datos poblacionales desagregados proporcionados por el usuario (Totales de Electores por Celda)
poblacion_conteo <- data.frame(
    provincia = c(rep("san-jose", 6), rep("alajuela", 6), rep("cartago", 6), rep("heredia", 6), rep("guanacaste", 6), rep("puntarenas", 6), rep("limon", 6)),
    grupo_edad = rep(c("Adulto", "Adulto", "Joven", "Joven", "AdultoMayor", "AdultoMayor"), 7),
    sexo = rep(c("H", "M"), 21),
    conteo = c(
        # SAN JOSE
        279327, 290835, 209504, 204246, 89404, 116464,
        # ALAJUELA
        170927, 169635, 138468, 131485, 51980, 57462,
        # CARTAGO
        103211, 106173, 77842, 75105, 30271, 34828,
        # HEREDIA
        90334, 93587, 67514, 65475, 26457, 33133,
        # GUANACASTE
        66004, 65182, 52843, 51148, 20286, 21642,
        # PUNTARENAS
        84643, 82204, 67259, 65331, 26108, 24752,
        # LIMON
        73427, 71246, 64744, 63371, 21219, 18888
    )
)

# 2. Cálculo del total nacional y la Proporción P_j para cada celda.
# Usamos 3,619,099 como total de la población con segregación de sexo y edad por provincias.
TOTAL_NACIONAL_NUEVO <- sum(poblacion_conteo$conteo) 

poblacion_tse <- poblacion_conteo %>%
    mutate(P_j = conteo / TOTAL_NACIONAL_NUEVO) %>%
    mutate(celda_ponderacion = paste(sexo, grupo_edad, provincia, sep = "_")) %>%
    select(celda_ponderacion, P_j)


# 2.B. Tabla de Totales Provinciales (N_h) para FPC (NO CAMBIA)
poblacion_provincia <- data.frame(
    estrato_provincia = c("san-jose", "alajuela", "cartago", "heredia", "guanacaste", "puntarenas", "limon"),
    # Se mantienen los N_provincia originales del usuario para el FPC
    N_provincia = c(1192706, 723861, 429191, 378289, 278818, 351197, 313972)
)

# 3. CARGA Y LIMPIEZA DE LA BASE DE LA ENCUESTA (ACTUALIZADA con Edad)
# ---------------------------------------------
df <- read_csv("C:\\Users\\vanev\\Downloads\\Opol EN102025\\Base de datos\\survey.csv") # Usando la ruta del usuario

df <- df %>%
    rename(
        sexo_raw = gender,
        conglomerado_canton = county,
        estrato_provincia = state,
        partido_preferente = party,
        educacion = education,
        voto_presidente = nationalElection,
        votara = willvote,
        voto_diputado = congress,
        edad_raw = age
    ) %>% 
    mutate(
        sexo = case_when(
            grepl("Femenino", sexo_raw, ignore.case = TRUE) ~ "M",
            grepl("Masculino", sexo_raw, ignore.case = TRUE) ~ "H",
            TRUE ~ "NA_SEXO"
        ),
        # Crucial: Estandarizar PROVINCIA a MINÚSCULAS para el join
        provincia = tolower(estrato_provincia),
        
        # Mapeo de rangos de edad de la encuesta a grupos de ponderación (TSE)
        grupo_edad = case_when(
            # Jóvenes: Menores de 35 años (inclusive)
            edad_raw %in% c("18-20", "21-24", "25-29", "30-34") ~ "Joven",
            # Adultos: De 36 a menores de 65 años
            edad_raw %in% c("35-39", "40-44", "45-49", "50-54", "55-59", "60-64") ~ "Adulto",
            # Adultos Mayores: De 65 años y más
            edad_raw %in% c("65-69", "70-79", "+80") ~ "AdultoMayor",
            TRUE ~ "NA_EDAD"
        )
    ) %>%
    # Celda de ponderación de TRES factores
    mutate(celda_ponderacion = paste(sexo, grupo_edad, provincia, sep = "_"))


# 4. CÁLCULO DE LA PONDERACIÓN
# ----------------------------

frecuencia_muestral <- df %>%
    group_by(celda_ponderacion) %>%
    summarise(n_j = n()) %>%
    ungroup() %>%
    mutate(p_j = n_j / sum(n_j))

df_ajustada <- frecuencia_muestral %>%
    left_join(poblacion_tse, by = "celda_ponderacion") %>%
    # p_j es la proporción muestral, P_j es la proporción poblacional
    mutate(ponderador_final = P_j / p_j)

df <- df %>%
    left_join(df_ajustada %>% select(celda_ponderacion, ponderador_final), 
              by = "celda_ponderacion") %>%
    # Si alguna celda no hizo match (ej: provincia no reconocida), se le asigna ponderador 1.0
    mutate(ponderador_final = if_else(is.na(ponderador_final), 1.0, ponderador_final))


# 5. PREPARACIÓN FINAL DE LA MUESTRA PARA SURVEY (Corrigiendo el problema de DEFF)
# ------------------------------------------------------------------------------

df_analisis <- df %>%
    # 5.1. FILTRAR SÓLO LAS ENCUESTAS VÁLIDAS
    filter(category == 1) %>% 
    # 5.2. Crear ID de conglomerado ÚNICO
    mutate(conglomerado_unico = paste(estrato_provincia, conglomerado_canton, sep = "_")) %>%
    # 5.3. Unir el Total de Población de la Provincia (N_provincia) para FPC
    # Nota: Usamos la columna 'provincia' limpia para el join
    left_join(poblacion_provincia, by = c("provincia" = "estrato_provincia")) %>%
    # 5.4. VERIFICACIÓN CRÍTICA DEL FPC: Eliminar filas que no se unieron con la población
    filter(!is.na(ponderador_final) & !is.na(conglomerado_unico) & !is.na(N_provincia))


# 3.1. Calcular el tamaño de la muestra por estrato (n_h)
tamanio_muestral_provincia <- df_analisis %>%
    group_by(provincia) %>%
    summarise(n_provincia = n()) %>%
    ungroup()

# 3.2. Unir el tamaño muestral (n_h) al DF analizado
df_analisis <- df_analisis %>%
    left_join(tamanio_muestral_provincia, by = "provincia")


# 4. DEFINICIÓN DEL DISEÑO Y CÁLCULO FINAL
# -----------------------------------------

# 4.1. Definición del Diseño de Muestreo Complejo
# (Usamos la columna N_provincia, que contiene N_h, y R infiere n_h)
encuesta_dsn <- svydesign(
    ids = ~conglomerado_unico,         
    strata = ~provincia,               
    weights = ~ponderador_final,       
    data = df_analisis,                
    fpc = ~N_provincia                 
)

# 4.2. Cálculo del Análisis (Proporción de Voto)
votara_resultado <- svymean(~votara, design = encuesta_dsn, na.rm = TRUE)

# 4.3. Extracción de Métricas: DEFF y ME
# ---------------------------------------

# 1. Intentar cálculo de DEFF con la función nativa (si falla, pasa al manual)
deff_real <- tryCatch({
    deff(votara_resultado) 
}, warning = function(w) {
    # 2. CAÍDA AL CÁLCULO MANUAL (SI LA FUNCIÓN DEFF FALLA)
    
    # a. Extraer la Varianza Compleja (Var_Comp) a partir del Error Estándar (SE) ajustado
    SE_ajustado <- SE(votara_resultado)
    varianza_compleja <- SE_ajustado^2
    
    # b. Extraer la Estimación Ponderada de la Proporción (p_hat)
    # y el tamaño total de la muestra (n)
    p_hat <- as.numeric(votara_resultado) # La proporción estimada (ej: 0.35)
    n_total <- nrow(df_analisis) # El número total de encuestas válidas (n)
    
    # c. Calcular la Varianza MAS (Var_MAS)
    # Fórmula: p_hat * (1 - p_hat) / (n - 1)
    varianza_mas <- (p_hat * (1 - p_hat)) / (n_total - 1)
    
    # d. Calcular el DEFF Manual
    # Fórmula: Var_Comp / Var_MAS
    deff_manual <- varianza_compleja / varianza_mas
    
    return(deff_manual)
})

# 3. Finalizar cálculo del Margen de Error
SE_ajustado <- SE(votara_resultado)
ME_final_porcentaje <- SE_ajustado * 1.96 * 100 # Z=1.96 para 95% Confianza


# 5. IMPRESIÓN DEFF FINAL
# -----------------------------------

cat("\nEfecto de Diseño (DEFF) Real (Calculado manualmente como respaldo):", round(deff_real, 3), "\n")
cat("Margen de Error Final (95% Conf. - Ajustado por DEFF): ±", round(ME_final_porcentaje, 2), "%\n")

