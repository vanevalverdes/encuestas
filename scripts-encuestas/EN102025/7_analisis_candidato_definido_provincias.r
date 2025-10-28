# ==============================================================================
# 1. GRÁFICO: INTENCIÓN DE VOTO POR PROVINCIA Y SEXO (BASE VOTOS VÁLIDOS)
# ==============================================================================

library(tidyr) 
library(ggplot2) 
library(dplyr) 

# 1. CÁLCULO DE PROPORCIONES PONDERADAS (svymean)
# ------------------------------------------------

# 1.1. Calcular la estimación por PROVINCIA y SEXO
svy_sex_provincia <- svyby(~voto_presidente, 
                           by = ~provincia + sexo, 
                           design = encuesta_dsn, 
                           FUN = svymean, 
                           na.rm = TRUE)

# 1.2. Calcular la estimación por PROVINCIA (Total agregado por sexo)
svy_provincia_total <- svyby(~voto_presidente, 
                             by = ~provincia, 
                             design = encuesta_dsn, 
                             FUN = svymean, 
                             na.rm = TRUE) %>%
    mutate(sexo = "Total") 

# 1.3. Combinar los resultados de sexo desagregado y total
svy_combined <- bind_rows(svy_sex_provincia, svy_provincia_total)

# 2. LIMPIEZA Y CÁLCULO SOBRE VOTOS VÁLIDOS
# ------------------------------------------

# 2.1. Convertir a formato largo, limpiar nombres y obtener la Proporción Bruta
resultados_long <- svy_combined %>%
    select(-starts_with("se.")) %>% 
    pivot_longer(cols = starts_with("voto_presidente"),
                 names_to = "Candidato_raw",
                 values_to = "Proporcion") %>%
    mutate(Candidato = gsub("^voto_presidente", "", Candidato_raw)) %>%
    filter(!is.na(Proporcion)) 

# 2.2. Definir las categorías que DEBEN ser excluidas del cálculo de la base
categorias_no_validas <- c("No Responde", "Nulo", "En blanco", "No Sabe", "NS/NR") # Agregué NS/NR para ser exhaustivo

# 2.3. CALCULAR EL VOTO VÁLIDO Y EL NUEVO PORCENTAJE

resultados_validos <- resultados_long %>%
    # A. Clasificar si es voto válido o no
    mutate(es_valido = !Candidato %in% categorias_no_validas) %>%
    
    # B. Agrupar por segmento (Provincia y Sexo)
    group_by(provincia, sexo) %>%
    
    # C. Calcular la SUMA de las proporciones de SOLO los candidatos válidos (Base Válida)
    mutate(Suma_Proporcion_Valida = sum(Proporcion[es_valido])) %>%
    
    # D. Recalcular el porcentaje sobre la nueva base
    mutate(
        # Si el candidato es válido, se recalcula el porcentaje
        `Voto (%) Válido` = if_else(es_valido, 
                                    (Proporcion / Suma_Proporcion_Valida) * 100, 
                                    0.00),
        # Si NO es válido, el porcentaje sobre la base válida es 0. 
        # Si quieres mostrar el valor de la proporción bruta, podrías usar otra columna.
        `Voto (%) Válido` = round(`Voto (%) Válido`, 2)
    ) %>%
    ungroup() %>%
    
    # E. Filtrar para quedarnos SOLO con los votos válidos y el 0% para las categorías inválidas
    filter(es_valido) # Mantenemos solo los candidatos con voto válido.

# 3. EXPORTAR A CSV (usando los nuevos porcentajes)
# ------------------------------------------------
nombre_archivo <- "intencion_voto_provincia_sexo_votos_validos.csv"

# Seleccionamos y renombrar las columnas finales para el CSV
resultados_csv_final <- resultados_validos %>%
    select(
        Candidato = Candidato,
        Segmento = sexo,
        provincia,
        Porcentaje_Voto_Valido = `Voto (%) Válido` # Usamos el nuevo porcentaje
    )

write.csv(resultados_csv_final, nombre_archivo, row.names = FALSE)

cat(paste0("\n✅ ¡Exportación completada! El archivo con el porcentaje sobre la base de VOTOS VÁLIDOS ha sido guardado como:\n", nombre_archivo, "\n"))


