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
RUTA_BASE_DATOS <- "C:\\Users\\vanev\\Documents\\Opol\\Opol Sexta EEN - ENE26\\survey.csv"
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

# 0. CONFIGURACIÓN DE RUTAS (Asegúrate de que estas carpetas existan)
CARPETA_EXPORTACION <- "C:\\Users\\vanev\\Documents\\Opol\\Opol Sexta EEN - ENE26\\"

# 4.2. BASE 2: Votantes Válidos (Solo Escala 5)
# -----------------------------------------------------------------------------
df_analisis_nacional <- df_analisis_total %>%
  filter(votara == 'Sí' & escala_voto == '5') %>%
  mutate(across(where(is.character), as.factor)) %>%
  droplevels()

# FUNCIÓN AUXILIAR: svymean_seguro
# Evita el error de "contrasts" calculando manualmente si solo hay 1 nivel
svymean_seguro <- function(formula, design) {
  var_name <- all.vars(formula)
  datos_col <- design$variables[[var_name]]
  
  # Si la variable es constante o tiene un solo nivel real
  if (length(unique(na.omit(datos_col))) < 2) {
    cat("\nℹ️ Calculando manualmente (Variable constante):", var_name)
    val_unico <- as.character(unique(na.omit(datos_col))[1])
    # Crear un objeto similar al que devuelve svymean
    res <- setNames(1, paste0(var_name, val_unico))
    attr(res, "var") <- matrix(0, 1, 1) # Varianza 0 porque es constante
    class(res) <- "svystat"
    return(res)
  } else {
    return(svymean(formula, design = design, na.rm = TRUE))
  }
}

# Recálculo de n_h para el FPC
df_analisis_nacional <- df_analisis_nacional %>%
  select(-any_of("n_provincia")) %>% 
  left_join(
    df_analisis_nacional %>% group_by(provincia) %>% summarise(n_provincia = n(), .groups = 'drop'),
    by = "provincia"
  )

# DISEÑO DE MUESTREO COMPLEJO 2
encuesta_dsn <- svydesign(
  ids = ~conglomerado_unico,
  strata = ~provincia,
  weights = ~ponderador_final,
  data = df_analisis_nacional,
  fpc = ~N_provincia
)

# -----------------------------------------------------------------------------
# 5. CÁLCULO DE RESULTADOS NACIONALES CLAVE
# -----------------------------------------------------------------------------

# Usamos svymean_seguro para las variables que pueden ser constantes en Escala 5
escala_resultado   <- svymean_seguro(~escala_voto, encuesta_dsn)
presidente_resultado <- svymean_seguro(~voto_presidente, encuesta_dsn)
nunca_votaria_resultado <- svymean_seguro(~nunca_votaria, encuesta_dsn)
diputado_resultado <- svymean_seguro(~voto_diputado, encuesta_dsn)

# Estos se calculan sobre la base TOTAL (sin riesgo de ser constantes habitualmente)
votara_resultado <- svymean(~votara, design = encuesta_dsn_total, na.rm = TRUE)
religion_resultado <- svymean(~religion, design = encuesta_dsn_total, na.rm = TRUE)
educacion_resultado <- svymean(~educacion, design = encuesta_dsn_total, na.rm = TRUE)
partido_preferente_resultado <- svymean(~partido_preferente, design = encuesta_dsn_total, na.rm = TRUE)
apoyo_chaves_resultado <- svymean(~apoyo_chaves, design = encuesta_dsn_total, na.rm = TRUE)



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
RUTA_EXPORTACION_TABLA <- "C:\\Users\\vanev\\Documents\\Opol\\Opol Sexta EEN - ENE26\\DISTRIBUCION_MUESTRA_PONDERADA_FINAL.csv"

readr::write_csv(
  x = tabla_exportar,
  file = RUTA_EXPORTACION_TABLA,
  na = "",
  append = FALSE
)

cat(paste0("\n✅ Exportación de Distribución de Muestra/Población: ", RUTA_EXPORTACION_TABLA, "\n"))


