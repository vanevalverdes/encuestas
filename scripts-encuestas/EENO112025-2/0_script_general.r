# ==============================================================================
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

TOTAL_NACIONAL_NUEVO <- sum(poblacion_conteo$conteo) 

poblacion_tse <- poblacion_conteo %>%
  mutate(P_j = conteo / TOTAL_NACIONAL_NUEVO) %>%
  mutate(celda_ponderacion = paste(sexo, grupo_edad, provincia, sep = "_")) %>%
  select(celda_ponderacion, P_j)


# 2.B. Tabla de Totales Provinciales (N_h) para FPC
poblacion_provincia <- data.frame(
  estrato_provincia = c("san-jose", "alajuela", "cartago", "heredia", "guanacaste", "puntarenas", "limon"),
  N_provincia = c(1192706, 723861, 429191, 378289, 278818, 351197, 313972)
)

# -----------------------------------------------------------------------------
# 3. CARGA, LIMPIEZA Y CÁLCULO DE LA PONDERACIÓN
# -----------------------------------------------------------------------------

# !!! RECUERDA: Cambiar la ruta del archivo CSV a tu ruta local actual.
RUTA_BASE_DATOS <- "C:\\Users\\vanev\\Documents\\Opol\\Opol Tercera EEN - NOV25\\survey.csv"
df <- read_delim(RUTA_BASE_DATOS, delim = ",", show_col_types = FALSE)

