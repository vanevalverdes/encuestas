1# ==============================================================================
# SCRIPT CONSOLIDADO: PROCESAMIENTO, ANÁLISIS Y EXPORTACIÓN DE ENCUESTAS OPOL
# ==============================================================================

# 1. CARGA DE LIBRERÍAS Y CONFIGURACIÓN
# -------------------------------------
library(dplyr)
library(readr)
library(survey)
library(tidyr)
library(ggplot2)
library(forcats)
library(tibble)
library(knitr)
library(gridExtra)

# Permite que el paquete survey ajuste la varianza cuando un estrato solo tiene una UPM
options(survey.lonely.psu = "adjust") 

# -----------------------------------------------------------------------------
# 2. DEFINICIÓN DE DATOS POBLACIONALES (PADRÓN ELECTORAL)
# -----------------------------------------------------------------------------

# 2.A. Tabla de Proporciones (P_j) para PONDERACIÓN (Sexos x Edades x Provincias)
poblacion_conteo <- data.frame(
  provincia = c(rep("san-jose", 6), rep("alajuela", 6), rep("cartago", 6), rep("heredia", 6), rep("guanacaste", 6), rep("puntarenas", 6), rep("limon", 6)),
  grupo_edad = rep(c("Adulto", "Adulto", "Joven", "Joven", "AdultoMayor", "AdultoMayor"), 7),
  sexo = rep(c("H", "M"), 21),
  conteo = c(
    # SAN JOSE
    281336, 292403, 205013, 199844, 92361, 120143,
    # ALAJUELA
    172861, 171288, 136355, 129295, 54006, 59625,
    # CARTAGO
    104210, 107116, 76258, 73722, 31393, 36126,
    # HEREDIA
    91314, 94365, 66138, 64234, 27434, 34306,
    # GUANACASTE
    66748, 65906, 52023, 50381, 21055, 22475,
    # PUNTARENAS
    85488, 83051, 65882, 63962, 26997, 25626,
    # LIMON
    74278, 72062, 63544, 62269, 21947, 19678
  )
)

TOTAL_NACIONAL_NUEVO <- sum(poblacion_conteo$conteo) 

poblacion_tse <- poblacion_conteo %>%
  mutate(P_j = conteo / TOTAL_NACIONAL_NUEVO) %>%
  mutate(celda_ponderacion = paste(sexo, grupo_edad, provincia, sep = "_")) %>%
  select(celda_ponderacion, P_j)


# 2.B. Tabla de Totales Provinciales (N_h) para FPC
poblacion_provincia <- data.frame(
  estrato_provincia = c("san-jose", "alajuela", "cartago", "heredia", "guanacaste", "puntarenas", "limon"),
  N_provincia = c(1191100, 723430, 428825, 377791, 278588, 351006, 313778)
)

# -----------------------------------------------------------------------------
# 3. CARGA, LIMPIEZA Y CÁLCULO DE LA PONDERACIÓN
# -----------------------------------------------------------------------------

# !!! RECUERDA: Cambiar la ruta del archivo CSV a tu ruta local actual.
RUTA_BASE_DATOS <- "C:\\Users\\vanev\\Documents\\Opol\\Opol IX EEN - ENE26\\survey.csv"
df <- read_delim(RUTA_BASE_DATOS, delim = ",", show_col_types = FALSE)

df <- df %>%
  rename(
    sexo_raw = gender,
    conglomerado_canton = county,
    estrato_provincia = state,
    voto_presidente = nationalElection,
    presidente_escala = presidentScale,
    votara = willvote,
    escala_voto = voteScale,
    voto_diputado = congress,
    edad_raw = age
  ) %>% 
  mutate(
    sexo = case_when(
      grepl("M", sexo_raw, ignore.case = TRUE) ~ "M",
      grepl("H", sexo_raw, ignore.case = TRUE) ~ "H",
      TRUE ~ "NA_SEXO"
    ),
    provincia = tolower(estrato_provincia),
    grupo_edad = case_when(
      edad_raw %in% c("18-20", "21-24", "25-29", "30-34") ~ "Joven",
      edad_raw %in% c("35-39", "40-44", "45-49", "50-54", "55-59", "60-64") ~ "Adulto",
      edad_raw %in% c("65-69", "70-79", "+80") ~ "AdultoMayor",
      TRUE ~ "NA_EDAD"
    )
  ) %>%
  mutate(celda_ponderacion = paste(sexo, grupo_edad, provincia, sep = "_"))

# CÁLCULO DE LA PONDERACIÓN POR POST-ESTRATIFICACIÓN
frecuencia_muestral <- df %>%
  group_by(celda_ponderacion) %>%
  summarise(n_j = n()) %>%
  ungroup() %>%
  mutate(p_j = n_j / sum(n_j))

df_ajustada <- frecuencia_muestral %>%
  left_join(poblacion_tse, by = "celda_ponderacion") %>%
  mutate(ponderador_final = P_j / p_j)

df <- df %>%
  left_join(df_ajustada %>% select(celda_ponderacion, ponderador_final),
            by = "celda_ponderacion") %>%
  mutate(ponderador_final = if_else(is.na(ponderador_final), 1.0, ponderador_final))


# -----------------------------------------------------------------------------
# 4. DEFINICIÓN DE BASES DE ANÁLISIS Y DISEÑOS SURVEY
# -----------------------------------------------------------------------------
# CÁLCULO DE LA TASA DE RESPUESTA AJUSTADA (RR2)
n_total_cargado <- nrow(df) # 3715

# Conteo de categorías para el cálculo de la Tasa de Respuesta
conteo_categorias <- df %>%
    group_by(category) %>%
    summarise(n = n())

# N Válido (Completadas, C)
n_valido <- conteo_categorias %>% filter(category == 1) %>% pull(n)
if (length(n_valido) == 0) { n_valido <- 0 } # Fallback si no hay Cat 1

# N No Elegible (NE). Asumiendo que category == 4 son No Elegibles.
n_no_elegible <- conteo_categorias %>% filter(category == 4) %>% pull(n)
if (length(n_no_elegible) == 0) { n_no_elegible <- 0 } # Fallback

# N Total de Elegibles (E)
# E = Total intentos (3715) - No Elegibles (Cat 4)
n_elegible_total <- n_total_cargado - n_no_elegible

# Tasa de Respuesta Ajustada (RR2): C / E * 100
# Esta es la tasa de completación sobre el total de casos que eran elegibles.
tasa_respuesta_porcentaje <- (n_valido / n_elegible_total) * 100

# Tasa de Rechazo: 100 - RR2
tasa_rechazo_porcentaje <- 100 - tasa_respuesta_porcentaje


# 4.1. BASE 1: Total de Encuestas Válidas (category == 1)
df_analisis_total <- df %>%
  filter(category == 1) %>%
  mutate(conglomerado_unico = paste(estrato_provincia, conglomerado_canton, sep = "_")) %>%
  left_join(poblacion_provincia, by = c("provincia" = "estrato_provincia")) %>%
  filter(!is.na(ponderador_final) & !is.na(conglomerado_unico) & !is.na(N_provincia))

# Cálculo de n_h para el FPC
tamanio_muestral_provincia_total <- df_analisis_total %>%
  group_by(provincia) %>%
  summarise(n_provincia = n()) %>%
  ungroup()

df_analisis_total <- df_analisis_total %>%
  left_join(tamanio_muestral_provincia_total, by = "provincia")

# DISEÑO DE MUESTREO COMPLEJO 1 (Base Total Válida)
encuesta_dsn_total <- svydesign(
  ids = ~conglomerado_unico,
  strata = ~provincia,
  weights = ~ponderador_final,
  data = df_analisis_total,
  fpc = ~N_provincia
)

# 4.2. BASE 2: Votantes Válidos (Decididos a votar: votara == 'Sí')
################# OJO: NUEVA ESCALA DE VOTO SOLO LOS QUE MARCAN 5 O 4 EN VOTESCALE
df_analisis_nacional <- df_analisis_total %>%
  filter(votara == 'Sí')
  #filter(votara == 'Sí' & escala_voto == '5')

# Recálculo de n_h para el FPC (en la submuestra)
tamanio_muestral_provincia_nacional <- df_analisis_nacional %>%
  group_by(provincia) %>%
  summarise(n_provincia = n()) %>%
  ungroup()

df_analisis_nacional <- df_analisis_nacional %>%
  left_join(tamanio_muestral_provincia_nacional, by = "provincia")

# DISEÑO DE MUESTREO COMPLEJO 2 (Base Votantes Válidos)
encuesta_dsn <- svydesign(
  ids = ~conglomerado_unico,
  strata = ~provincia,
  weights = ~ponderador_final,
  data = df_analisis_nacional,
  fpc = ~N_provincia
)

# 4.3. BASE 3: Votantes Válidos (Decididos a votar: votara == 'Sí') y Con Alta Seguridad de Voto
df_analisis_nacional_presidente_escala <- df_analisis_nacional %>%
  filter(presidente_escala != 'NULL')

# Recálculo de n_h para el FPC (en la submuestra)
tamanio_muestral_provincia_nacional_presidente_escala <- df_analisis_nacional_presidente_escala %>%
  group_by(provincia) %>%
  summarise(n_provincia = n()) %>%
  ungroup()

df_analisis_nacional_presidente_escala <- df_analisis_nacional_presidente_escala %>%
  left_join(tamanio_muestral_provincia_nacional_presidente_escala, by = "provincia")

# DISEÑO DE MUESTREO COMPLEJO 3 (Base Votantes Válidos con Alta Seguridad de Voto)
encuesta_dsn_presidente_escala <- svydesign(
  ids = ~conglomerado_unico,
  strata = ~provincia,
  weights = ~ponderador_final,
  data = df_analisis_nacional_presidente_escala,
  fpc = ~N_provincia
)

# -----------------------------------------------------------------------------
# 5. CÁLCULO DE RESULTADOS NACIONALES CLAVE (svymean, DEFF, ME)
# -----------------------------------------------------------------------------

# Cálculos de resultados
votara_resultado <- svymean(~votara, design = encuesta_dsn_total, na.rm = TRUE)

presidente_escala_resultado <- svymean(~presidente_escala, design = encuesta_dsn_presidente_escala, na.rm = TRUE) # Base Votantes
escala_resultado <- svymean(~escala_voto, design = encuesta_dsn, na.rm = TRUE) # Base Votantes
presidente_resultado <- svymean(~voto_presidente, design = encuesta_dsn, na.rm = TRUE) # Base Votantes
diputado_resultado <- svymean(~voto_diputado, design = encuesta_dsn, na.rm = TRUE) # Base Votantes

# CÁLCULO DE DEFF Y MARGEN DE ERROR MÁXIMO
# -----------------------------------------------------------------

