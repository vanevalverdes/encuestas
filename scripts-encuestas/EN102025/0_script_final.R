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
RUTA_BASE_DATOS <- "C:\\Users\\vanev\\Downloads\\Opol EN102025\\Base de datos\\survey.csv"
df <- read_csv(RUTA_BASE_DATOS) 

df <- df %>%
    rename(
        sexo_raw = gender,
        religion = religion,
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
df_analisis_nacional <- df_analisis_total %>%
    filter(votara == 'Sí')

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
partido_preferente_resultado <- svymean(~partido_preferente, design = encuesta_dsn_total, na.rm = TRUE)
presidente_resultado <- svymean(~voto_presidente, design = encuesta_dsn, na.rm = TRUE) # Base Votantes
diputado_resultado <- svymean(~voto_diputado, design = encuesta_dsn, na.rm = TRUE) # Base Votantes

# CÁLCULO DE DEFF Y MARGEN DE ERROR (Usando 'votara' como ejemplo)
# -----------------------------------------------------------------
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
cat("          MÉTRICAS DE DISEÑO Y ERROR                   \n")
cat("======================================================\n")
cat("Efecto de Diseño (DEFF) (Base Total Válida):", round(deff_real, 3), "\n")
cat("Margen de Error Final (95% Conf. - Ajustado por DEFF): ±", round(ME_final_porcentaje, 2), "%\n")

cat("\n======================================================\n")
cat("             RESULTADOS NACIONALES PONDERADOS          \n")
cat("======================================================\n")
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
RUTA_EXPORTACION_TABLA <- "C:\\Users\\vanev\\Downloads\\Opol EN102025\\DISTRIBUCION_MUESTRA_PONDERADA_FINAL.csv"

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
rechazo_partido_preferente_ponderada <- extraer_rechazo(partido_preferente_resultado)

respuesta_votara_ponderada <- 1 - rechazo_votara_ponderada
respuesta_presidente_ponderada <- 1 - rechazo_presidente_ponderada
respuesta_diputado_ponderada <- 1 - rechazo_diputado_ponderada
respuesta_partido_preferente_ponderada <- 1 - rechazo_partido_preferente_ponderada


cat("\n======================================================\n")
cat("    TASAS DE NO RESPUESTA (RECHAZO) Y RESPUESTA PONDERADAS\n")
cat("======================================================\n")
cat("1. Base Total Válida (Pregunta Votará):\n")
cat(paste("    - Tasa de Respuesta Ponderada (Sí/No):", round(respuesta_votara_ponderada * 100, 2), "%\n"))
cat(paste("    - Tasa de Rechazo Ponderada (No Responde):", round(rechazo_votara_ponderada * 100, 2), "%\n\n"))

cat("2. Base Votantes Válidos (Intención de Voto):\n")
cat("    - Voto Presidencial (Base Votantes):\n")
cat(paste("      - Tasa de Respuesta Ponderada (Candidato/Nulo/Blanco/NS):", round(respuesta_presidente_ponderada * 100, 2), "%\n"))
cat(paste("      - Tasa de Rechazo Ponderada (No Responde):", round(rechazo_presidente_ponderada * 100, 2), "%\n"))
cat("    - Partido Preferente (Base Total Válida):\n")
cat(paste("      - Tasa de Respuesta Ponderada (Partido/Ninguno):", round(respuesta_partido_preferente_ponderada * 100, 2), "%\n"))
cat(paste("      - Tasa de Rechazo Ponderada (No Responde):", round(rechazo_partido_preferente_ponderada * 100, 2), "%\n"))
cat("======================================================\n")


# -----------------------------------------------------------------------------
# 8. EXPORTACIONES CSV AVANZADAS (VOTO VÁLIDO POR PROVINCIA Y NACIONAL/SEXO)
# -----------------------------------------------------------------------------

categorias_no_validas <- c("No Responde", "Nulo", "En blanco", "No Sabe", "NS/NR") 

# A. CÁLCULO DE VOTO POR PROVINCIA Y SEXO (Base Voto Válido)
# ----------------------------------------------------------

# 1. Combinar resultados por provincia/sexo y provincia/total
svy_sex_provincia <- svyby(~voto_presidente, by = ~provincia + sexo, design = encuesta_dsn, FUN = svymean, na.rm = TRUE)
svy_provincia_total <- svyby(~voto_presidente, by = ~provincia, design = encuesta_dsn, FUN = svymean, na.rm = TRUE) %>% mutate(sexo = "Total")
svy_combined <- bind_rows(svy_sex_provincia, svy_provincia_total)

# 2. Convertir a formato largo
resultados_long_provincia <- svy_combined %>%
    select(-starts_with("se.")) %>% 
    pivot_longer(cols = starts_with("voto_presidente"), names_to = "Candidato_raw", values_to = "Proporcion") %>%
    mutate(Candidato = gsub("^voto_presidente", "", Candidato_raw)) %>%
    filter(!is.na(Proporcion)) 

# 3. Recálculo sobre Votos Válidos
resultados_validos_provincia <- resultados_long_provincia %>%
    mutate(es_valido = !Candidato %in% categorias_no_validas) %>%
    group_by(provincia, sexo) %>%
    mutate(Suma_Proporcion_Valida = sum(Proporcion[es_valido])) %>%
    mutate(
        Porcentaje_Voto_Valido = if_else(es_valido, (Proporcion / Suma_Proporcion_Valida) * 100, 0.00),
        Porcentaje_Voto_Valido = round(Porcentaje_Voto_Valido, 2)
    ) %>%
    ungroup() %>%
    filter(es_valido) 

# 4. Exportar a CSV
resultados_csv_provincia_voto_valido <- resultados_validos_provincia %>%
    select(Provincia = provincia, Segmento = sexo, Candidato, Porcentaje_Voto_Valido) %>%
    arrange(Provincia, Segmento, desc(Porcentaje_Voto_Valido))

RUTA_EXPORTACION_PROVINCIA_VOTO <- "C:\\Users\\vanev\\Downloads\\Opol EN102025\\intencion_voto_provincia_sexo_votos_validos.csv"
readr::write_csv(resultados_csv_provincia_voto_valido, RUTA_EXPORTACION_PROVINCIA_VOTO)
cat(paste0("✅ Exportación de Voto Válido por Provincia/Sexo: ", RUTA_EXPORTACION_PROVINCIA_VOTO, "\n"))


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

RUTA_EXPORTACION_NACIONAL_VOTO <- "C:\\Users\\vanev\\Downloads\\Opol EN102025\\intencion_voto_nacional_votos_validos_por_sexo.csv"
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

categorias_especiales_limpias <- c("No Sabe", "NS/NR", "Nulo", "No Responde", "En blanco")

resultados_candidatos <- resultados_formateados %>%
    mutate(tipo = ifelse(Candidato %in% categorias_especiales_limpias, "No Candidato", "Candidato")) %>%
    mutate(Candidato = fct_reorder(Candidato, `Voto (%)`, .fun = sum, .desc = FALSE)) %>%
    mutate(Candidato = fct_relevel(Candidato, categorias_especiales_limpias))

# 9.1. GRÁFICO: VOTO PRESIDENCIAL
grafico_voto_mejorado <- ggplot(resultados_candidatos, aes(x = Candidato, y = `Voto (%)`)) +
    geom_col(aes(fill = tipo), width = 0.8) +
    geom_text(aes(label = paste0(`Voto (%)`, "%")), hjust = -0.1, size = 4, color = "black", fontface = "bold") +
    scale_fill_manual(values = c("Candidato" = "#1d1c49", "No Candidato" = "#D45A26")) +
    labs(title = "Intención de Voto Presidencial", subtitle = "Encuesta Nacional OPOL Octubre 2025", x = NULL, y = "Porcentaje de Voto (%)", fill = "Tipo de Voto") +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(resultados_candidatos$`Voto (%)`) * 1.15)) +
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
    mutate(tipo = ifelse(Partido %in% categorias_especiales_partido, "No Identificado", "Identificado")) %>%
    mutate(Partido = fct_reorder(Partido, `Voto (%)`, .fun = sum, .desc = FALSE)) %>%
    mutate(Partido = fct_relevel(Partido, categorias_especiales_partido))

