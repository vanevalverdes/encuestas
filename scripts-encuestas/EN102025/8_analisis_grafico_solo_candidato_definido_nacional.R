# ==============================================================================
# 1. CÁLCULO Y EXPORTACIÓN: VOTO VÁLIDO NACIONAL (POR SEXO)
# ==============================================================================

library(tidyr) 
library(dplyr) 
library(survey) 

# NOTA: Este código asume que 'encuesta_dsn' (el diseño para la base votantes válidos)
# y las librerías necesarias ya están cargadas.

# 1. CÁLCULO DE PROPORCIONES PONDERADAS NACIONALES
# ------------------------------------------------

# 1.1. Calcular la estimación por SEXO a nivel nacional (Hombres, Mujeres)
svy_sex_nacional <- svyby(~voto_presidente, 
                          by = ~sexo, 
                          design = encuesta_dsn, 
                          FUN = svymean, 
                          na.rm = TRUE)

# 1.2. Calcular la estimación NACIONAL TOTAL (sin desagregación por sexo)
svy_nacional_total <- as.data.frame(svymean(~voto_presidente, 
                                            design = encuesta_dsn, 
                                            na.rm = TRUE)) %>%
    rownames_to_column(var = "Candidato_raw") %>%
    rename(Proporcion = mean, SE = SE) %>%
    # Convertir a formato ancho y añadir el segmento 'sexo' = 'Nacional'
    pivot_wider(names_from = Candidato_raw, values_from = c(Proporcion, SE)) %>%
    mutate(sexo = "Nacional") %>%
    # Alinear los nombres de columna para el merge, quitando el prefijo 'Proporcion_' y 'SE_'
    rename_with(~ sub("Proporcion_", "", .x), starts_with("Proporcion_")) %>%
    rename_with(~ sub("SE_", "se.", .x), starts_with("SE_")) %>%
    # Seleccionar solo las columnas necesarias para el bind_rows
    select(sexo, starts_with("voto_presidente"), starts_with("se.voto_presidente"))

# 1.3. Alinear y Combinar H/M con el Total Nacional
svy_combined_nacional <- bind_rows(svy_sex_nacional, svy_nacional_total)


# 2. LIMPIEZA Y CÁLCULO SOBRE VOTOS VÁLIDOS A NIVEL NACIONAL
# ----------------------------------------------------------

# 2.1. Convertir a formato largo y limpiar nombres
resultados_nacional_long <- svy_combined_nacional %>%
    select(sexo, starts_with("voto_presidente")) %>% # Solo las proporciones (mean)
    pivot_longer(cols = starts_with("voto_presidente"),
                 names_to = "Candidato_raw",
                 values_to = "Proporcion") %>%
    mutate(Candidato = gsub("^voto_presidente", "", Candidato_raw)) %>%
    filter(!is.na(Proporcion)) 

# 2.2. Definir las categorías a excluir
categorias_no_validas <- c("No Responde", "Nulo", "En blanco", "No Sabe", "NS/NR")

# 2.3. CALCULAR EL VOTO VÁLIDO Y EL NUEVO PORCENTAJE

resultados_nacional_validos <- resultados_nacional_long %>%
    # A. Clasificar si es voto válido o no
    mutate(es_valido = !Candidato %in% categorias_no_validas) %>%
    
    # B. Agrupar por segmento (solo Sexo: H/M/Nacional)
    group_by(sexo) %>%
    
    # C. Calcular la SUMA de las proporciones de SOLO los candidatos válidos (Base Válida)
    mutate(Suma_Proporcion_Valida = sum(Proporcion[es_valido])) %>%
    
    # D. Recalcular el porcentaje sobre la nueva base
    mutate(
        `Porcentaje_Voto_Valido` = if_else(es_valido, 
                                    (Proporcion / Suma_Proporcion_Valida) * 100, 
                                    0.00),
        `Porcentaje_Voto_Valido` = round(`Porcentaje_Voto_Valido`, 2)
    ) %>%
    ungroup() %>%
    
    # E. Filtrar para quedarnos SOLO con los votos válidos
    filter(es_valido) 