sexo_resultado <- svymean(~sexo, design = encuesta_dsn_total, na.rm = TRUE)
# 1. Intentar cálculo de DEFF (si falla, pasa al manual)
deff_real <- tryCatch({
    deff(votara_resultado) 
}, warning = function(w) {
    SE_ajustado <- SE(votara_resultado)
    varianza_compleja <- SE_ajustado^2
    p_hat <- as.numeric(votara_resultado) 
    n_total <- nrow(df_analisis_total) # n total de la base usada para 'votara'
    varianza_mas <- (p_hat * (1 - p_hat)) / (n_total - 1)
    deff_manual <- varianza_compleja / varianza_mas
    return(deff_manual)
})

# 2. Finalizar cálculo del Margen de Error
SE_ajustado <- SE(votara_resultado)
ME_final_porcentaje <- SE_ajustado * 1.96 * 100 # Z=1.96 para 95% Confianza


# IMPRESIÓN DE RESULTADOS Y MÉTRICAS
# ----------------------------------
cat("\n======================================================\n")
cat("      MÉTRICAS DE DISEÑO Y ERROR Y RESPUESTA          \n")
cat("======================================================\n")
cat("Tamaño de Muestra Bruta (Intentos):", n_total_cargado, "\n")
cat("Tamaño de Casos Elegibles (E):", n_elegible_total, "\n")
cat("Tamaño de Muestra Válida (n):", n_valido, "\n")
cat("Tasa de Respuesta Ajustada (RR2):", round(tasa_respuesta_porcentaje, 2), "%\n")
cat("Tasa de Rechazo (Inversa de RR2):", round(tasa_rechazo_porcentaje, 2), "%\n")
cat("------------------------------------------------------\n")
# IMPRESIÓN DE RESULTADOS Y MÉTRICAS
# ----------------------------------
cat("Efecto de Diseño (DEFF) (Base Total Válida):", round(deff_real, 2), "\n")
cat("Margen de Error Final (95% Conf. - Ajustado por DEFF): ±", round(ME_final_porcentaje, 2), "%\n")
cat("======================================================\n")

cat("\n======================================================\n")
cat("       RESULTADOS NACIONALES PONDERADOS      \n")
cat("======================================================\n")
cat("Escala de decididos a votar:\n")
print(escala_resultado)
cat("Estimación Ponderada del Voto a Diputados:\n")
print(diputado_resultado)
cat("\nEstimación Ponderada del Voto Presidencial:\n")
print(presidente_resultado)
cat("======================================================\n")

# -----------------------------------------------------------------------------
# 6. TABLA CONSOLIDADA ESTILO IMAGEN (SEXO, EDAD, PROVINCIA)
# -----------------------------------------------------------------------------

# 1. Crear resúmenes individuales para cada variable
# --- Bloque SEXO ---
resumen_sexo <- df_analisis_total %>%
  group_by(Variable = sexo) %>%
  summarise(n = n(), n_pond = sum(ponderador_final)) %>%
  mutate(Ponderador = "Sexo")

# --- Bloque EDAD ---
resumen_edad <- df_analisis_total %>%
  group_by(Variable = grupo_edad) %>%
  summarise(n = n(), n_pond = sum(ponderador_final)) %>%
  mutate(Ponderador = "Grupo edad")

# --- Bloque PROVINCIA ---
resumen_provincia <- df_analisis_total %>%
  group_by(Variable = provincia) %>%
  summarise(n = n(), n_pond = sum(ponderador_final)) %>%
  mutate(Ponderador = "Provincia")

# 2. Unir y calcular porcentajes usando MESS por bloque
tabla_consolidada <- bind_rows(resumen_sexo, resumen_edad, resumen_provincia) %>%
  # Unir con totales de población (basado en tu tabla poblacion_conteo)
  left_join(
    bind_rows(
      poblacion_conteo %>% group_by(Variable = sexo) %>% summarise(N_pob = sum(conteo)),
      poblacion_conteo %>% group_by(Variable = grupo_edad) %>% summarise(N_pob = sum(conteo)),
      poblacion_conteo %>% group_by(Variable = provincia) %>% summarise(N_pob = sum(conteo))
    ), by = "Variable"
  ) %>%
  group_by(Ponderador) %>%
  mutate(
    `% Muestra Bruta` = MESS::round_percent(n, decimals = 2),
    `% Población` = MESS::round_percent(N_pob, decimals = 2),
    `% Muestra Ponderada` = MESS::round_percent(n_pond, decimals = 2)
  ) %>%
  ungroup() %>%
  select(Ponderador, Variable, `% Muestra Bruta`, `% Población`, `% Muestra Ponderada`)

# 3. Limpieza estética para el CSV (opcional: dejar solo la primera etiqueta de grupo)
tabla_final_export <- tabla_consolidada %>%
  mutate(Ponderador = if_else(duplicated(Ponderador), "", Ponderador))

# 4. Exportación
RUTA_EXPORTACION_CONSOLIDADA <- "C:\\Users\\vanev\\Documents\\Opol\\Opol IX EEN - ENE26\\CUADRO_CONSOLIDADO_PONDERACION.csv"

readr::write_csv(tabla_final_export, RUTA_EXPORTACION_CONSOLIDADA)

cat(paste0("\n✅ Cuadro consolidado exportado en: ", RUTA_EXPORTACION_CONSOLIDADA, "\n"))

# -----------------------------------------------------------------------------
# 6. TABLA COMPARATIVA DE DISTRIBUCIÓN Y EXPORTACIÓN CSV
# -----------------------------------------------------------------------------

# 1. Consolidación de datos
muestra_raw <- df_analisis_total %>%
  group_by(provincia, grupo_edad, sexo) %>%
  summarise(`Muestra Bruta (n)` = n(), .groups = 'drop')

poblacion_teorica <- poblacion_conteo %>%
  rename(`Población (N)` = conteo) %>%
  select(provincia, grupo_edad, sexo, `Población (N)`)

muestra_ponderada <- df_analisis_total %>%
  group_by(provincia, grupo_edad, sexo) %>%
  summarise(`Muestra Ponderada` = sum(ponderador_final), .groups = 'drop')

tabla_final <- muestra_raw %>%
  full_join(poblacion_teorica, by = c("provincia", "grupo_edad", "sexo")) %>%
  full_join(muestra_ponderada, by = c("provincia", "grupo_edad", "sexo"))

# 2. Cálculo de Porcentajes y Totales
Total_Muestra_Bruta <- sum(tabla_final$`Muestra Bruta (n)`, na.rm = TRUE)
Total_Poblacion <- sum(tabla_final$`Población (N)`, na.rm = TRUE)
Total_Muestra_Ponderada <- sum(tabla_final$`Muestra Ponderada`, na.rm = TRUE)

tabla_final_distribucion <- tabla_final %>%
  mutate(
    `% Muestra Bruta` = round((`Muestra Bruta (n)` / Total_Muestra_Bruta) * 100, 2),
    `% Población` = round((`Población (N)` / Total_Poblacion) * 100, 2),
    `% Muestra Ponderada` = round((`Muestra Ponderada` / Total_Muestra_Ponderada) * 100, 2)
  ) %>%
  select(
    Provincia = provincia, `Grupo Edad` = grupo_edad, Sexo = sexo,
    `Muestra Bruta (n)`, `% Muestra Bruta`,
    `Población (N)`, `% Población`,
    `Muestra Ponderada`, `% Muestra Ponderada`
  ) %>%
  arrange(Provincia, `Grupo Edad`, Sexo)

totales_row <- data.frame(
  Provincia = "TOTAL", `Grupo Edad` = "TOTAL", Sexo = "TOTAL",
  `Muestra Bruta (n)` = Total_Muestra_Bruta, `% Muestra Bruta` = 100.00,
  `Población (N)` = Total_Poblacion, `% Población` = 100.00,
  `Muestra Ponderada` = Total_Muestra_Ponderada, `% Muestra Ponderada` = 100.00
)

tabla_final_con_totales <- bind_rows(tabla_final_distribucion, totales_row)

# 3. Formato y Exportación
tabla_exportar <- tabla_final_con_totales
names(tabla_exportar) <- gsub(" ", "_", names(tabla_exportar))
names(tabla_exportar) <- gsub("\\.", "", names(tabla_exportar))

# !!! RECUERDA: Cambiar la ruta del archivo CSV de exportación.
RUTA_EXPORTACION_TABLA <- "C:\\Users\\vanev\\Documents\\Opol\\Opol IX EEN - ENE26\\DISTRIBUCION_MUESTRA_PONDERADA_FINAL.csv"

readr::write_csv(
  x = tabla_exportar,
  file = RUTA_EXPORTACION_TABLA,
  na = "",
  append = FALSE
)

cat(paste0("\n✅ Exportación de Distribución de Muestra/Población: ", RUTA_EXPORTACION_TABLA, "\n"))


# -----------------------------------------------------------------------------
# 7. TASAS DE NO RESPUESTA (RECHAZO) Y RESPUESTA PONDERADAS
# -----------------------------------------------------------------------------

extraer_rechazo <- function(resultado_svy) {
  resultado_df <- as.data.frame(resultado_svy)
  rechazo <- resultado_df %>%
    filter(grepl("No Responde", rownames(.), ignore.case = TRUE)) %>%
    pull(mean)
  return(ifelse(length(rechazo) == 0, 0, rechazo))
}

rechazo_votara_ponderada <- extraer_rechazo(votara_resultado)
rechazo_presidente_ponderada <- extraer_rechazo(presidente_resultado)
rechazo_diputado_ponderada <- extraer_rechazo(diputado_resultado)
rechazo_escala_ponderada <- extraer_rechazo(escala_resultado)
rechazo_presidente_escala <- extraer_rechazo(presidente_escala_resultado)

respuesta_votara_ponderada <- 1 - rechazo_votara_ponderada
respuesta_presidente_ponderada <- 1 - rechazo_presidente_ponderada
respuesta_diputado_ponderada <- 1 - rechazo_diputado_ponderada
respuesta_escala_ponderada <- 1 - rechazo_escala_ponderada
respuesta_presidente_escala <- 1 - rechazo_presidente_escala


cat("\n======================================================\n")
cat(" TASAS DE NO RESPUESTA (RECHAZO) Y RESPUESTA PONDERADAS\n")
cat("======================================================\n")

cat("1. Base Total Válida (Pregunta Votará):\n")
vals_vot <- MESS::round_percent(c(respuesta_votara_ponderada, rechazo_votara_ponderada), decimals = 2)
cat(paste(" - Tasa de Respuesta Ponderada (Sí/No):", vals_vot[1], "%\n"))
cat(paste(" - Tasa de Rechazo Ponderada (No Responde):", vals_vot[2], "%\n\n"))

cat("2. Base Votantes Válidos (Intención de Voto):\n")
cat(" - Escala seguros de votar:\n")
vals_escala <- MESS::round_percent(c(respuesta_escala_ponderada, rechazo_escala_ponderada), decimals = 2)
cat(paste("  - Tasa de Respuesta Ponderada:", vals_escala[1], "%\n"))
cat(paste("  - Tasa de Rechazo Ponderada (No Responde):", vals_escala[2], "%\n"))