grafico_partido_preferente <- ggplot(resultados_partido, aes(x = Partido, y = `Voto (%)`)) +
    geom_col(aes(fill = tipo), width = 0.8) +
    geom_text(aes(label = paste0(`Voto (%)`, "%")), hjust = -0.1, size = 4, color = "black", fontface = "bold") +
    scale_fill_manual(values = c("Identificado" = "#1d1c49", "No Identificado" = "#D45A26")) +
    labs(title = "Preferencia o Identificación con Partido Político", subtitle = "Encuesta Nacional OPOL Octubre 2025", x = NULL, y = "Porcentaje (%)", fill = "Clasificación") +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(resultados_partido$`Voto (%)`) * 1.15)) +
    theme_minimal() +
    theme(legend.position = "bottom")

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
    labs(title = "Intención de Voto para Diputados", subtitle = "Encuesta Nacional OPOL Octubre 2025", x = NULL, y = "Porcentaje de Voto (%)", fill = "Clasificación") +
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
    labs(title = "¿Usted votará en las próximas elecciones?", subtitle = "Encuesta Nacional OPOL Octubre 2025", x = NULL, y = "Porcentaje (%)", fill = NULL) +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(resultados_votara$`Voto (%)`) * 1.1)) +
    theme_minimal() +
    theme(legend.position = "none")