# 4. GENERACIÓN DEL GRÁFICO (Barras Agrupadas y Facetadas)
# --------------------------------------------------------

# 4.1. Filtrar solo el top 5 global de candidatos válidos
candidatos_a_mostrar <- resultados_formateados %>%
    filter(!Candidato %in% categorias_no_validas) %>% # Usamos la lista de no válidos para el filtro
    arrange(desc(`Voto (%)`)) %>%
    head(5) %>%
    pull(Candidato)

resultados_grafico <- resultados_validos %>%
    filter(Candidato %in% candidatos_a_mostrar) %>%
    # Ordenar el Sexo para que 'Total' quede al final en la leyenda
    mutate(sexo = factor(sexo, levels = c("H", "M", "Total"))) %>%
    # Reordenar candidatos en el gráfico
    mutate(Candidato = fct_reorder(Candidato, `Voto (%) Válido`, .fun = mean, .desc = FALSE)) 
    
grafico_voto_provincia_sexo_valido <- ggplot(resultados_grafico, 
                                       aes(x = Candidato, y = `Voto (%) Válido`, fill = sexo)) +
    # Barras agrupadas (dodged)
    geom_col(position = position_dodge(width = 0.8), width = 0.7) +
    # Etiquetas de valor
    geom_text(aes(label = paste0(`Voto (%) Válido`, "%")), 
              position = position_dodge(width = 0.8), 
              vjust = -0.5, 
              size = 3,
              fontface = "bold") +
    
    # Facetas por Provincia
    facet_wrap(~ provincia, scales = "free_y", ncol = 2) +
    
    # Colores consistentes para Hombres, Mujeres, Total
    scale_fill_manual(values = c("H" = "#007bff", "M" = "#dc3545", "Total" = "#343a40")) +
    
    # Formato y etiquetas
    labs(
        title = "Intención de Voto Presidencial por Provincia y Sexo (Voto Válido)",
        subtitle = "Base: Votos con Candidato Definido (Ponderado). Muestra top 5 candidatos.",
        x = "Candidato", 
        y = "Porcentaje de Voto Válido (%)",
        fill = "Segmento"
    ) +
    # Voltear coordenadas para que los nombres de los candidatos se vean mejor
    coord_flip() +
    # Ajustar límite del eje X
    scale_y_continuous(expand = expansion(mult = c(0, 0.20))) + 
    theme_minimal() +
    theme(legend.position = "bottom",
          plot.title = element_text(face = "bold"))

# Mostrar el gráfico
print(grafico_voto_provincia_sexo_valido)

# ==============================================================================
# 2. EXPORTACIÓN CSV: VOTO PRESIDENCIAL POR PROVINCIA Y SEXO (VOTOS VÁLIDOS)
# ==============================================================================

# NOTA: Utilizamos el dataframe 'resultados_validos' previamente calculado,
# que ya está filtrado para contener SOLO los candidatos válidos (es_valido = TRUE)
# y cuyo porcentaje ('Voto (%) Válido') suma 100% dentro de cada segmento (Provincia x Sexo).

# 1. Preparar el dataframe para la exportación
resultados_csv_voto_valido <- resultados_validos %>%
    # Seleccionamos y renombrar las columnas finales para el CSV
    select(
        Provincia = provincia,
        Segmento = sexo,
        Candidato = Candidato,
        # Esta columna es el resultado clave: porcentaje sobre los que tienen candidato definido
        Porcentaje_Voto_Valido = `Voto (%) Válido`
    ) %>%
    # Ordenar para fácil lectura
    arrange(Provincia, Segmento, desc(Porcentaje_Voto_Valido))


# 2. EXPORTAR A CSV
# -----------------
# Define un nombre de archivo claro
nombre_archivo_voto_valido <- "intencion_voto_provincia_sexo_votos_validos_final.csv"

# Se usa write.csv con coma (,) como separador por defecto
write.csv(resultados_csv_voto_valido, nombre_archivo_voto_valido, row.names = FALSE)


cat(paste0("\n✅ ¡Exportación completada! El archivo con el porcentaje sobre la base de VOTOS VÁLIDOS (solo candidato definido) ha sido guardado como:\n", nombre_archivo_voto_valido, "\n"))