cat(" - Voto Presidencial (Base Votantes):\n")
vals_presi <- MESS::round_percent(c(respuesta_presidente_ponderada, rechazo_presidente_ponderada), decimals = 2)
cat(paste("  - Tasa de Respuesta Ponderada (Candidato/Nulo/Blanco/NS):", vals_presi[1], "%\n"))
cat(paste("  - Tasa de Rechazo Ponderada (No Responde):", vals_presi[2], "%\n"))

cat(" - Escala de seguridad de Voto Presidencial (Base Votantes):\n")
vals_presi_escala <- MESS::round_percent(c(respuesta_presidente_escala, rechazo_presidente_escala), decimals = 2)
cat(paste("  - Tasa de Respuesta Ponderada (Candidato/Nulo/Blanco/NS):", vals_presi_escala[1], "%\n"))
cat(paste("  - Tasa de Rechazo Ponderada (No Responde):", vals_presi_escala[2], "%\n"))

cat(" - Voto Diputados (Base Votantes):\n")
vals_diputado <- MESS::round_percent(c(respuesta_diputado_ponderada, rechazo_diputado_ponderada), decimals = 2)
cat(paste("  - Tasa de Respuesta Ponderada (Candidato/Nulo/Blanco/NS):", vals_diputado[1], "%\n"))
cat(paste("  - Tasa de Rechazo Ponderada (No Responde):", vals_diputado[2], "%\n"))


cat("======================================================\n")


# -----------------------------------------------------------------------------
# 8. EXPORTACIONES CSV AVANZADAS (VOTO VÁLIDO POR PROVINCIA Y NACIONAL/SEXO)
# -----------------------------------------------------------------------------

categorias_no_validas <- c("No Responde", "Nulo", "En blanco", "No Sabe", "NS/NR", "En Blanco") 

# A. CÁLCULO DE VOTO POR PROVINCIA Y SEXO (Base Voto Válido)
# ----------------------------------------------------------

# 1. Combinar resultados por provincia/sexo y provincia/total
svy_sex_provincia <- svyby(~voto_presidente, by = ~provincia + sexo, design = encuesta_dsn, FUN = svymean, na.rm = TRUE)
svy_provincia_total <- svyby(~voto_presidente, by = ~provincia, design = encuesta_dsn, FUN = svymean, na.rm = TRUE) %>% mutate(sexo = "Total")
svy_combined <- bind_rows(svy_sex_provincia, svy_provincia_total)

# 2. Convertir a formato largo
resultados_long_provincia <- svy_combined %>% select(-starts_with("se.")) %>%
  pivot_longer(cols = starts_with("voto_presidente"), names_to = "Candidato_raw", values_to = "Proporcion") %>%
  mutate(Candidato = gsub("^voto_presidente", "", Candidato_raw)) %>%
 filter(!is.na(Proporcion))

# --- CÁLCULO DEL N PONDERADO POR SEGMENTO (Provincia/Sexo) ---
# Usamos el diseño encuesta_dsn (Votantes Válidos) para obtener el N ponderado por grupo
n_ponderado_segmento <- encuesta_dsn$variables %>%
 group_by(provincia, sexo) %>%
 # Sumar el ponderador_final para obtener el N efectivo del segmento
 summarise(N_Ponderado_Segmento = sum(ponderador_final, na.rm = TRUE), .groups = 'drop') %>%
 # Añadir el total por provincia
 bind_rows(
  encuesta_dsn$variables %>%
   group_by(provincia) %>%
   summarise(N_Ponderado_Segmento = sum(ponderador_final, na.rm = TRUE), .groups = 'drop') %>%
   mutate(sexo = "Total")
 )

# 3. Recálculo sobre Votos Válidos y CÁLCULO DE ABSOLUTOS PONDERADOS
resultados_validos_provincia <- resultados_long_provincia %>%
 mutate(es_valido = !Candidato %in% categorias_no_validas) %>%
 # Unir el N ponderado calculado
 left_join(n_ponderado_segmento, by = c("provincia", "sexo")) %>%
 
 group_by(provincia, sexo) %>%
 mutate(Suma_Proporcion_Valida = sum(Proporcion[es_valido]),
  Porcentaje_Voto_Valido = if_else(es_valido,MESS::round_percent(Proporcion / Suma_Proporcion_Valida, decimals = 2), 0.00),
  
  # CÁLCULO DEL ABSOLUTO PONDERADO: 
  # Porcentaje Voto Válido * Suma de la Proporción Válida de la celda * N Ponderado Total de la Muestra
  # Simplificando: La proporción del candidato (sin recalcular) * N ponderado total
  Absoluto_Ponderado_Total = Proporcion * N_Ponderado_Segmento,
  
  # Recalcular el Absoluto Ponderado SÓLO para Votos Válidos:
  # Porcentaje Voto Válido * (N ponderado total del segmento / 100)
  Absoluto_Voto_Valido = if_else(es_valido, (Porcentaje_Voto_Valido / 100) * (Absoluto_Ponderado_Total / Suma_Proporcion_Valida), 0.00)
 ) %>%
 ungroup() %>%
 filter(es_valido) 

# 4. Exportar a CSV
resultados_csv_provincia_voto_valido <- resultados_validos_provincia %>%
 select(Provincia = provincia, Segmento = sexo, Candidato, Absoluto_Voto_Valido, Porcentaje_Voto_Valido) %>%
 arrange(Provincia, Segmento, desc(Porcentaje_Voto_Valido))

RUTA_EXPORTACION_PROVINCIA_VOTO <- "C:\\Users\\vanev\\Documents\\Opol\\Opol IX EEN - ENE26\\intencion_voto_provincia_sexo_votos_validos.csv"
readr::write_csv(resultados_csv_provincia_voto_valido, RUTA_EXPORTACION_PROVINCIA_VOTO)
cat(paste0("✅ Exportación de Voto Válido por Provincia/Sexo (con Absolutos Ponderados): ", RUTA_EXPORTACION_PROVINCIA_VOTO, "\n"))


# -----------------------------------------------------------------------------
# 8.1 EXPORTACIONES CSV AVANZADAS DIPUTADOS (VOTO VÁLIDO POR PROVINCIA Y NACIONAL/SEXO)
# -----------------------------------------------------------------------------

categorias_no_validas <- c("No Responde", "Nulo", "En Blanco", "No Sabe", "NS/NR") 

# A. CÁLCULO DE VOTO POR PROVINCIA Y SEXO (Base Voto Válido)
# ----------------------------------------------------------

# 1. Combinar resultados por provincia/sexo y provincia/total
svy_sex_provincia <- svyby(~voto_diputado, by = ~provincia + sexo, design = encuesta_dsn, FUN = svymean, na.rm = TRUE)
svy_provincia_total <- svyby(~voto_diputado, by = ~provincia, design = encuesta_dsn, FUN = svymean, na.rm = TRUE) %>% mutate(sexo = "Total")
svy_combined <- bind_rows(svy_sex_provincia, svy_provincia_total)

# 2. Convertir a formato largo
resultados_long_provincia <- svy_combined %>% select(-starts_with("se.")) %>%
  pivot_longer(cols = starts_with("voto_diputado"), names_to = "Candidato_raw", values_to = "Proporcion") %>%
  mutate(Candidato = gsub("^voto_diputado", "", Candidato_raw)) %>%
 filter(!is.na(Proporcion))

# --- CÁLCULO DEL N PONDERADO POR SEGMENTO (Provincia/Sexo) ---
# Usamos el diseño encuesta_dsn (Votantes Válidos) para obtener el N ponderado por grupo
n_ponderado_segmento <- encuesta_dsn$variables %>%
 group_by(provincia, sexo) %>%
 # Sumar el ponderador_final para obtener el N efectivo del segmento
 summarise(N_Ponderado_Segmento = sum(ponderador_final, na.rm = TRUE), .groups = 'drop') %>%
 # Añadir el total por provincia
 bind_rows(
  encuesta_dsn$variables %>%
   group_by(provincia) %>%
   summarise(N_Ponderado_Segmento = sum(ponderador_final, na.rm = TRUE), .groups = 'drop') %>%
   mutate(sexo = "Total")
 )

# 3. Recálculo sobre Votos Válidos y CÁLCULO DE ABSOLUTOS PONDERADOS
resultados_validos_provincia <- resultados_long_provincia %>%
 mutate(es_valido = !Candidato %in% categorias_no_validas) %>%
 # Unir el N ponderado calculado
 left_join(n_ponderado_segmento, by = c("provincia", "sexo")) %>%
 
 group_by(provincia, sexo) %>%
 mutate(Suma_Proporcion_Valida = sum(Proporcion[es_valido])) %>%
 mutate(
  Porcentaje_Voto_Valido = if_else(es_valido, MESS::round_percent(Proporcion[es_valido] / Suma_Proporcion_Valida, decimals = 2), 0.00),
  
  # CÁLCULO DEL ABSOLUTO PONDERADO: 
  # Porcentaje Voto Válido * Suma de la Proporción Válida de la celda * N Ponderado Total de la Muestra
  # Simplificando: La proporción del candidato (sin recalcular) * N ponderado total
  Absoluto_Ponderado_Total = Proporcion * N_Ponderado_Segmento,
  
  # Recalcular el Absoluto Ponderado SÓLO para Votos Válidos:
  # Porcentaje Voto Válido * (N ponderado total del segmento / 100)
  Absoluto_Voto_Valido = if_else(es_valido, (Porcentaje_Voto_Valido / 100) * (Absoluto_Ponderado_Total / Suma_Proporcion_Valida), 0.00)
 ) %>%
 ungroup() %>%
 filter(es_valido) 

# 4. Exportar a CSV
resultados_csv_provincia_voto_valido <- resultados_validos_provincia %>%
 select(Provincia = provincia, Segmento = sexo, Candidato, Absoluto_Voto_Valido, Porcentaje_Voto_Valido) %>%
 arrange(Provincia, Segmento, desc(Porcentaje_Voto_Valido))

RUTA_EXPORTACION_PROVINCIA_VOTO <- "C:\\Users\\vanev\\Documents\\Opol\\Opol IX EEN - ENE26\\intencion_voto_diputados_provincia_sexo_votos_validos.csv"
readr::write_csv(resultados_csv_provincia_voto_valido, RUTA_EXPORTACION_PROVINCIA_VOTO)
cat(paste0("✅ Exportación de Voto Válido para diputados por Provincia/Sexo (con Absolutos Ponderados): ", RUTA_EXPORTACION_PROVINCIA_VOTO, "\n"))

# B. CÁLCULO DE VOTO NACIONAL POR SEXO (Base Voto Válido)
# -------------------------------------------------------