# 3. EXPORTAR A CSV
# -----------------

# 3.1. Preparar el dataframe para la exportación
resultados_csv_nacional_voto_valido <- resultados_nacional_validos %>%
    select(
        Segmento = sexo,
        Candidato = Candidato,
        Porcentaje_Voto_Valido = Porcentaje_Voto_Valido
    ) %>%
    # Ordenar para fácil lectura: Nacional al inicio, luego H, M, y por porcentaje descendente
    mutate(Segmento = factor(Segmento, levels = c("Nacional", "H", "M"))) %>%
    arrange(Segmento, desc(Porcentaje_Voto_Valido))


# 3.2. EXPORTAR A CSV
nombre_archivo_nacional_voto_valido <- "intencion_voto_nacional_votos_validos_por_sexo.csv"

# Se usa write.csv con coma (,) como separador por defecto
write.csv(resultados_csv_nacional_voto_valido, nombre_archivo_nacional_voto_valido, row.names = FALSE)


cat(paste0("\n✅ ¡Exportación completada! El archivo con el porcentaje sobre la base de VOTOS VÁLIDOS consolidado a nivel NACIONAL (desagregado por sexo) ha sido guardado como:\n", nombre_archivo_nacional_voto_valido, "\n"))

# ==============================================================================
# 1. GRÁFICO: INTENCIÓN DE VOTO VÁLIDO CONSOLIDADO NACIONAL (Solo Total)
# ==============================================================================

library(ggplot2)
library(dplyr)
library(forcats)

# NOTA: Este código asume que 'resultados_nacional_validos' ya fue generado 
# y contiene la columna 'Porcentaje_Voto_Valido' ajustada sobre la base válida.

# 1. Preparar y Filtrar datos para el gráfico (SOLO NACIONAL)
# ------------------------------------------------------------
resultados_grafico_nacional_total <- resultados_nacional_validos %>%
    # Filtrar solo la línea consolidada
    filter(sexo == "Nacional") %>%
    
    # Reordenar el eje X (Candidatos) por el porcentaje de voto nacional (descendente)
    mutate(Candidato = fct_reorder(Candidato, 
                                   Porcentaje_Voto_Valido, 
                                   .fun = mean, 
                                   .desc = FALSE))

# 2. Generar el gráfico
# ----------------------
grafico_voto_valido_nacional_total <- ggplot(resultados_grafico_nacional_total, 
                                           aes(x = Candidato, y = Porcentaje_Voto_Valido)) +
    
    # A. Barras (color base oscuro)
    geom_col(fill = "#1d1c49", width = 0.7) +
    
    # B. Etiquetas de valor (Porcentaje)
    geom_text(aes(label = paste0(Porcentaje_Voto_Valido, "%")), 
              hjust = -0.1, # Ajuste para que queden fuera de la barra
              size = 4,
              fontface = "bold") +
    
    # C. Formato y etiquetas
    labs(
        title = "Intención de Voto Presidencial (Voto Válido) Nacional",
        subtitle = "Base: Decididos a votar con candidato definido. (Excluye indecisos y votos no válidos).",
        x = NULL, 
        y = "Porcentaje de Voto Válido (%)"
    ) +
    
    # D. Voltear coordenadas para una mejor lectura de los nombres
    coord_flip() +
    
    # E. Ajustar límite del eje Y
    scale_y_continuous(expand = expansion(mult = c(0, 0.20))) + 
    theme_minimal() +
    theme(plot.title = element_text(face = "bold", hjust = 0),
          plot.subtitle = element_text(hjust = 0),
          # Eliminar el eje X si solo son etiquetas de valor
          axis.text.x = element_blank(),
          axis.ticks.x = element_blank())

# Mostrar el gráfico
print(grafico_voto_valido_nacional_total)