df <- df %>%
  rename(
    sexo_raw = gender,
    religion = religion,
    conglomerado_canton = county,
    estrato_provincia = state,
    partido_preferente = party,
    educacion = education,
    voto_presidente = nationalElection,
    nunca_votaria = neverVote,
    votara = willvote,
    escala_voto = voteScale,
    voto_diputado = congress,
    apoyo_chaves = chavesSupport,
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
  #filter(votara == 'Sí' & escala_voto %in% c('4', '5'))

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

# -----------------------------------------------------------------------------
# 5. CÁLCULO DE RESULTADOS NACIONALES CLAVE (svymean, DEFF, ME)
# -----------------------------------------------------------------------------

# Cálculos de resultados
votara_resultado <- svymean(~votara, design = encuesta_dsn_total, na.rm = TRUE)
religion_resultado <- svymean(~religion, design = encuesta_dsn_total, na.rm = TRUE)
educacion_resultado <- svymean(~educacion, design = encuesta_dsn_total, na.rm = TRUE)
partido_preferente_resultado <- svymean(~partido_preferente, design = encuesta_dsn_total, na.rm = TRUE)
apoyo_chaves_resultado <- svymean(~apoyo_chaves, design = encuesta_dsn_total, na.rm = TRUE)

escala_resultado <- svymean(~escala_voto, design = encuesta_dsn, na.rm = TRUE) # Base Votantes
presidente_resultado <- svymean(~voto_presidente, design = encuesta_dsn, na.rm = TRUE) # Base Votantes
nunca_votaria_resultado <- svymean(~nunca_votaria, design = encuesta_dsn, na.rm = TRUE) # Base Votantes
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
cat("Efecto de Diseño (DEFF) (Base Total Válida):", round(deff_real, 3), "\n")
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
cat("\nEstimación Ponderada de Partido Preferente:\n")
print(partido_preferente_resultado)
cat("======================================================\n")

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
RUTA_EXPORTACION_TABLA <- "C:\\Users\\vanev\\Documents\\Opol\\Opol Tercera EEN - NOV25\\DISTRIBUCION_MUESTRA_PONDERADA_FINAL.csv"

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
rechazo_religion_ponderada <- extraer_rechazo(religion_resultado)
rechazo_educacion_ponderada <- extraer_rechazo(educacion_resultado)
rechazo_apoyo_chaves_ponderada <- extraer_rechazo(apoyo_chaves_resultado)
rechazo_nunca_votaria_ponderada <- extraer_rechazo(nunca_votaria_resultado)
rechazo_presidente_ponderada <- extraer_rechazo(presidente_resultado)
rechazo_diputado_ponderada <- extraer_rechazo(diputado_resultado)
rechazo_partido_preferente_ponderada <- extraer_rechazo(partido_preferente_resultado)
rechazo_escala_ponderada <- extraer_rechazo(escala_resultado)

respuesta_votara_ponderada <- 1 - rechazo_votara_ponderada
respuesta_religion_ponderada <- 1 - rechazo_religion_ponderada
respuesta_educacion_ponderada <- 1 - rechazo_educacion_ponderada
respuesta_apoyo_chaves_ponderada <- 1 - rechazo_apoyo_chaves_ponderada
respuesta_nunca_votaria_ponderada <- 1 - rechazo_nunca_votaria_ponderada
respuesta_presidente_ponderada <- 1 - rechazo_presidente_ponderada
respuesta_diputado_ponderada <- 1 - rechazo_diputado_ponderada
respuesta_partido_preferente_ponderada <- 1 - rechazo_partido_preferente_ponderada
respuesta_escala_ponderada <- 1 - rechazo_escala_ponderada


cat("\n======================================================\n")
cat(" TASAS DE NO RESPUESTA (RECHAZO) Y RESPUESTA PONDERADAS\n")
cat("======================================================\n")
cat("1. Base Total Válida (Pregunta Religion):\n")
cat(paste(" - Tasa de Respuesta Ponderada (religiones/no sabe):", round(respuesta_religion_ponderada * 100, 2), "%\n"))
cat(paste(" - Tasa de Rechazo Ponderada (No Responde):", round(rechazo_religion_ponderada * 100, 2), "%\n\n"))
cat("1. Base Total Válida (Pregunta Educación):\n")
cat(paste(" - Tasa de Respuesta Ponderada (Niveles educativos):", round(respuesta_educacion_ponderada * 100, 2), "%\n"))
cat(paste(" - Tasa de Rechazo Ponderada (No Responde):", round(rechazo_educacion_ponderada * 100, 2), "%\n\n"))

cat("1. Base Total Válida (Pregunta Votará):\n")
cat(paste(" - Tasa de Respuesta Ponderada (Sí/No):", round(respuesta_votara_ponderada * 100, 2), "%\n"))
cat(paste(" - Tasa de Rechazo Ponderada (No Responde):", round(rechazo_votara_ponderada * 100, 2), "%\n\n"))
cat(" - Partido Preferente (Base Total Válida):\n")
cat(paste("  - Tasa de Respuesta Ponderada (Partido/Ninguno):", round(respuesta_partido_preferente_ponderada * 100, 2), "%\n"))
cat(paste("  - Tasa de Rechazo Ponderada (No Responde):", round(rechazo_partido_preferente_ponderada * 100, 2), "%\n"))

cat(" - Apoyo a Chaves (Base Total Válida):\n")
cat(paste("  - Tasa de Respuesta Ponderada (Si/No/No Sabe):", round(respuesta_apoyo_chaves_ponderada * 100, 2), "%\n"))
cat(paste("  - Tasa de Rechazo Ponderada (No Responde):", round(rechazo_apoyo_chaves_ponderada * 100, 2), "%\n"))

cat("2. Base Votantes Válidos (Intención de Voto):\n")
cat(" - Escala seguros de votar:\n")
cat(paste("  - Tasa de Respuesta Ponderada:", round(respuesta_escala_ponderada * 100, 2), "%\n"))
cat(paste("  - Tasa de Rechazo Ponderada (No Responde):", round(rechazo_escala_ponderada * 100, 2), "%\n"))
cat(" - Voto Presidencial (Base Votantes):\n")
cat(paste("  - Tasa de Respuesta Ponderada (Candidato/Nulo/Blanco/NS):", round(respuesta_presidente_ponderada * 100, 2), "%\n"))
cat(paste("  - Tasa de Rechazo Ponderada (No Responde):", round(rechazo_presidente_ponderada * 100, 2), "%\n"))
cat(" - Voto Diputados (Base Votantes):\n")
cat(paste("  - Tasa de Respuesta Ponderada (Candidato/Nulo/Blanco/NS):", round(respuesta_diputado_ponderada * 100, 2), "%\n"))
cat(paste("  - Tasa de Rechazo Ponderada (No Responde):", round(rechazo_diputado_ponderada * 100, 2), "%\n"))
cat(" - Voto Nunca votaria (Base Votantes):\n")
cat(paste("  - Tasa de Respuesta Ponderada (Candidato/Nulo/Blanco/NS):", round(respuesta_nunca_votaria_ponderada * 100, 2), "%\n"))
cat(paste("  - Tasa de Rechazo Ponderada (No Responde):", round(rechazo_nunca_votaria_ponderada * 100, 2), "%\n"))

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
 mutate(Suma_Proporcion_Valida = sum(Proporcion[es_valido])) %>%
 mutate(
  Porcentaje_Voto_Valido = if_else(es_valido, (Proporcion / Suma_Proporcion_Valida) * 100, 0.00),
  Porcentaje_Voto_Valido = round(Porcentaje_Voto_Valido, 2),
  
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

RUTA_EXPORTACION_PROVINCIA_VOTO <- "C:\\Users\\vanev\\Documents\\Opol\\Opol Tercera EEN - NOV25\\intencion_voto_provincia_sexo_votos_validos.csv"
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
  Porcentaje_Voto_Valido = if_else(es_valido, (Proporcion / Suma_Proporcion_Valida) * 100, 0.00),
  Porcentaje_Voto_Valido = round(Porcentaje_Voto_Valido, 2),
  
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

RUTA_EXPORTACION_PROVINCIA_VOTO <- "C:\\Users\\vanev\\Documents\\Opol\\Opol Tercera EEN - NOV25\\intencion_voto_diputados_provincia_sexo_votos_validos.csv"
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
    Porcentaje_Voto_Valido = if_else(es_valido, (Proporcion / Suma_Proporcion_Valida) * 100, 0.00),
    Porcentaje_Voto_Valido = round(Porcentaje_Voto_Valido, 2)
  ) %>%
  ungroup() %>%
  filter(es_valido) 

# 4. Exportar a CSV
resultados_csv_nacional_voto_valido <- resultados_nacional_validos %>%
  select(Segmento = sexo, Candidato, Porcentaje_Voto_Valido) %>%
  mutate(Segmento = factor(Segmento, levels = c("Nacional", "H", "M"))) %>%
  arrange(Segmento, desc(Porcentaje_Voto_Valido))

RUTA_EXPORTACION_NACIONAL_VOTO <- "C:\\Users\\vanev\\Documents\\Opol\\Opol Tercera EEN - NOV25\\intencion_voto_nacional_votos_validos_por_sexo.csv"
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
  mutate(`Voto (%)` = round(Proporcion * 100, 2)) %>%
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
  labs(title = "Distribución porcentual de personas entrevistadas por intención de voto presidencial, noviembre 2025", subtitle = "Base: Total de personas que votarán (Ponderado)", x = NULL, y = "Porcentaje (%)", fill = "Tipo de Voto") +
  coord_flip() +
  scale_y_continuous(limits = c(0, max(resultados_candidatos$`Voto (%)`) * 1.15)) +
  theme_minimal() +
  theme(legend.position = "bottom")



# CÁLCULO DE LA TABLA PONDERADA DEL VOTO NUNCA VOTARIA (para gráficos)
nunca_votaria_resultado_df <- as.data.frame(nunca_votaria_resultado)

resultados_nunca_votaria_formateados <- nunca_votaria_resultado_df %>%
  rownames_to_column(var = "Candidato") %>%
  rename(Proporcion = mean, Error_Estandar = SE) %>%
  mutate(Candidato = gsub("^nunca_votaria", "", Candidato)) %>%
  mutate(`Voto (%)` = round(Proporcion * 100, 2)) %>%
  arrange(desc(`Voto (%)`))

categorias_especiales_limpias <- c("No Sabe", "NS/NR", "Nulo", "No Responde", "En blanco", "En Blanco")

resultados_nunca_candidatos <- resultados_nunca_votaria_formateados %>%
  mutate(tipo = ifelse(Candidato %in% categorias_especiales_limpias, "Ninguna persona definida", "Persona candidata")) %>%
  mutate(Candidato = fct_reorder(Candidato, `Voto (%)`, .fun = sum, .desc = FALSE)) %>%
  mutate(Candidato = fct_relevel(Candidato, categorias_especiales_limpias))

# 9.1. GRÁFICO: VOTO NUNCA VOTARIA
grafico_voto_nunca_votaria <- ggplot(resultados_nunca_candidatos, aes(x = Candidato, y = `Voto (%)`)) +
  geom_col(aes(fill = tipo), width = 0.8) +
  geom_text(aes(label = paste0(`Voto (%)`, "%")), hjust = -0.1, size = 4, color = "black", fontface = "bold") +
  scale_fill_manual(values = c("Persona candidata" = "#1d1c49", "Ninguna persona definida" = "#D45A26")) +
  labs(title = "Distribución porcentual de la opción que nunca votaría a presidencia, noviembre 2025", subtitle = "Base: Total de personas que votarán (Ponderado)", x = NULL, y = "Porcentaje (%)", fill = "Tipo de Voto") +
  coord_flip() +
  scale_y_continuous(limits = c(0, max(resultados_nunca_candidatos$`Voto (%)`) * 1.15)) +
  theme_minimal() +
  theme(legend.position = "bottom")



# 9.2. GRÁFICO: PARTIDO PREFERENTE
partido_preferente_df <- as.data.frame(partido_preferente_resultado)
resultados_partido <- partido_preferente_df %>%
  rownames_to_column(var = "Partido") %>% rename(Proporcion = mean) %>%
  mutate(Partido = gsub("^partido_preferente", "", Partido)) %>%
  mutate(`Voto (%)` = round(Proporcion * 100, 2)) %>%
  select(Partido, `Voto (%)`)

categorias_especiales_partido <- c("No Responde", "Ninguno", "NS/NR", "No Sabe")
resultados_partido <- resultados_partido %>%
  mutate(tipo = ifelse(Partido %in% categorias_especiales_partido, "Sin Partido Político", "Partido Político")) %>%
  mutate(Partido = fct_reorder(Partido, `Voto (%)`, .fun = sum, .desc = FALSE)) %>%
  mutate(Partido = fct_relevel(Partido, categorias_especiales_partido))

grafico_partido_preferente <- ggplot(resultados_partido, aes(x = Partido, y = `Voto (%)`)) +
  geom_col(aes(fill = tipo), width = 0.8) +
  geom_text(aes(label = paste0(`Voto (%)`, "%")), hjust = -0.1, size = 4, color = "black", fontface = "bold") +
  scale_fill_manual(values = c("Partido Político" = "#1d1c49", "Sin Partido Político" = "#D45A26")) +
  labs(title = "Distribución porcentual de identificación con Partido Político, noviembre 2025", subtitle = "Base: Total de entrevistas válidas (Ponderado)", x = NULL, y = "Porcentaje (%)", fill = "Clasificación") +
  coord_flip() +
  scale_y_continuous(limits = c(0, max(resultados_partido$`Voto (%)`) * 1.15)) +
  theme_minimal() +
  theme(legend.position = "bottom")


# 9.2. GRÁFICO: APOYO A CHAVES (Duplicado en el código original, renombrado para claridad)
apoyo_chaves_df <- as.data.frame(apoyo_chaves_resultado)
resultados_apoyo_chaves_gestion <- apoyo_chaves_df %>%
  rownames_to_column(var = "Respuesta") %>% rename(Proporcion = mean) %>%
  mutate(Respuesta = gsub("^apoyo_chaves", "", Respuesta)) %>%
  mutate(`Voto (%)` = round(Proporcion * 100, 2)) %>%
  select(Respuesta, `Voto (%)`)

categorias_especiales_apoyo <- c("No Responde", "No Sabe", "No responde")
resultados_apoyo_chaves_gestion <- resultados_apoyo_chaves_gestion %>%
  mutate(tipo = ifelse(Respuesta %in% categorias_especiales_apoyo, "Indefinido", "Apoyo gestión Chaves")) %>%
  mutate(Respuesta = fct_reorder(Respuesta, `Voto (%)`, .fun = sum, .desc = FALSE))

grafico_apoyo_chaves <- ggplot(resultados_apoyo_chaves_gestion, aes(x = Respuesta, y = `Voto (%)`)) +
  geom_col(aes(fill = tipo), width = 0.8) +
  geom_text(aes(label = paste0(`Voto (%)`, "%")), hjust = -0.1, size = 5, color = "black", fontface = "bold") +
  scale_fill_manual(values = c("Apoyo gestión Chaves" = "#1d1c49", "Indefinido" = "#D45A26")) +
  labs(title = "Distribución porcentual de apoyo a la gestión de Rodrigo Chaves, noviembre 2025", subtitle = "Base: Total entrevistas Válidas (Ponderado)", x = NULL, y = "Porcentaje (%)", fill = NULL) +
  coord_flip() +
  scale_y_continuous(limits = c(0, max(resultados_apoyo_chaves_gestion$`Voto (%)`) * 1.1)) +
  theme_minimal() +
  theme(legend.position = "none")

# 9.3. GRÁFICO: VOTO DIPUTADO
voto_diputado_df <- as.data.frame(diputado_resultado)
resultados_diputado <- voto_diputado_df %>%
  rownames_to_column(var = "Partido") %>% rename(Proporcion = mean) %>%
  mutate(Partido = gsub("^voto_diputado", "", Partido)) %>%
  mutate(`Voto (%)` = round(Proporcion * 100, 2)) %>%
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
  labs(title = "Distribución porcentual de intención de voto para diputaciones, noviembre 2025", subtitle = "Base: Total de personas que votarán (Ponderado)", x = NULL, y = "Porcentaje de Voto (%)", fill = "Clasificación") +
  coord_flip() +
  scale_y_continuous(limits = c(0, max(resultados_diputado$`Voto (%)`) * 1.15)) +
  theme_minimal() +
  theme(legend.position = "bottom")


# 9.4. GRÁFICO: VOTARÁ
votara_df <- as.data.frame(votara_resultado)
resultados_votara <- votara_df %>%
  rownames_to_column(var = "Respuesta") %>% rename(Proporcion = mean) %>%
  mutate(Respuesta = gsub("^votara", "", Respuesta)) %>%
  mutate(`Voto (%)` = round(Proporcion * 100, 2)) %>%
  select(Respuesta, `Voto (%)`)

resultados_votara <- resultados_votara %>%
  mutate(tipo = ifelse(Respuesta == "Sí", "Votará", "No Votará / No Responde")) %>%
  mutate(Respuesta = fct_relevel(Respuesta, "No Responde", "No", "Sí")) 

grafico_votara <- ggplot(resultados_votara, aes(x = Respuesta, y = `Voto (%)`)) +
  geom_col(aes(fill = tipo), width = 0.8) +
  geom_text(aes(label = paste0(`Voto (%)`, "%")), hjust = -0.1, size = 5, color = "black", fontface = "bold") +
  scale_fill_manual(values = c("Votará" = "#1d1c49", "No Votará / No Responde" = "#D45A26")) +
  labs(title = "Distribución porcentual de decididos a votar en próximas elecciones, noviembre 2025", subtitle = "Base: Total entrevistas Válidas (Ponderado)", x = NULL, y = "Porcentaje (%)", fill = NULL) +
  coord_flip() +
  scale_y_continuous(limits = c(0, max(resultados_votara$`Voto (%)`) * 1.1)) +
  theme_minimal() +
  theme(legend.position = "none")


# 9.5. GRÁFICO: DISTRIBUCIÓN DE RELIGIÓN
religion_df <- as.data.frame(religion_resultado)
resultados_religion <- religion_df %>%
  rownames_to_column(var = "Religion") %>% rename(Proporcion = mean) %>%
  mutate(Religion = gsub("^religion", "", Religion)) %>%
  mutate(`Porcentaje (%)` = round(Proporcion * 100, 2)) %>%
  select(Religion, `Porcentaje (%)`)

resultados_religion <- resultados_religion %>%
  mutate(tipo = ifelse(Religion %in% c("No Responde"), "Otras/No Definido", "Mayorías")) %>%
  mutate(Religion = fct_reorder(Religion, `Porcentaje (%)`, .fun = sum, .desc = FALSE))

grafico_religion <- ggplot(resultados_religion, aes(x = Religion, y = `Porcentaje (%)`)) +
  geom_col(aes(fill = tipo), width = 0.8) +
  geom_text(aes(label = paste0(`Porcentaje (%)`, "%")), hjust = -0.1, size = 4, color = "black", fontface = "bold") +
  scale_fill_manual(values = c("Mayorías" = "#1d1c49", "Otras/No Definido" = "#D45A26")) +
  labs(title = "Distribución porcentual por religión, noviembre 2025", subtitle = "Base: Total entrevistas Válidas (Ponderado)", x = NULL, y = "Porcentaje (%)", fill = NULL) +
  coord_flip() +
  scale_y_continuous(limits = c(0, max(resultados_religion$`Porcentaje (%)`) * 1.15)) +
  theme_minimal() +
  theme(legend.position = "bottom")


# 9.6. GRÁFICO: DISTRIBUCIÓN DE EDUCACIÓN (CÓDIGO COMPLETADO)
# educacion_resultado <- svymean(~educacion, design = encuesta_dsn_total, na.rm = TRUE)
educacion_df <- as.data.frame(educacion_resultado)
resultados_educacion <- educacion_df %>%
  rownames_to_column(var = "Nivel_Educacion") %>% rename(Proporcion = mean) %>%
  mutate(Nivel_Educacion = gsub("^educacion", "", Nivel_Educacion)) %>%
  mutate(`Porcentaje (%)` = round(Proporcion * 100, 2)) %>%
  select(Nivel_Educacion, `Porcentaje (%)`)

categorias_especiales_edu <- c("No Responde", "No Sabe")
resultados_educacion <- resultados_educacion %>%
  mutate(tipo = ifelse(Nivel_Educacion %in% categorias_especiales_edu, "No Definido", "Nivel Educativo")) %>%
  mutate(Nivel_Educacion = fct_reorder(Nivel_Educacion, `Porcentaje (%)`, .fun = sum, .desc = FALSE))

grafico_educacion <- ggplot(resultados_educacion, aes(x = Nivel_Educacion, y = `Porcentaje (%)`)) +
  geom_col(aes(fill = tipo), width = 0.8) +
  geom_text(aes(label = paste0(`Porcentaje (%)`, "%")), hjust = -0.1, size = 4, color = "black", fontface = "bold") +
  scale_fill_manual(values = c("Nivel Educativo" = "#1d1c49", "No Definido" = "#D45A26")) +
  labs(title = "Distribución porcentual de personas entrevistadas por Nivel Educativo, noviembre 2025", subtitle = "Base: Total entrevistas válidas (Ponderado)", x = NULL, y = "Porcentaje (%)", fill = NULL) +
  coord_flip() +
  scale_y_continuous(limits = c(0, max(resultados_educacion$`Porcentaje (%)`) * 1.15)) +
  theme_minimal() +
  theme(legend.position = "bottom")

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
    mutate(Porcentaje = (n_ponderado / sum(n_ponderado)) * 100) %>%
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
    geom_text(aes(label = paste0(round(Porcentaje, 1), "%")),
              position = position_dodge(width = 0.8), # Misma posición que las barras
              hjust = -0.1, size = 3.5, fontface = "bold") +
    
    # AJUSTES DE COLOR Y TÍTULOS
    scale_fill_manual(values = c("Hombres" = "#1d1c49", "Mujeres" = "#D45A26")) +
    labs(
        title = "Distribución porcentual de personas entrevistadas por provincia y sexo, noviembre 2025",
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
        `% Muestra Bruta` = (N_Bruto / Total_Bruto) * 100
    ) %>%
    # Formatear la etiqueta para el gráfico
    mutate(
        Etiqueta_Final = paste0(round(`% Muestra Bruta`, 1), "% (n=", N_Bruto, ")")
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
        Etiqueta_Final = paste0(round(`% Muestra`, 1), "% (n=", N_Bruto, ")")
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
        `% Muestra` = (N_Ponderado / Total_Ponderado) * 100,
        Tipo_Distribucion = "2. Muestra Ponderada (AJUSTADA)"
    ) %>%
    mutate(
        # CAMBIO REALIZADO AQUÍ: Solo muestra el porcentaje
        Etiqueta_Final = paste0(round(`% Muestra`, 1), "%")
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
    `Voto (%)` = if_else(es_valido, (Proporcion / Suma_Proporcion_Valida) * 100, 0.00)
  ) %>%
  filter(es_valido) %>% # Solo mantener los votos válidos
  mutate(`Voto (%)` = round(`Voto (%)`, 2))

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
    title = "Distribución porcentual de personas entrevistadas por Intención de Voto Válido a presidencia, noviembre 2025",
    subtitle = "Base: Votantes Válidos a Nivel Nacional (Excluye Nulos/Blancos/NS/NR - Ponderado)",
    x = NULL,
    y = "Porcentaje de Voto Válido (%)"
  ) +
  coord_flip() +
  scale_y_continuous(limits = c(0, max(df_partidos$`Voto (%)`) * 1.15)) +
  theme_minimal() +
  theme(legend.position = "none")