# 1. Combinar resultados por sexo y Nacional Total
svy_sex_nacional <- svyby(~voto_presidente, by = ~sexo, design = encuesta_dsn, FUN = svymean, na.rm = TRUE)
svy_nacional_total <- as.data.frame(svymean(~voto_presidente, design = encuesta_dsn, na.rm = TRUE)) %>%
  rownames_to_column(var = "Candidato_raw") %>% rename(Proporcion = mean) %>%
  pivot_wider(names_from = Candidato_raw, values_from = Proporcion) %>%
  mutate(sexo = "Nacional") %>%
  rename_with(~ sub("voto_presidente", "voto_presidente", .x), starts_with("voto_presidente")) %>%
  select(sexo, starts_with("voto_presidente"))

svy_combined_nacional <- bind_rows(svy_sex_nacional, svy_nacional_total)

# 2. Convertir a formato largo
resultados_nacional_long <- svy_combined_nacional %>%
  select(sexo, starts_with("voto_presidente")) %>% 
  pivot_longer(cols = starts_with("voto_presidente"), names_to = "Candidato_raw", values_to = "Proporcion") %>%
  mutate(Candidato = gsub("^voto_presidente", "", Candidato_raw)) %>%
  filter(!is.na(Proporcion)) 

# 3. Recálculo sobre Votos Válidos
resultados_nacional_validos <- resultados_nacional_long %>%
  mutate(es_valido = !Candidato %in% categorias_no_validas) %>%
  group_by(sexo) %>%
  mutate(Suma_Proporcion_Valida = sum(Proporcion[es_valido])) %>%
  mutate(
    Porcentaje_Voto_Valido = if_else(es_valido, MESS::round_percent(Proporcion[es_valido] / Suma_Proporcion_Valida, decimals = 2) , 0.00),
  ) %>%
  ungroup() %>%
  filter(es_valido) 

# 4. Exportar a CSV
resultados_csv_nacional_voto_valido <- resultados_nacional_validos %>%
  select(Segmento = sexo, Candidato, Porcentaje_Voto_Valido) %>%
  mutate(Segmento = factor(Segmento, levels = c("Nacional", "H", "M"))) %>%
  arrange(Segmento, desc(Porcentaje_Voto_Valido))

RUTA_EXPORTACION_NACIONAL_VOTO <- "C:\\Users\\vanev\\Documents\\Opol\\Opol IX EEN - ENE26\\intencion_voto_nacional_votos_validos_por_sexo.csv"
readr::write_csv(resultados_csv_nacional_voto_valido, RUTA_EXPORTACION_NACIONAL_VOTO)
cat(paste0("✅ Exportación de Voto Válido Nacional/Sexo: ", RUTA_EXPORTACION_NACIONAL_VOTO, "\n"))


# -----------------------------------------------------------------------------
# 9. GENERACIÓN DE GRÁFICOS (ALMACENADOS EN VARIABLES)
# -----------------------------------------------------------------------------

# CÁLCULO DE LA TABLA PONDERADA DEL VOTO PRESIDENCIAL (para gráficos)
presidente_resultado_df <- as.data.frame(presidente_resultado)

resultados_formateados <- presidente_resultado_df %>%
  rownames_to_column(var = "Candidato") %>%
  rename(Proporcion = mean, Error_Estandar = SE) %>%
  mutate(Candidato = gsub("^voto_presidente", "", Candidato)) %>%
  mutate(`Voto (%)` = MESS::round_percent(Proporcion, decimals = 2)) %>%
  arrange(desc(`Voto (%)`))

categorias_especiales_limpias <- c("No Sabe", "NS/NR", "Nulo", "No Responde", "En blanco", "En Blanco")

resultados_candidatos <- resultados_formateados %>%
  mutate(tipo = ifelse(Candidato %in% categorias_especiales_limpias, "Ninguna persona definida", "Persona candidata")) %>%
  mutate(Candidato = fct_reorder(Candidato, `Voto (%)`, .fun = sum, .desc = FALSE)) %>%
  mutate(Candidato = fct_relevel(Candidato, categorias_especiales_limpias))

# 9.1. GRÁFICO: VOTO PRESIDENCIAL
grafico_voto_presidencial <- ggplot(resultados_candidatos, aes(x = Candidato, y = `Voto (%)`)) +
  geom_col(aes(fill = tipo), width = 0.8) +
  geom_text(aes(label = paste0(`Voto (%)`, "%")), hjust = -0.1, size = 4, color = "black", fontface = "bold") +
  scale_fill_manual(values = c("Persona candidata" = "#1d1c49", "Ninguna persona definida" = "#D45A26")) +
  labs(title = "Distribución porcentual de personas entrevistadas por intención de voto presidencial, enero 2026", subtitle = "Base: Total de personas que votarán (Ponderado)", x = NULL, y = "Porcentaje (%)", fill = "Tipo de Voto") +
  coord_flip() +
  scale_y_continuous(limits = c(0, max(resultados_candidatos$`Voto (%)`) * 1.15)) +
  theme_minimal() +
  theme(legend.position = "bottom")


# 9.3. GRÁFICO: VOTO DIPUTADO
voto_diputado_df <- as.data.frame(diputado_resultado)
resultados_diputado <- voto_diputado_df %>%
  rownames_to_column(var = "Partido") %>% rename(Proporcion = mean) %>%
  mutate(Partido = gsub("^voto_diputado", "", Partido)) %>%
  mutate(`Voto (%)` = MESS::round_percent(Proporcion, decimals = 2)) %>%
  select(Partido, `Voto (%)`)

categorias_especiales_diputado <- c("Nulo", "En Blanco", "No Sabe", "No Responde", "NS/NR")
resultados_diputado <- resultados_diputado %>%
  mutate(tipo = ifelse(Partido %in% categorias_especiales_diputado, "Voto No Válido/Indeciso", "Intención Partidaria")) %>%
  mutate(Partido = fct_reorder(Partido, `Voto (%)`, .fun = sum, .desc = FALSE)) %>%
  mutate(Partido = fct_relevel(Partido, categorias_especiales_diputado))

grafico_voto_diputado <- ggplot(resultados_diputado, aes(x = Partido, y = `Voto (%)`)) +
  geom_col(aes(fill = tipo), width = 0.8) +
  geom_text(aes(label = paste0(`Voto (%)`, "%")), hjust = -0.1, size = 4, color = "black", fontface = "bold") +
  scale_fill_manual(values = c("Intención Partidaria" = "#1d1c49", "Voto No Válido/Indeciso" = "#D45A26")) +
  labs(title = "Distribución porcentual de intención de voto para diputaciones, enero 2026", subtitle = "Base: Total de personas que votarán (Ponderado)", x = NULL, y = "Porcentaje de Voto (%)", fill = "Clasificación") +
  coord_flip() +
  scale_y_continuous(limits = c(0, max(resultados_diputado$`Voto (%)`) * 1.15)) +
  theme_minimal() +
  theme(legend.position = "bottom")


# 9.4. GRÁFICO: VOTARÁ
votara_df <- as.data.frame(votara_resultado)
resultados_votara <- votara_df %>%
  rownames_to_column(var = "Respuesta") %>% rename(Proporcion = mean) %>%
  mutate(Respuesta = gsub("^votara", "", Respuesta)) %>%
  mutate(`Voto (%)` = MESS::round_percent(Proporcion, decimals = 2)) %>%
  select(Respuesta, `Voto (%)`)

resultados_votara <- resultados_votara %>%
  mutate(tipo = ifelse(Respuesta == "Sí", "Votará", "No Votará / No Responde")) %>%
  mutate(Respuesta = fct_relevel(Respuesta, "No Responde", "No", "Sí")) 

grafico_votara <- ggplot(resultados_votara, aes(x = Respuesta, y = `Voto (%)`)) +
  geom_col(aes(fill = tipo), width = 0.8) +
  geom_text(aes(label = paste0(`Voto (%)`, "%")), hjust = -0.1, size = 5, color = "black", fontface = "bold") +
  scale_fill_manual(values = c("Votará" = "#1d1c49", "No Votará / No Responde" = "#D45A26")) +
  labs(title = "Distribución porcentual de decididos a votar en próximas elecciones, enero 2026", subtitle = "Base: Total entrevistas Válidas (Ponderado)", x = NULL, y = "Porcentaje (%)", fill = NULL) +
  coord_flip() +
  scale_y_continuous(limits = c(0, max(resultados_votara$`Voto (%)`) * 1.1)) +
  theme_minimal() +
  theme(legend.position = "none")



# ==============================================================================
# GRÁFICO: DISTRIBUCIÓN PORCENTUAL DE ENTREVISTAS VÁLIDAS POR PROVINCIA Y SEXO
# ==============================================================================
formatear_provincia <- function(df) {
    df %>%
        mutate(
            Provincia = case_when(
                Provincia == "san-jose" ~ "San José",
                Provincia == "alajuela" ~ "Alajuela",
                Provincia == "cartago" ~ "Cartago",
                Provincia == "heredia" ~ "Heredia",
                Provincia == "guanacaste" ~ "Guanacaste",
                Provincia == "puntarenas" ~ "Puntarenas",
                Provincia == "limon" ~ "Limón",
                TRUE ~ Provincia
            )
        )
}
# 1. Preparación de los datos: Conteo y Cálculo de Porcentajes
distribucion_ponderada <- df_analisis_total %>%
    group_by(Provincia = provincia, Sexo = sexo) %>%
    # *** CAMBIO CRÍTICO: Usar sum(ponderador_final) en lugar de n() ***
    summarise(n_ponderado = sum(ponderador_final), .groups = 'drop') %>%
    # Calcular el porcentaje sobre el total de ponderadores (debe ser cercano a n_total)
    formatear_provincia() %>%
    mutate(Porcentaje = MESS::round_percent(n_ponderado / sum(n_ponderado), decimals = 2)) %>%
    # Ordenar la Provincia por el total del ponderador
    mutate(Provincia = fct_reorder(Provincia, n_ponderado, .fun=sum)) %>%
    # Asegurar que los niveles de Sexo sean legibles
    mutate(Sexo_Label = factor(Sexo, levels = c("M", "H"), labels = c("Mujeres", "Hombres")))
    
