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
RUTA_BASE_DATOS <- "C:\\Users\\vanev\\Documents\\Opol\\Opol Cuarta EEN - DIC25\\survey.csv"
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
  filter(votara == 'Sí' & escala_voto == '5')

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
  labs(title = "Distribución porcentual de personas entrevistadas por intención de voto presidencial, diciembre2025", subtitle = "Base: Total de personas que votarán (Ponderado)", x = NULL, y = "Porcentaje (%)", fill = "Tipo de Voto") +
  coord_flip() +
  scale_y_continuous(limits = c(0, max(resultados_candidatos$`Voto (%)`) * 1.15)) +
  theme_minimal() +
  theme(legend.position = "bottom")

nunca_votaria_resultado <- svymean(~nunca_votaria, design = encuesta_dsn, na.rm = TRUE) # Base Votantes