# B. CÁLCULO DE VOTO NACIONAL POR SEXO (Base Voto Válido)
# -------------------------------------------------------
categorias_no_validas <- c("No Responde", "Nulo", "En Blanco", "No Sabe", "NS/NR")

# 1. Intentar svyby. Si falla por falta de niveles, calculamos solo el nacional.
svy_combined_nacional <- tryCatch({
    s_sexo <- svyby(~voto_presidente, by = ~sexo, design = encuesta_dsn, FUN = svymean, na.rm = TRUE)
    
    # Preparar el Nacional para unir
    s_nac  <- as.data.frame(presidente_resultado) %>%
              rownames_to_column(var = "Candidato_raw") %>%
              mutate(sexo = "Nacional", Candidato_raw = gsub("voto_presidente", "", Candidato_raw)) %>%
              pivot_wider(names_from = Candidato_raw, values_from = mean, names_prefix = "voto_presidente")
    
    bind_rows(s_sexo, s_nac)
}, error = function(e) {
    cat("\n⚠️ No se pudo desglosar por sexo (datos insuficientes). Generando solo Nacional.")
    as.data.frame(presidente_resultado) %>%
      rownames_to_column(var = "Candidato_raw") %>%
      mutate(sexo = "Nacional", Candidato_raw = gsub("voto_presidente", "", Candidato_raw)) %>%
      pivot_wider(names_from = Candidato_raw, values_from = mean, names_prefix = "voto_presidente")
})

# 2. Procesar para exportación
resultados_nacional_validos <- svy_combined_nacional %>%
  select(sexo, starts_with("voto_presidente")) %>%
  pivot_longer(cols = starts_with("voto_presidente"), names_to = "Candidato_raw", values_to = "Proporcion") %>%
  mutate(Candidato = gsub("voto_presidente", "", Candidato_raw)) %>%
  filter(!is.na(Proporcion)) %>%
  mutate(es_valido = !Candidato %in% categorias_no_validas) %>%
  group_by(sexo) %>%
  filter(any(es_valido)) %>%
  mutate(Porcentaje_Voto_Valido = round((Proporcion / sum(Proporcion[es_valido])) * 100, 2)) %>%
  filter(es_valido) %>%
  ungroup() %>%
  select(Segmento = sexo, Candidato, Porcentaje_Voto_Valido) %>%
  arrange(Segmento, desc(Porcentaje_Voto_Valido))

readr::write_csv(resultados_nacional_validos, paste0(CARPETA_EXPORTACION, "intencion_voto_nacional_votos_validos_por_sexo.csv"))
cat(paste0("\n✅ Exportación de Intención de Voto Nacional por Sexo (Votos Válidos): ", CARPETA_EXPORTACION, "intencion_voto_nacional_votos_validos_por_sexo.csv\n"))++++++


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



# CÁLCULO DE LA TABLA PONDERADA DEL VOTO NUNCA VOTARIA (para gráficos)
nunca_votaria_resultado_df <- as.data.frame(nunca_votaria_resultado)

resultados_nunca_votaria_formateados <- nunca_votaria_resultado_df %>%
  rownames_to_column(var = "Candidato") %>%
  rename(Proporcion = mean, Error_Estandar = SE) %>%
  mutate(Candidato = gsub("^nunca_votaria", "", Candidato)) %>%
  mutate(`Voto (%)` = MESS::round_percent(Proporcion, decimals = 2)) %>%
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
  labs(title = "Distribución porcentual de la opción que nunca votaría a presidencia, enero 2026", subtitle = "Base: Total de personas que votarán (Ponderado)", x = NULL, y = "Porcentaje (%)", fill = "Tipo de Voto") +
  coord_flip() +
  scale_y_continuous(limits = c(0, max(resultados_nunca_candidatos$`Voto (%)`) * 1.15)) +
  theme_minimal() +
  theme(legend.position = "bottom")


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