# 9.5. GRÁFICO: DISTRIBUCIÓN DE RELIGIÓN
religion_resultado <- svymean(~religion, design = encuesta_dsn_total, na.rm = TRUE)
religion_df <- as.data.frame(religion_resultado)
resultados_religion <- religion_df %>%
    rownames_to_column(var = "Religion") %>% rename(Proporcion = mean) %>%
    mutate(Religion = gsub("^religion", "", Religion)) %>%
    mutate(`Porcentaje (%)` = round(Proporcion * 100, 2)) %>%
    select(Religion, `Porcentaje (%)`)

resultados_religion <- resultados_religion %>%
    mutate(tipo = ifelse(Religion %in% c("No Responde", "Otro"), "Otras/No Definido", "Mayorías")) %>%
    mutate(Religion = fct_reorder(Religion, `Porcentaje (%)`, .fun = sum, .desc = FALSE))

grafico_religion <- ggplot(resultados_religion, aes(x = Religion, y = `Porcentaje (%)`)) +
    geom_col(aes(fill = tipo), width = 0.8) +
    geom_text(aes(label = paste0(`Porcentaje (%)`, "%")), hjust = -0.1, size = 4, color = "black", fontface = "bold") +
    scale_fill_manual(values = c("Mayorías" = "#1d1c49", "Otras/No Definido" = "#D45A26")) +
    labs(title = "Distribución Ponderada por Religión", subtitle = "Base: Total Encuestas Válidas (Ponderado)", x = NULL, y = "Porcentaje (%)", fill = NULL) +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(resultados_religion$`Porcentaje (%)`) * 1.15)) +
    theme_minimal() +
    theme(legend.position = "bottom")

# 9.6. GRÁFICO: DISTRIBUCIÓN DE EDUCACIÓN (CÓDIGO COMPLETADO)
educacion_resultado <- svymean(~educacion, design = encuesta_dsn_total, na.rm = TRUE)
educacion_df <- as.data.frame(educacion_resultado)
resultados_educacion <- educacion_df %>%
    rownames_to_column(var = "Nivel_Educacion") %>% rename(Proporcion = mean) %>%
    mutate(Nivel_Educacion = gsub("^educacion", "", Nivel_Educacion)) %>%
    mutate(`Porcentaje (%)` = round(Proporcion * 100, 2)) %>%
    select(Nivel_Educacion, `Porcentaje (%)`)

categorias_especiales_edu <- c("No Responde", "NS/NR")
resultados_educacion <- resultados_educacion %>%
    mutate(tipo = ifelse(Nivel_Educacion %in% categorias_especiales_edu, "No Definido", "Definido")) %>%
    mutate(Nivel_Educacion = fct_reorder(Nivel_Educacion, `Porcentaje (%)`, .fun = sum, .desc = FALSE))

grafico_educacion <- ggplot(resultados_educacion, aes(x = Nivel_Educacion, y = `Porcentaje (%)`)) +
    geom_col(aes(fill = tipo), width = 0.8) +
    geom_text(aes(label = paste0(`Porcentaje (%)`, "%")), hjust = -0.1, size = 4, color = "black", fontface = "bold") +
    scale_fill_manual(values = c("Definido" = "#1d1c49", "No Definido" = "#D45A26")) +
    labs(title = "Distribución Ponderada por Nivel Educativo", subtitle = "Base: Total Encuestas Válidas (Ponderado)", x = NULL, y = "Porcentaje (%)", fill = NULL) +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(resultados_educacion$`Porcentaje (%)`) * 1.15)) +
    theme_minimal() +
    theme(legend.position = "bottom")

cat("\n✅ Todos los objetos de gráficos (grafico_voto_mejorado, grafico_religion, etc.) han sido generados y almacenados en el ambiente de R. Puedes imprimirlos o guardarlos manualmente.\n")