# 2. Generación del Gráfico
grafico_distribucion_muestra_sexo_provincia <- ggplot(distribucion_ponderada, 
                                                     aes(x = Provincia, y = Porcentaje, fill = Sexo_Label)) +
    
    # BARRAS: Usamos geom_col para barras de lado a lado (position = "dodge")
    geom_col(position = position_dodge(width = 0.8), width = 0.7) +
    
    # ETIQUETAS DE VALOR
    geom_text(aes(label = paste0(MESS::round_percent(Porcentaje, decimals = 2), "%")),
              position = position_dodge(width = 0.8), # Misma posición que las barras
              hjust = -0.1, size = 3.5, fontface = "bold") +
    
    # AJUSTES DE COLOR Y TÍTULOS
    scale_fill_manual(values = c("Hombres" = "#1d1c49", "Mujeres" = "#D45A26")) +
    labs(
        title = "Distribución porcentual de personas entrevistadas por provincia y sexo, enero 2026",
        subtitle = "Base: Total de entrevistas válidas (Ponderado)",
        x = NULL,
        y = "Porcentaje sobre la Muestra Total (%)",
        fill = "Sexo"
    ) +
    
    # VOLTEAR COORDENADAS (Mejor visualización para provincias)
    coord_flip() +
    
    # AJUSTE DEL EJE X (para hacer espacio a las etiquetas)
    scale_y_continuous(limits = c(0, max(distribucion_ponderada$Porcentaje) * 1.15)) +
    
    # TEMA
    theme_minimal() +
    theme(legend.position = "bottom")

# ==============================================================================
# GRÁFICO: DISTRIBUCIÓN PORCENTUAL PONDERADA POR PROVINCIA
# ==============================================================================

# 1. Preparación de los datos: Filtrar y formatear la tabla_final_distribucion
# Usamos los datos de la tabla generada en la Sección 6, pero solo los totales por provincia
# Para evitar duplicados, usaremos la tabla calculada en la sección 6, sumando por provincia.
distribucion_ponderada_provincia <- tabla_final_distribucion %>%
  filter(Sexo != "TOTAL") %>% # Excluir la fila de TOTAL nacional
  group_by(Provincia) %>%
  summarise(
    `% Muestra Ponderada` = sum(`% Muestra Ponderada`, na.rm = TRUE),
    .groups = 'drop'
  ) %>%
  formatear_provincia() %>%
  # Reordenar la Provincia por el porcentaje (de menor a mayor para coord_flip)
  mutate(Provincia = fct_reorder(Provincia, `% Muestra Ponderada`, .fun=sum, .desc = FALSE))

# 2. Generación del Gráfico
grafico_distribucion_ponderada_provincia <- ggplot(distribucion_ponderada_provincia, 
                                                     aes(x = Provincia, y = `% Muestra Ponderada`)) +
    
    # BARRAS: Barras de color uniforme
    geom_col(fill = "#1d1c49", width = 0.7) +
    
    # ETIQUETAS DE VALOR
    geom_text(aes(label = paste0(round(`% Muestra Ponderada`, 1), "%")),
              hjust = -0.1, # Ajuste para que quede a la derecha de la barra
              size = 4, 
              fontface = "bold") +
    
    # AJUSTES DE TÍTULOS
    labs(
        title = "Distribución Porcentual Ponderada por Provincia",
        subtitle = "Ajuste de la muestra al Padrón Electoral",
        x = NULL,
        y = "Porcentaje sobre la Muestra Total Ponderada (%)"
    ) +
    
    # VOLTEAR COORDENADAS
    coord_flip() +
    
    # AJUSTE DEL EJE Y (para hacer espacio a las etiquetas)
    scale_y_continuous(limits = c(0, max(distribucion_ponderada_provincia$`% Muestra Ponderada`) * 1.15)) +
    
    # TEMA
    theme_minimal() 

# ==============================================================================
# GRÁFICO: % Y NÚMERO BRUTO DE ENTREVISTAS VÁLIDAS POR PROVINCIA
# ==============================================================================

# 1. Preparación de los datos: Calcular % y N bruto por provincia
# Usamos df_analisis_total (Base total de encuestas válidas)
distribucion_bruta_provincia <- df_analisis_total %>%
    group_by(Provincia = provincia) %>%
    summarise(
        # Número de entrevistas (n) BRUTO
        N_Bruto = n(),
        .groups = 'drop'
    ) %>%
    formatear_provincia() %>%
    # Calcular el porcentaje sobre el total bruto
    mutate(
        Total_Bruto = sum(N_Bruto),
        `% Muestra Bruta` = MESS::round_percent(N_Bruto / Total_Bruto, decimals = 2)
    ) %>%
    # Formatear la etiqueta para el gráfico
    mutate(
        Etiqueta_Final = MESS::round_percent(`% Muestra Bruta`, decimals = 2)
    ) %>%
    # Reordenar para el gráfico
    mutate(Provincia = fct_reorder(Provincia, `% Muestra Bruta`, .fun=sum, .desc = FALSE))


# 2. Generación del Gráfico
grafico_distribucion_bruta_provincia <- ggplot(distribucion_bruta_provincia, 
                                                     aes(x = Provincia, y = `% Muestra Bruta`)) +
    
    # BARRAS: Barras de color uniforme
    geom_col(fill = "#D45A26", width = 0.7) +
    
    # ETIQUETAS DE VALOR (Incluye el N bruto)
    geom_text(aes(label = Etiqueta_Final),
              hjust = -0.05, # Ajuste para que quede a la derecha de la barra
              size = 4, 
              fontface = "bold") +
    
    # AJUSTES DE TÍTULOS
    labs(
        title = "Distribución Porcentual y Número de Entrevistas BRUTAS por Provincia",
        subtitle = "Base: Total de Entrevistas Válidas (SIN PONDERAR)",
        x = NULL,
        y = "Porcentaje Bruto de la Muestra Total (%)"
    ) +
    
    # VOLTEAR COORDENADAS
    coord_flip() +
    
    # AJUSTE DEL EJE Y (para hacer espacio a las etiquetas)
    scale_y_continuous(limits = c(0, max(distribucion_bruta_provincia$`% Muestra Bruta`) * 1.2)) +
    
    # TEMA
    theme_minimal() 

# ==============================================================================
# UNIFICACIÓN DE GRÁFICOS: DISTRIBUCIÓN POR PROVINCIA (BRUTA Y PONDERADA)
# ==============================================================================

# 1. Recalcular y/o asegurar que los data frames y gráficos existen:
# --- 1.1. Gráfico BRUTO (sin ponderar) ---
distribucion_bruta_provincia <- df_analisis_total %>%
    group_by(Provincia = provincia) %>%
    summarise(
        N_Bruto = n(),
        .groups = 'drop'
    ) %>%
    formatear_provincia() %>%
    mutate(
        Total_Bruto = sum(N_Bruto),
        `% Muestra` = (N_Bruto / Total_Bruto) * 100,
        Tipo_Distribucion = "1. Muestra Bruta (SIN Ponderar)"
    ) %>%
    mutate(
        Etiqueta_Final = MESS::round_percent(`% Muestra`, decimals = 2)
    ) %>%
    mutate(Provincia = fct_reorder(Provincia, `% Muestra`, .fun=sum, .desc = FALSE))

grafico_distribucion_bruta_provincia <- ggplot(distribucion_bruta_provincia, 
                                               aes(x = Provincia, y = `% Muestra`)) +
    geom_col(fill = "#D45A26", width = 0.7) +
    # Ajuste 1: Aumentar la separación con hjust
    geom_text(aes(label = Etiqueta_Final), hjust = -0.2, size = 3.5, fontface = "bold") +
    labs(title = "Muestra Bruta (SIN PONDERAR)", x = NULL, y = "Porcentaje Bruto (%)") +
    coord_flip() +
    # Ajuste 2: Aumentar el límite del eje Y a * 1.4
    scale_y_continuous(limits = c(0, max(distribucion_bruta_provincia$`% Muestra`) * 1.4)) +
    theme_minimal() 

# --- 1.2. Gráfico PONDERADO ---
distribucion_ponderada_provincia_final <- df_analisis_total %>%
    group_by(Provincia = provincia) %>%
    summarise(
        N_Ponderado = sum(ponderador_final, na.rm = TRUE),
        .groups = 'drop'
    ) %>%
    formatear_provincia() %>%
    mutate(
        Total_Ponderado = sum(N_Ponderado),
        `% Muestra` = MESS::round_percent(N_Ponderado / Total_Ponderado, decimals = 2),
        Tipo_Distribucion = "2. Muestra Ponderada (AJUSTADA)"
    ) %>%
    mutate(
        # CAMBIO REALIZADO AQUÍ: Solo muestra el porcentaje
        Etiqueta_Final = paste0(MESS::round_percent(`% Muestra`, decimals = 2), "%")
    ) %>%
    mutate(Provincia = fct_reorder(Provincia, `% Muestra`, .fun=sum, .desc = FALSE))

grafico_distribucion_ponderada_provincia_completo <- ggplot(distribucion_ponderada_provincia_final, 
                                                     aes(x = Provincia, y = `% Muestra`)) +
    geom_col(fill = "#1d1c49", width = 0.7) +
    # Ajuste de etiqueta (se mantiene hjust=-0.2 y size=3.5 para el espacio)
    geom_text(aes(label = Etiqueta_Final), hjust = -0.2, size = 3.5, fontface = "bold") + 
    labs(title = "Muestra Ponderada (AJUSTADA)", x = NULL, y = "Porcentaje Ponderado (%)") +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(distribucion_ponderada_provincia_final$`% Muestra`) * 1.4)) +
    theme_minimal() 


# 2. UNIFICAR LOS GRÁFICOS usando grid.arrange
grid.arrange(
    grafico_distribucion_bruta_provincia,
    grafico_distribucion_ponderada_provincia_completo,
    ncol = 2,
    top = textGrob("Comparación de Distribución Muestral por Provincia (Bruta vs. Ponderada)",
                   gp = gpar(fontsize = 14, fontface = "bold"))
)

# ==============================================================================
# GENERACIÓN DE GRÁFICO: VOTO VÁLIDO A PRESIDENTE (PONDERADO)
# ==============================================================================

library(ggplot2)
library(dplyr)
library(forcats)
library(survey)
library(tibble)

# Variables de limpieza
categorias_no_validas <- c("No Responde", "Nulo", "En Blanco", "No Sabe", "NS/NR") 
# La base de diseño 'encuesta_dsn' ya está definida para Votantes Válidos (votara == 'Sí')

# 1. Calcular la media ponderada de voto_presidente
resultado_nacional <- svymean(~voto_presidente, design = encuesta_dsn, na.rm = TRUE)

# 2. Formatear y recalcular sobre Votos Válidos
df_resultado <- as.data.frame(resultado_nacional) %>%
  rownames_to_column(var = "Partido_raw") %>%
  rename(Proporcion = mean) %>%
  mutate(Partido = gsub("^voto_presidente", "", Partido_raw)) %>%
  filter(!is.na(Proporcion)) %>%
  mutate(es_valido = !Partido %in% categorias_no_validas) %>%
  
  # Recalculo sobre Votos Válidos
  mutate(Suma_Proporcion_Valida = sum(Proporcion[es_valido])) %>%
  mutate(
    `Voto (%)` = if_else(es_valido, MESS::round_percent(Proporcion / Suma_Proporcion_Valida, decimals = 2), 0.00)
  ) %>%
  filter(es_valido) %>% # Solo mantener los votos válidos
  mutate(`Voto (%)` = MESS::round_percent(`Voto (%)`, decimals = 2))

