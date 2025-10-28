
# 6. RESULTADOS PREGUNTAS NACIONALES
# -----------------------------------

# Se define un df_analisis_nacional con solo las respuestas de decididos a votar
df_analisis_nacional <- df %>%
    filter(category == 1) %>% 
    filter(votara == 'Sí') %>% 
    mutate(conglomerado_unico = paste(estrato_provincia, conglomerado_canton, sep = "_")) %>%
    left_join(poblacion_provincia, by = c("provincia" = "estrato_provincia")) %>%
    filter(!is.na(ponderador_final) & !is.na(conglomerado_unico) & !is.na(N_provincia))


# 3.1. Calcular el tamaño de la muestra por estrato (n_h)
tamanio_muestral_provincia <- df_analisis_nacional %>%
    group_by(provincia) %>%
    summarise(n_provincia = n()) %>%
    ungroup()

# 3.2. Unir el tamaño muestral (n_h) al DF analizado
df_analisis_nacional <- df_analisis_nacional %>%
    left_join(tamanio_muestral_provincia, by = "provincia")


# 4. DEFINICIÓN DEL DISEÑO Y CÁLCULO FINAL
# -----------------------------------------

# 4.1. Definición del Diseño de Muestreo Complejo
# (Usamos la columna N_provincia, que contiene N_h, y R infiere n_h)
encuesta_dsn <- svydesign(
    ids = ~conglomerado_unico,         
    strata = ~provincia,               
    weights = ~ponderador_final,       
    data = df_analisis_nacional,               
    fpc = ~N_provincia                 
)


# Definición del Diseño para Base TOTAL (df_analisis)
# Usamos df_analisis (Base Válida Total) para uso de en las preguntas sociodemográficas.

# 1.1. Recálculo del Diseño (usando la base TOTAL)
df_analisis_total <- df %>%
    filter(category == 1) %>% 
    mutate(conglomerado_unico = paste(estrato_provincia, conglomerado_canton, sep = "_")) %>%
    left_join(poblacion_provincia, by = c("provincia" = "estrato_provincia")) %>%
    filter(!is.na(ponderador_final) & !is.na(conglomerado_unico) & !is.na(N_provincia))

tamanio_muestral_provincia_total <- df_analisis_total %>%
    group_by(provincia) %>%
    summarise(n_provincia = n()) %>%
    ungroup()

df_analisis_total <- df_analisis_total %>%
    left_join(tamanio_muestral_provincia_total, by = "provincia")

encuesta_dsn_total <- svydesign(
    ids = ~conglomerado_unico,
    strata = ~provincia,
    weights = ~ponderador_final,
    data = df_analisis_total,
    fpc = ~N_provincia
)


# 4.2. Cálculo del Análisis (Proporción de Voto)
votara_resultado <- svymean(~votara, design = encuesta_dsn_total, na.rm = TRUE)
partido_preferente_resultado <- svymean(~partido_preferente, design = encuesta_dsn_total, na.rm = TRUE)
presidente_resultado <- svymean(~voto_presidente, design = encuesta_dsn, na.rm = TRUE)
diputado_resultado <- svymean(~voto_diputado, design = encuesta_dsn, na.rm = TRUE)


cat("\n
======================================================\n
         RESULTADOS FINALES DIPUTADOS      \n
======================================================\n
Estimación Ponderada del Voto a Diputados (diputado_resultado):\n")
print(diputado_resultado)
cat("======================================================\n")

cat("\n
======================================================\n
         RESULTADOS FINALES PRESIDENTE     \n
======================================================\n
Estimación Ponderada del Voto Presidencial (presidente_resultado):\n")
print(presidente_resultado)
cat("======================================================\n")

cat("\n
======================================================\n
       RESULTADOS FINALES PARTIDO PREFERENTE \n
======================================================\n
Estimación Ponderada de Partido Preferente (partido_preferente_resultado):\n")
print(partido_preferente_resultado)
cat("======================================================\n")