# ==============================================================================
# GENERACIÓN DE GRÁFICO: ESCALA DE DECIDIDOS A VOTAR (PONDERADO)
# ==============================================================================

# Variables de limpieza
categorias_no_validas <- c("No Responde", "Nulo", "En Blanco", "No Sabe", "NS/NR") 
# La base de diseño 'encuesta_dsn' ya está definida para Votantes Válidos (votara == 'Sí')

# 1. Calcular la media ponderada de voto_presidente
resultado_nacional <- svymean(~escala_voto, design = encuesta_dsn, na.rm = TRUE)

# 2. Formatear y recalcular sobre Votos Válidos
df_resultado <- as.data.frame(resultado_nacional) %>%
  rownames_to_column(var = "Partido_raw") %>%
  rename(Proporcion = mean) %>%
  mutate(Partido = gsub("^escala_voto", "", Partido_raw)) %>%
  filter(!is.na(Proporcion)) %>%
  mutate(es_valido = !Partido %in% categorias_no_validas) %>%
  
  # Recalculo sobre Votos Válidos
  mutate(Suma_Proporcion_Valida = sum(Proporcion[es_valido])) %>%
  mutate(
    `Voto (%)` = if_else(es_valido, (Proporcion / Suma_Proporcion_Valida) * 100, 0.00)
  ) %>%
  filter(es_valido) %>% # Solo mantener los votos válidos
  mutate(`Voto (%)` = round(`Voto (%)`, 2))