# 3. Preparar para el gráfico
df_partidos <- df_resultado %>%
  # Eliminar filas con 0% de voto válido
  filter(`Voto (%)` > 0) %>%
  # Ordenar por porcentaje de voto válido
  mutate(Partido = fct_reorder(Partido, `Voto (%)`, .fun = sum, .desc = FALSE))

# 4. Crear el gráfico
grafico_presidente_valido <- ggplot(df_partidos, aes(x = Partido, y = `Voto (%)`)) +
  geom_col(fill = "#1d1c49", width = 0.8) +
  geom_text(aes(label = paste0(`Voto (%)`, "%")), 
            hjust = -0.1, size = 4.0, color = "black", fontface = "bold") +
  labs(
    title = "Distribución porcentual de personas entrevistadas por Intención de Voto Válido a presidencia, enero 2026",
    subtitle = "Base: Votantes Válidos a Nivel Nacional (Excluye Nulos/Blancos/NS/NR - Ponderado)",
    x = NULL,
    y = "Porcentaje de Voto Válido (%)"
  ) +
  coord_flip() +
  scale_y_continuous(limits = c(0, max(df_partidos$`Voto (%)`) * 1.15)) +
  theme_minimal() +
  theme(legend.position = "none")


# ==============================================================================
# GENERACIÓN DE GRÁFICO: ESCALA DE DECIDIDOS A VOTAR (PONDERADO) - FINAL
# ==============================================================================

# Variables de limpieza
categorias_no_validas <- c("No Responde", "Nulo", "En Blanco", "No Sabe", "NS/NR") 
# La base de diseño 'encuesta_dsn' ya está definida para Votantes Válidos (votara == 'Sí')

# 1. Calcular la media ponderada de escala_voto
resultado_nacional <- svymean(~escala_voto, design = encuesta_dsn, na.rm = TRUE)

# 2. Formatear, Renombrar y Recalcular
df_resultado <- as.data.frame(resultado_nacional) %>%
    # 🚨 CORRECCIÓN: Usamos 'Escala_raw' y 'Escala_Nivel' para evitar confusión con 'Partido'
    rownames_to_column(var = "Escala_raw") %>%
    rename(Proporcion = mean) %>%
    
    # Extraer el valor numérico de la escala (1, 2, 3, 4, 5)
    mutate(Escala_Nivel = gsub("^escala_voto", "", Escala_raw)) %>%
    filter(!is.na(Proporcion)) %>%
    mutate(es_valido = !Escala_Nivel %in% categorias_no_validas) %>%
    
    # Recalculo sobre Votos Válidos
    mutate(Suma_Proporcion_Valida = sum(Proporcion[es_valido])) %>%
    mutate(
        `Voto (%)` = if_else(es_valido, (Proporcion / Suma_Proporcion_Valida) * 100, 0.00)
    ) %>%
    filter(es_valido) %>% # Solo mantener los votos válidos
    mutate(`Voto (%)` = MESS::round_percent(`Voto (%)`, decimals = 2))

# 3. Preparar para el gráfico (ORDEN FIJO DE LA ESCALA)
df_escala <- df_resultado %>%
    # Eliminar filas con 0% de voto válido
    filter(`Voto (%)` > 0) %>%
    
    # 🚨 CORRECCIÓN: IMPONER ORDEN MANUAL DE LA ESCALA (5 a 1)
    # En un gráfico volteado (coord_flip), el orden del factor (levels) debe ser del 1 al 5
    # para que el nivel "5" aparezca arriba y el "1" abajo.
    mutate(Escala_Nivel = factor(Escala_Nivel, levels = c("1", "2", "3", "4", "5")))


# 4. Crear el gráfico
grafico_escala_voto <- ggplot(df_escala, aes(x = Escala_Nivel, y = `Voto (%)`)) +
    # Usamos COLOR_PRINCIPAL definido en el archivo graficos.r
    geom_col(fill = "#1d1c49", width = 0.8) +
    geom_text(aes(label = paste0(`Voto (%)`, "%")), 
              hjust = -0.1, size = 4.0, color = "black", fontface = "bold") +
    labs(
        title = "Distribución porcentual de entrevistas por escala de decididos a votar, enero 2026",
        subtitle = "Base: Votantes Válidos a Nivel Nacional (Excluye NS/NR - Ponderado)",
        x = NULL,
        y = "Porcentaje de Voto Válido (%)"
    ) +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(df_escala$`Voto (%)`) * 1.15)) +
    theme_minimal() +
    theme(legend.position = "none")
    
print(grafico_escala_voto)

# --- EXPORTACIÓN (Si DIR_GRAFICOS existe) ---
if (exists("DIR_GRAFICOS")) {
    ggsave(
        filename = file.path(DIR_GRAFICOS, "Escala_Voto_Decididos.png"), 
        plot = grafico_escala_voto,
        width = 8, 
        height = 6, 
        units = "in"
    )
}

# ==============================================================================
# GENERACIÓN DE GRÁFICO: ESCALA DE SEGURIDAD DE ELECCIÓN PRESIDENCIAL (PONDERADO) - FINAL
# ==============================================================================

# Variables de limpieza
categorias_no_validas <- c("No Responde", "Nulo", "En Blanco", "No Sabe", "NS/NR") 
# La base de diseño 'encuesta_dsn' ya está definida para Votantes Válidos (votara == 'Sí')

# 1. Calcular la media ponderada de presidente_escala
resultado_nacional_escala <- svymean(~presidente_escala, design = encuesta_dsn_presidente_escala, na.rm = TRUE)

# 2. Formatear, Renombrar y Recalcular
df_resultado <- as.data.frame(resultado_nacional_escala) %>%
    # 🚨 CORRECCIÓN: Usamos 'Escala_raw' y 'Escala_Nivel' para evitar confusión con 'Partido'
    rownames_to_column(var = "Escala_raw") %>%
    rename(Proporcion = mean) %>%
    
    # Extraer el valor numérico de la escala (1, 2, 3, 4, 5)
    mutate(Escala_Nivel = gsub("^presidente_escala", "", Escala_raw)) %>%
    filter(!is.na(Proporcion)) %>%
    mutate(es_valido = !Escala_Nivel %in% categorias_no_validas) %>%
    
    # Recalculo sobre Votos Válidos
    mutate(Suma_Proporcion_Valida = sum(Proporcion[es_valido])) %>%
    mutate(
        `Voto (%)` = if_else(es_valido, (Proporcion / Suma_Proporcion_Valida) * 100, 0.00)
    ) %>%
    filter(es_valido) %>% # Solo mantener los votos válidos
    mutate(`Voto (%)` = MESS::round_percent(`Voto (%)`, decimals = 2))

# 3. Preparar para el gráfico (ORDEN FIJO DE LA ESCALA)
df_escala <- df_resultado %>%
    # Eliminar filas con 0% de voto válido
    filter(`Voto (%)` > 0) %>%
    
    # 🚨 CORRECCIÓN: IMPONER ORDEN MANUAL DE LA ESCALA (5 a 1)
    # En un gráfico volteado (coord_flip), el orden del factor (levels) debe ser del 1 al 5
    # para que el nivel "5" aparezca arriba y el "1" abajo.
    mutate(Escala_Nivel = factor(Escala_Nivel, levels = c("1", "2", "3", "4", "5")))


# 4. Crear el gráfico
grafico_escala_presidente <- ggplot(df_escala, aes(x = Escala_Nivel, y = `Voto (%)`)) +
    # Usamos COLOR_PRINCIPAL definido en el archivo graficos.r
    geom_col(fill = "#1d1c49", width = 0.8) +
    geom_text(aes(label = paste0(`Voto (%)`, "%")), 
              hjust = -0.1, size = 4.0, color = "black", fontface = "bold") +
    labs(
        title = "Distribución porcentual por escala de seguridad de opción presidencial, enero 2026",
        subtitle = "Base: Votantes Válidos a Nivel Nacional (Excluye NS/NR - Ponderado)",
        x = NULL,
        y = "Porcentaje de Voto Válido (%)"
    ) +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(df_escala$`Voto (%)`) * 1.15)) +
    theme_minimal() +
    theme(legend.position = "none")
    
print(grafico_escala_presidente)

# --- EXPORTACIÓN (Si DIR_GRAFICOS existe) ---
if (exists("DIR_GRAFICOS")) {
    ggsave(
        filename = file.path(DIR_GRAFICOS, "Escala_Voto_Decididos_presidente.png"), 
        plot = grafico_escala_presidente,
        width = 8, 
        height = 6, 
        units = "in"
    )
}
# Imprimir el gráfico
cat("\n✅ Todos los objetos de gráficos (grafico_voto_mejorado, grafico_religion, etc.) han sido generados y almacenados en el ambiente de R. Puedes imprimirlos o guardarlos manualmente.\n")

  CARPETA_EXPORTACION <- "C:/Users/vanev/Documents/Opol/Opol IX EEN - ENE26/Graficos/"
  
  # Nombre del archivo (ej: voto_diputados_san-jose.png)
  ruta_completa_archivo <- paste0(CARPETA_EXPORTACION, "Escala_Voto_Decididos_presidente.png")
  grafico <- grafico_escala_voto
  
  # 7.2. Guardar el gráfico
  ggsave(
      filename = ruta_completa_archivo,
      plot = grafico,
      width = 12,
      height = 6,
      units = "in",
      dpi = 300
  )

  # Nombre del archivo (ej: voto_diputados_san-jose.png)
  ruta_completa_archivo <- paste0(CARPETA_EXPORTACION, "grafico_distribucion_muestra_sexo_provincia.png")
  grafico <- grafico_distribucion_muestra_sexo_provincia
  
  # 7.2. Guardar el gráfico
  ggsave(
      filename = ruta_completa_archivo,
      plot = grafico,
      width = 12,
      height = 6,
      units = "in",
      dpi = 300
  )

  # Nombre del archivo (ej: voto_diputados_san-jose.png)
  ruta_completa_archivo <- paste0(CARPETA_EXPORTACION, "grafico_votara.png")
  grafico <- grafico_votara
  # 7.2. Guardar el gráfico
  ggsave(
      filename = ruta_completa_archivo,
      plot = grafico,
      width = 12,
      height = 6,
      units = "in",
      dpi = 300
  )
  # Nombre del archivo (ej: voto_diputados_san-jose.png)
  ruta_completa_archivo <- paste0(CARPETA_EXPORTACION, "grafico_voto_presidencial.png")
  grafico <- grafico_voto_presidencial
  # 7.2. Guardar el gráfico
  ggsave(
      filename = ruta_completa_archivo,
      plot = grafico,
      width = 12,
      height = 6,
      units = "in",
      dpi = 300
  )
  # Nombre del archivo (ej: voto_diputados_san-jose.png)
  ruta_completa_archivo <- paste0(CARPETA_EXPORTACION, "grafico_presidente_valido.png")
  grafico <- grafico_presidente_valido
  # 7.2. Guardar el gráfico
  ggsave(
      filename = ruta_completa_archivo,
      plot = grafico,
      width = 12,
      height = 6,
      units = "in",
      dpi = 300
  )
  
  # Nombre del archivo (ej: voto_diputados_san-jose.png)
  ruta_completa_archivo <- paste0(CARPETA_EXPORTACION, "grafico_voto_diputado.png")
  grafico <- grafico_voto_diputado
  # 7.2. Guardar el gráfico
  ggsave(
      filename = ruta_completa_archivo,
      plot = grafico,
      width = 12,
      height = 6,
      units = "in",
      dpi = 300
  )

