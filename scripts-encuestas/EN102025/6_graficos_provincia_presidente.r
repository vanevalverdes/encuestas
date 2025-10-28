# ==============================================================================
# 1. GRÁFICO: INTENCIÓN DE VOTO POR PROVINCIA Y SEXO (Base Votantes Válidos)
# ==============================================================================

library(tidyr) 
library(ggplot2) 
library(dplyr) # Aseguramos la carga de dplyr para la manipulación de datos
# NOTA: Este código usa 'encuesta_dsn', 'df_analisis_nacional' y 'resultados_formateados' 
# definidos en su script global previo.

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
    mutate(sexo = "Total") # Añadir columna para distinguirlo

# 1.3. Combinar los resultados de sexo desagregado y total
svy_combined <- bind_rows(svy_sex_provincia, svy_provincia_total)

# 2. LIMPIEZA Y FORMATO
# ----------------------

# 2.1. Convertir a formato largo y limpiar nombres
resultados_long <- svy_combined %>%
    # Eliminar errores estándar para el gráfico (se.)
    select(-starts_with("se.")) %>% 
    # Transformar a formato largo para el gráfico (una fila por candidato)
    pivot_longer(cols = starts_with("voto_presidente"),
                 names_to = "Candidato_raw",
                 values_to = "Proporcion") %>%
    mutate(Candidato = gsub("^voto_presidente", "", Candidato_raw)) %>%
    mutate(`Voto (%)` = round(Proporcion * 100, 2)) %>%
    filter(!is.na(`Voto (%)`)) 

# 2.2. Filtrar solo los candidatos principales + No Responde/Nulo (para claridad visual)
# Nota: Asumimos que 'resultados_formateados' existe en el entorno global
candidatos_a_mostrar <- resultados_formateados %>% 
    filter(!Candidato %in% c(" No Responde", " Nulo", " En blanco", " No Sabe", " NS/NR")) %>%
    head(7) %>%
    pull(Candidato)

categorias_especiales_a_mostrar <- c(" No Responde", " Nulo")
candidatos_finales <- c(candidatos_a_mostrar, categorias_especiales_a_mostrar)

resultados_filtrados <- resultados_long %>%
    filter(Candidato %in% candidatos_finales) %>%
    # Ordenar el Sexo para que 'Total' quede al final en la leyenda
    mutate(sexo = factor(sexo, levels = c("H", "M", "Total"))) %>%
    # Asegurar el orden de los candidatos en el eje X
    mutate(Candidato = factor(Candidato, levels = candidatos_finales)) %>%
    arrange(provincia, sexo, desc(`Voto (%)`))

# 3. GENERACIÓN DE MÚLTIPLES GRÁFICOS (Uno por Provincia)
# -------------------------------------------------------

# Obtener la lista única de provincias a iterar
provincias_unicas <- unique(resultados_filtrados$provincia)

# Colores consistentes
colores_segmento <- c("H" = "#1d1c49", "M" = "#056085ff", "Total" = "#D45A26")

# Generar y mostrar un gráfico para cada provincia
lista_de_graficos <- list()

for (p in provincias_unicas) {
    
    # Filtrar los datos para la provincia actual
    data_provincia <- resultados_filtrados %>% filter(provincia == p)
    
    # Crear el gráfico
    grafico <- ggplot(data_provincia, 
                      aes(x = Candidato, y = `Voto (%)`, fill = sexo)) +
        
        # Barras agrupadas (dodged)
        geom_col(position = position_dodge(width = 0.8), width = 0.7) +
        
        # Etiquetas de valor
        geom_text(aes(label = paste0(`Voto (%)`, "%")), 
                  position = position_dodge(width = 0.8), 
                  vjust = -0.5, 
                  size = 3,
                  fontface = "bold") +
        
        # Colores
        scale_fill_manual(values = colores_segmento) +
        
        # Formato y etiquetas específicos para la provincia
        labs(
            title = paste0("Intención de Voto Presidencial en ", p),
            subtitle = "Base: Votantes Válidos (Ponderado). Segmentado por Sexo.",
            x = "Candidato", 
            y = "Porcentaje de Voto (%)",
            fill = "Segmento"
        ) +
        
        # Ajustar límite del eje Y para que quepan las etiquetas
        scale_y_continuous(expand = expansion(mult = c(0, 0.15))) + 
        theme_minimal() +
        theme(axis.text.x = element_text(angle = 45, hjust = 1),
              legend.position = "bottom",
              plot.title = element_text(face = "bold", size = 14),
              plot.subtitle = element_text(size = 10, color = "gray50"))
    
    # Imprimir el gráfico (o guardar en una lista si se necesita más tarde)
    print(grafico)
    
    # Opcional: Almacenar en una lista si el entorno lo soporta
    lista_de_graficos[[p]] <- grafico
}

# La variable 'lista_de_graficos' ahora contiene un gráfico para cada provincia.