# 3. Preparar para el gráfico
df_partidos <- df_resultado %>%
  # Eliminar filas con 0% de voto válido
  filter(`Voto (%)` > 0) %>%
  # Ordenar por porcentaje de voto válido
  mutate(Partido = fct_reorder(Partido, `Voto (%)`, .fun = sum, .desc = FALSE))

# 4. Crear el gráfico
grafico_escala_voto <- ggplot(df_partidos, aes(x = Partido, y = `Voto (%)`)) +
  geom_col(fill = "#1d1c49", width = 0.8) +
  geom_text(aes(label = paste0(`Voto (%)`, "%")), 
            hjust = -0.1, size = 4.0, color = "black", fontface = "bold") +
  labs(
    title = "Distribución porcentual de entrevistas por escala de decididos a votar, noviembre 2025",
    subtitle = "Base: Votantes Válidos a Nivel Nacional (Excluye NS/NR - Ponderado)",
    x = NULL,
    y = "Porcentaje de Voto Válido (%)"
  ) +
  coord_flip() +
  scale_y_continuous(limits = c(0, max(df_partidos$`Voto (%)`) * 1.15)) +
  theme_minimal() +
  theme(legend.position = "none")


# Imprimir el gráfico
cat("\n✅ Todos los objetos de gráficos (grafico_voto_mejorado, grafico_religion, etc.) han sido generados y almacenados en el ambiente de R. Puedes imprimirlos o guardarlos manualmente.\n")

  CARPETA_EXPORTACION <- "C:/Users/vanev/Documents/Opol/Opol Tercera EEN - NOV25/Graficos/"
  
  # Nombre del archivo (ej: voto_diputados_san-jose.png)
  ruta_completa_archivo <- paste0(CARPETA_EXPORTACION, "grafico_escala_voto.png")
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
  ruta_completa_archivo <- paste0(CARPETA_EXPORTACION, "grafico_religion.png")
  grafico <- grafico_religion
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
  ruta_completa_archivo <- paste0(CARPETA_EXPORTACION, "grafico_educacion.png")
  grafico <- grafico_educacion
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
  ruta_completa_archivo <- paste0(CARPETA_EXPORTACION, "grafico_partido_preferente.png")
  grafico <- grafico_partido_preferente
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
  ruta_completa_archivo <- paste0(CARPETA_EXPORTACION, "grafico_apoyo_chaves.png")
  grafico <- grafico_apoyo_chaves
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
  ruta_completa_archivo <- paste0(CARPETA_EXPORTACION, "grafico_voto_nunca_votaria.png")
  grafico <- grafico_voto_nunca_votaria
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
        mutate(`Voto (%)` = round(Proporcion * 100, 2))
        
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
  CARPETA_EXPORTACION <- "C:/Users/vanev/Documents/Opol/Opol Tercera EEN - NOV25/Graficos/Provincias/"
  
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
    mutate(`Voto (%)` = round(`Voto (%)`, 2))
  
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
  CARPETA_EXPORTACION <- "C:/Users/vanev/Documents/Opol/Opol Tercera EEN - NOV25/Graficos/Provincias/"
  
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
        mutate(`Voto (%)` = round(Proporcion * 100, 2))
        
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
  CARPETA_EXPORTACION <- "C:/Users/vanev/Documents/Opol/Opol Tercera EEN - NOV25/Graficos/Provincias/"
  
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
    mutate(`Voto (%)` = round(`Voto (%)`, 2))
  
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
  CARPETA_EXPORTACION <- "C:/Users/vanev/Documents/Opol/Opol Tercera EEN - NOV25/Graficos/Provincias/"
  
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