# -----------------------------------------------------------------------------

# ==============================================================================
# GENERACIÓN INDIVIDUAL DE 7 GRÁFICOS: VOTO A DIPUTADOS POR PROVINCIA (COMPLETO)
# ==============================================================================

# Variables definidas en el script anterior
# encuesta_dsn (Diseño de muestreo ponderado para Votantes Válidos)
categorias_no_partidarias <- c("No Responde", "Nulo", "En Blanco", "No Sabe", "NS/NR") 
provincias <- c("san-jose", "alajuela", "cartago", "heredia", "guanacaste", "puntarenas", "limon")

# Función auxiliar para formatear los nombres de provincia (incluye tildes)
formatear_nombre_provincia <- function(p_raw) {
    p_formatted <- case_when(
        p_raw == "san-jose" ~ "San José",
        p_raw == "alajuela" ~ "Alajuela",
        p_raw == "cartago" ~ "Cartago",
        p_raw == "heredia" ~ "Heredia",
        p_raw == "guanacaste" ~ "Guanacaste",
        p_raw == "puntarenas" ~ "Puntarenas",
        p_raw == "limon" ~ "Limón",
        TRUE ~ tools::toTitleCase(p_raw)
    )
    return(p_formatted)
}

# --- INICIO DEL BUCLE DE PROCESAMIENTO ---
for (p in provincias) {
  # 1. Filtrar el diseño de encuesta para la provincia actual
    dsn_provincia <- subset(encuesta_dsn, provincia == p)
    
    # *** CORRECCIÓN: Calcular el N de la provincia directamente ***
    # NROW cuenta el número de filas (encuestas) en el dataframe asociado al diseño.
    n_provincia_actual <- NROW(dsn_provincia$variables) 
    
    # 2. Calcular la media ponderada (proporción) de voto_diputado
    resultado_provincia <- svymean(~voto_diputado, design = dsn_provincia, na.rm = TRUE)

    
    # 3. Formatear los resultados (usando la Proporción Total)
    df_resultado <- as.data.frame(resultado_provincia) %>%
        rownames_to_column(var = "Partido_raw") %>%
        rename(Proporcion = mean) %>%
        mutate(Partido = gsub("^voto_diputado", "", Partido_raw)) %>%
        filter(!is.na(Proporcion)) %>%
        
        # Calcular el Voto (%) sobre el TOTAL (Proporción * 100)
        mutate(`Voto (%)` = MESS::round_percent(Proporcion, decimals = 2))
        
# 4. Clasificar y resumir para IMPRESIÓN DE DATOS
    df_resumen <- df_resultado %>%
        # Definir la categoría de voto
        mutate(
            tipo = ifelse(Partido %in% categorias_no_partidarias, "No Válido/Indeciso", "Voto Válido")
        ) %>%
        # Sumar los porcentajes por tipo de voto
        group_by(tipo) %>%
        summarise(
            `Total %` = sum(`Voto (%)`, na.rm = TRUE),
            .groups = 'drop'
        )
    
    # --- IMPRESIÓN DE DATOS SOLICITADOS EN CONSOLA ---
    nombre_provincia <- formatear_nombre_provincia(p)
    
    cat("\n========================================================================\n")
    cat(paste("🗳️  RESUMEN DE VOTO A DIPUTADOS:", toupper(nombre_provincia)), "\n")
    cat(paste("Base: Votantes Válidos Ponderados (n =", unique(df_resumen$n_provincia), ")\n"))
    cat("------------------------------------------------------------------------\n")
    
    voto_valido <- df_resumen %>% filter(tipo == "Voto Válido") %>% pull(`Total %`)
    voto_no_valido <- df_resumen %>% filter(tipo == "No Válido/Indeciso") %>% pull(`Total %`)
    
    cat(sprintf("  Porcentaje Voto VÁLIDO (Partidario): %.2f %%\n", voto_valido))
    cat(sprintf("  Porcentaje Voto NO VÁLIDO (Indeciso/Nulo/Blanco): %.2f %%\n", voto_no_valido))
    cat("========================================================================\n\n")

    
    # 5. Clasificar y ordenar para el gráfico
    df_candidatos <- df_resultado %>%
        filter(`Voto (%)` > 0) %>% # Eliminar menciones de 0%
        mutate(
            tipo = ifelse(Partido %in% categorias_no_partidarias, "Voto No Partidario/Indeciso", "Intención Partidaria")
        ) %>%
        # Ordenar los partidos por porcentaje (de menor a mayor para coord_flip)
        mutate(Partido = fct_reorder(Partido, `Voto (%)`, .fun = sum, .desc = FALSE)) %>%
        # Asegurar que las categorías no partidarias se muestren al final (arriba en coord_flip)
        mutate(Partido = fct_relevel(Partido, categorias_no_partidarias))
    
    
    # 6. Crear el gráfico
    grafico <- ggplot(df_candidatos, aes(x = Partido, y = `Voto (%)`)) +
        geom_col(aes(fill = tipo), width = 0.8) +
        geom_text(aes(label = paste0(`Voto (%)`, "%")), 
                  hjust = -0.1, size = 3.5, color = "black", fontface = "bold") +
        scale_fill_manual(values = c("Intención Partidaria" = "#1d1c49", "Voto No Partidario/Indeciso" = "#D45A26")) +
        labs(
            title = paste("Distribución porcentual por voto válido a diputaciones -", nombre_provincia),
            subtitle = paste0("Base: Votantes Válidos en ", nombre_provincia, " (Ponderado sobre el Total de Votantes)"),
            x = NULL,
            y = "Porcentaje sobre el Total de Votantes (%)",
            fill = "" # Elimina el título de la leyenda
        ) +
        coord_flip() +
        scale_y_continuous(limits = c(0, max(df_candidatos$`Voto (%)`) * 1.15)) +
        theme_minimal() +
        theme(legend.position = "bottom", legend.title = element_blank())
    
    # 7. Imprimir el gráfico individualmente
    print(grafico)
      # Define la carpeta de exportación (Asegúrate de que exista o créala antes)
  CARPETA_EXPORTACION <- "C:/Users/vanev/Documents/Opol/Opol IX EEN - ENE26/Graficos/Provincias/"
  
  # Nombre del archivo (ej: voto_diputados_san-jose.png)
  nombre_archivo <- paste0("voto_diputados_total_", p, ".png")
  ruta_completa_archivo <- paste0(CARPETA_EXPORTACION, nombre_archivo)
  
  # 7.2. Guardar el gráfico
  ggsave(
      filename = ruta_completa_archivo,
      plot = grafico,
      width = 12,
      height = 6,
      units = "in",
      dpi = 300
  )
  
  cat(paste0("✅ Gráfico guardado: ", ruta_completa_archivo, "\n"))
}

# ==============================================================================
# GENERACIÓN INDIVIDUAL DE 7 GRÁFICOS: VOTO VÁLIDO A DIPUTADOS POR PROVINCIA 
# ==============================================================================


# Variables definidas en el script anterior
# encuesta_dsn (Diseño de muestreo ponderado para Votantes Válidos)
categorias_no_validas <- c("No Responde", "Nulo", "En blanco", "No Sabe", "NS/NR", "En Blanco") 
provincias <- c("san-jose", "alajuela", "cartago", "heredia", "guanacaste", "puntarenas", "limon")

for (p in provincias) {
  # 1. Filtrar el diseño de encuesta para la provincia actual
  dsn_provincia <- subset(encuesta_dsn, provincia == p)
  
  # 2. Calcular la media ponderada de voto_diputado
  resultado_provincia <- svymean(~voto_diputado, design = dsn_provincia, na.rm = TRUE)
  
  # 3. Formatear y recalcular sobre Votos Válidos
  df_resultado <- as.data.frame(resultado_provincia) %>%
    rownames_to_column(var = "Partido_raw") %>%
    rename(Proporcion = mean) %>%
    mutate(Partido = gsub("^voto_diputado", "", Partido_raw)) %>%
    filter(!is.na(Proporcion)) %>%
    mutate(es_valido = !Partido %in% categorias_no_validas) %>%
    
    # Recalculo sobre Votos Válidos (Suma de las proporciones válidas)
    mutate(Suma_Proporcion_Valida = sum(Proporcion[es_valido])) %>%
    mutate(
      `Voto (%)` = if_else(es_valido, (Proporcion / Suma_Proporcion_Valida) * 100, 0.00)
    ) %>%
    filter(es_valido) %>% # Solo mantener los votos válidos
    mutate(`Voto (%)` = MESS::round_percent(`Voto (%)`, decimals = 2))
  
  # 4. Preparar para el gráfico
  df_candidatos <- df_resultado %>%
    # Eliminar filas con 0% de voto válido (que no tendrían mención real)
    filter(`Voto (%)` > 0) %>%
    # Ordenar por porcentaje de voto válido
    mutate(Partido = fct_reorder(Partido, `Voto (%)`, .fun = sum, .desc = FALSE))

  # 5. Crear el gráfico
  grafico <- ggplot(df_candidatos, aes(x = Partido, y = `Voto (%)`)) +
    geom_col(fill = "#1d1c49", width = 0.8) +
    geom_text(aes(label = paste0(`Voto (%)`, "%")), 
              hjust = -0.1, size = 3.5, color = "black", fontface = "bold") +
    labs(
      title = paste("Distribución porcentual por voto válido a diputaciones -", toupper(p)),
      subtitle = paste0("Base: Votantes Válidos en ", tools::toTitleCase(p), " (Ponderado)"),
      x = NULL,
      y = "Porcentaje de Voto Válido (%)"
    ) +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(df_candidatos$`Voto (%)`) * 1.15)) +
    theme_minimal() +
    theme(legend.position = "none")

  # 6. Imprimir el gráfico individualmente
  print(grafico)
  # Define la carpeta de exportación (Asegúrate de que exista o créala antes)
  CARPETA_EXPORTACION <- "C:/Users/vanev/Documents/Opol/Opol IX EEN - ENE26/Graficos/Provincias/"
  
  # Nombre del archivo (ej: voto_diputados_san-jose.png)
  nombre_archivo <- paste0("voto_diputados_voto_valido_", p, ".png")
  ruta_completa_archivo <- paste0(CARPETA_EXPORTACION, nombre_archivo)
  
  # 7.2. Guardar el gráfico
  ggsave(
      filename = ruta_completa_archivo,
      plot = grafico,
      width = 12,
      height = 6,
      units = "in",
      dpi = 300
  )
  
  cat(paste0("✅ Gráfico guardado: ", ruta_completa_archivo, "\n"))
}


# ==============================================================================
# GENERACIÓN INDIVIDUAL DE 7 GRÁFICOS: VOTO A PRESIDENTE POR PROVINCIA (COMPLETO)
# ==============================================================================

# Variables definidas en el script anterior
# encuesta_dsn (Diseño de muestreo ponderado para Votantes Válidos)
categorias_no_partidarias <- c("No Responde", "Nulo", "En Blanco", "No Sabe", "NS/NR") 
provincias <- c("san-jose", "alajuela", "cartago", "heredia", "guanacaste", "puntarenas", "limon")

# Función auxiliar para formatear los nombres de provincia (incluye tildes)
formatear_nombre_provincia <- function(p_raw) {
    p_formatted <- case_when(
        p_raw == "san-jose" ~ "San José",
        p_raw == "alajuela" ~ "Alajuela",
        p_raw == "cartago" ~ "Cartago",
        p_raw == "heredia" ~ "Heredia",
        p_raw == "guanacaste" ~ "Guanacaste",
        p_raw == "puntarenas" ~ "Puntarenas",
        p_raw == "limon" ~ "Limón",
        TRUE ~ tools::toTitleCase(p_raw)
    )
    return(p_formatted)
}

# --- INICIO DEL BUCLE DE PROCESAMIENTO ---
for (p in provincias) {
  # 1. Filtrar el diseño de encuesta para la provincia actual
    dsn_provincia <- subset(encuesta_dsn, provincia == p)
    
    # *** CORRECCIÓN: Calcular el N de la provincia directamente ***
    # NROW cuenta el número de filas (encuestas) en el dataframe asociado al diseño.
    n_provincia_actual <- NROW(dsn_provincia$variables) 
    
    # 2. Calcular la media ponderada (proporción) de voto_presidente
    resultado_provincia <- svymean(~voto_presidente, design = dsn_provincia, na.rm = TRUE)

    
    # 3. Formatear los resultados (usando la Proporción Total)
    df_resultado <- as.data.frame(resultado_provincia) %>%
        rownames_to_column(var = "Partido_raw") %>%
        rename(Proporcion = mean) %>%
        mutate(Partido = gsub("^voto_presidente", "", Partido_raw)) %>%
        filter(!is.na(Proporcion)) %>%
        
        # Calcular el Voto (%) sobre el TOTAL (Proporción * 100)
        mutate(`Voto (%)` = MESS::round_percent(Proporcion, decimals = 2))
        
# 4. Clasificar y resumir para IMPRESIÓN DE DATOS
    df_resumen <- df_resultado %>%
        # Definir la categoría de voto
        mutate(
            tipo = ifelse(Partido %in% categorias_no_partidarias, "No Válido/Indeciso", "Voto Válido")
        ) %>%
        # Sumar los porcentajes por tipo de voto
        group_by(tipo) %>%
        summarise(
            `Total %` = sum(`Voto (%)`, na.rm = TRUE),
            .groups = 'drop'
        )
    
    # --- IMPRESIÓN DE DATOS SOLICITADOS EN CONSOLA ---
    nombre_provincia <- formatear_nombre_provincia(p)
    
    cat("\n========================================================================\n")
    cat(paste("🗳️  RESUMEN DE VOTO A PRESIDENTE:", toupper(nombre_provincia)), "\n")
    cat(paste("Base: Votantes Válidos Ponderados (n =", unique(df_resumen$n_provincia), ")\n"))
    cat("------------------------------------------------------------------------\n")
    
    voto_valido <- df_resumen %>% filter(tipo == "Voto Válido") %>% pull(`Total %`)
    voto_no_valido <- df_resumen %>% filter(tipo == "No Válido/Indeciso") %>% pull(`Total %`)
    
    cat(sprintf("  Porcentaje Voto VÁLIDO (Partidario): %.2f %%\n", voto_valido))
    cat(sprintf("  Porcentaje Voto NO VÁLIDO (Indeciso/Nulo/Blanco): %.2f %%\n", voto_no_valido))
    cat("========================================================================\n\n")

    
    # 5. Clasificar y ordenar para el gráfico
    df_candidatos <- df_resultado %>%
        filter(`Voto (%)` > 0) %>% # Eliminar menciones de 0%
        mutate(
            tipo = ifelse(Partido %in% categorias_no_partidarias, "Indeciso/Sin preferencia", "Intención Partidaria")
        ) %>%
        # Ordenar los partidos por porcentaje (de menor a mayor para coord_flip)
        mutate(Partido = fct_reorder(Partido, `Voto (%)`, .fun = sum, .desc = FALSE)) %>%
        # Asegurar que las categorías no partidarias se muestren al final (arriba en coord_flip)
        mutate(Partido = fct_relevel(Partido, categorias_no_partidarias))
    
    
    # 6. Crear el gráfico
    grafico <- ggplot(df_candidatos, aes(x = Partido, y = `Voto (%)`)) +
        geom_col(aes(fill = tipo), width = 0.8) +
        geom_text(aes(label = paste0(`Voto (%)`, "%")), 
                  hjust = -0.1, size = 3.5, color = "black", fontface = "bold") +
        scale_fill_manual(values = c("Intención Partidaria" = "#1d1c49", "Indeciso/Sin preferencia" = "#D45A26")) +
        labs(
            title = paste("Distribución porcentual por voto a presidencia -", nombre_provincia),
            subtitle = paste0("Base: Votantes en ", nombre_provincia, " (Ponderado sobre el Total de Votantes)"),
            x = NULL,
            y = "Porcentaje sobre el Total de Votantes (%)",
            fill = "" # Elimina el título de la leyenda
        ) +
        coord_flip() +
        scale_y_continuous(limits = c(0, max(df_candidatos$`Voto (%)`) * 1.15)) +
        theme_minimal() +
        theme(legend.position = "bottom", legend.title = element_blank())
    
    # 7. Imprimir el gráfico individualmente
    print(grafico)
  # Define la carpeta de exportación (Asegúrate de que exista o créala antes)
  CARPETA_EXPORTACION <- "C:/Users/vanev/Documents/Opol/Opol IX EEN - ENE26/Graficos/Provincias/"
  
  # Nombre del archivo (ej: voto_diputados_san-jose.png)
  nombre_archivo <- paste0("voto_presidente_total_", p, ".png")
  ruta_completa_archivo <- paste0(CARPETA_EXPORTACION, nombre_archivo)
  
  # 7.2. Guardar el gráfico
  ggsave(
      filename = ruta_completa_archivo,
      plot = grafico,
      width = 12,
      height = 6,
      units = "in",
      dpi = 300
  )
  
  cat(paste0("✅ Gráfico guardado: ", ruta_completa_archivo, "\n"))
}

# ==============================================================================
# GENERACIÓN INDIVIDUAL DE 7 GRÁFICOS: VOTO VÁLIDO A PRESIDENTE POR PROVINCIA
# ==============================================================================


# Variables definidas en el script anterior
# encuesta_dsn (Diseño de muestreo ponderado para Votantes Válidos)
categorias_no_validas <- c("No Responde", "Nulo", "En Blanco", "No Sabe", "NS/NR") 
provincias <- c("san-jose", "alajuela", "cartago", "heredia", "guanacaste", "puntarenas", "limon")

for (p in provincias) {
  # 1. Filtrar el diseño de encuesta para la provincia actual
  dsn_provincia <- subset(encuesta_dsn, provincia == p)
  
  # 2. Calcular la media ponderada de voto_presidente
  resultado_provincia <- svymean(~voto_presidente, design = dsn_provincia, na.rm = TRUE)
  
  # 3. Formatear y recalcular sobre Votos Válidos
  df_resultado <- as.data.frame(resultado_provincia) %>%
    rownames_to_column(var = "Partido_raw") %>%
    rename(Proporcion = mean) %>%
    mutate(Partido = gsub("^voto_presidente", "", Partido_raw)) %>%
    filter(!is.na(Proporcion)) %>%
    mutate(es_valido = !Partido %in% categorias_no_validas) %>%
    
    # Recalculo sobre Votos Válidos (Suma de las proporciones válidas)
    mutate(Suma_Proporcion_Valida = sum(Proporcion[es_valido])) %>%
    mutate(
      `Voto (%)` = if_else(es_valido, (Proporcion / Suma_Proporcion_Valida) * 100, 0.00)
    ) %>%
    filter(es_valido) %>% # Solo mantener los votos válidos
    mutate(`Voto (%)` = MESS::round_percent(`Voto (%)`, decimals = 2))
  
  # 4. Preparar para el gráfico
  df_candidatos <- df_resultado %>%
    # Eliminar filas con 0% de voto válido (que no tendrían mención real)
    filter(`Voto (%)` > 0) %>%
    # Ordenar por porcentaje de voto válido
    mutate(Partido = fct_reorder(Partido, `Voto (%)`, .fun = sum, .desc = FALSE))

  # 5. Crear el gráfico
  grafico <- ggplot(df_candidatos, aes(x = Partido, y = `Voto (%)`)) +
    geom_col(fill = "#1d1c49", width = 0.8) +
    geom_text(aes(label = paste0(`Voto (%)`, "%")), 
              hjust = -0.1, size = 3.5, color = "black", fontface = "bold") +
    labs(
      title = paste("Distribución porcentual por voto válido a presidencia -", toupper(p)),
      subtitle = paste0("Base: Votantes Válidos en ", tools::toTitleCase(p), " (Ponderado)"),
      x = NULL,
      y = "Porcentaje de Voto Válido (%)"
    ) +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(df_candidatos$`Voto (%)`) * 1.15)) +
    theme_minimal() +
    theme(legend.position = "none")

  # 6. Imprimir el gráfico individualmente
  print(grafico)
  # Define la carpeta de exportación (Asegúrate de que exista o créala antes)
  CARPETA_EXPORTACION <- "C:/Users/vanev/Documents/Opol/Opol IX EEN - ENE26/Graficos/Provincias/"
  
  # Nombre del archivo (ej: voto_diputados_san-jose.png)
  nombre_archivo <- paste0("voto_presidente_validos_", p, ".png")
  ruta_completa_archivo <- paste0(CARPETA_EXPORTACION, nombre_archivo)
  
  # 7.2. Guardar el gráfico
  ggsave(
      filename = ruta_completa_archivo,
      plot = grafico,
      width = 12,
      height = 6,
      units = "in",
      dpi = 300
  )
  
  cat(paste0("✅ Gráfico guardado: ", ruta_completa_archivo, "\n"))
}