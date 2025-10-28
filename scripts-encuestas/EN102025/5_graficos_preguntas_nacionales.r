
# ==============================================================================
# GRÁFICO: PARTIDO VOTO PRESIDENCIAL (Base Votantes Válidos)
# ==============================================================================

library(ggplot2)
library(dplyr)
library(forcats)


library(dplyr)
library(knitr)
library(tibble)

presidente_resultado_df <- as.data.frame(presidente_resultado)

resultados_formateados <- presidente_resultado_df %>%
    rownames_to_column(var = "Candidato") %>%
    rename(Proporcion = mean, Error_Estandar = SE) %>%
    mutate(Candidato = gsub("^voto_presidente", "", Candidato)) %>%
    mutate(
        ME_individual = Error_Estandar * 1.96,
        Voto_pct = round(Proporcion * 100, 2),
        ME_pct = round(ME_individual * 100, 2)
    ) %>%
    select(
        Candidato, 
        `Voto (%)` = Voto_pct, 
        `Margen de Error Individual (±%)` = ME_pct, 
        `Error Estándar (SE)` = Error_Estandar
    ) %>%
    arrange(desc(`Voto (%)`))

kable(resultados_formateados, 
      caption = "Estimación Ponderada del Voto Presidencial (95% C.I.)")
# 1. Definir las categorías especiales (Corregido para eliminar la advertencia anterior)
categorias_especiales_limpias <- c(
    "No Sabe", "NS/NR", "Nulo", "No Responde", "En blanco"
)


# 2. Filtrar y reordenar candidatos
resultados_candidatos <- resultados_formateados %>%
    # 2.1. Separar los candidatos (los que NO son categorías especiales)
    mutate(tipo = ifelse(Candidato %in% categorias_especiales_limpias, "No Candidato", "Candidato")) %>%
    
    # 2.2. Reordenar: Primero, los candidatos se ordenan por Voto (%) de mayor a menor.
    mutate(Candidato = fct_reorder(Candidato, `Voto (%)`, .fun = sum, .desc = FALSE)) %>%
    
    # 2.3. Mover las categorías especiales al inicio para luego enviarlas al final con coord_flip().
    mutate(Candidato = fct_relevel(Candidato, categorias_especiales_limpias))


# 3. Generar el gráfico (Se mantiene igual, ya que el orden se maneja en el paso 2)
grafico_voto_mejorado <- ggplot(resultados_candidatos, 
                               aes(x = Candidato, y = `Voto (%)`)) +
    
    # A. BARRAS DE VOTO
    geom_col(aes(fill = tipo), width = 0.8) + # Usar 'tipo' para diferenciar color
    
    # B. ETIQUETAS DE VALOR 
    geom_text(aes(label = paste0(`Voto (%)`, "%")), 
              hjust = -0.1, size = 4, 
              color = "black", fontface = "bold") + 
    
    # C. ESCALA DE COLORES (Opcional: Colorea diferente los "No Candidatos")
    scale_fill_manual(values = c("Candidato" = "#1d1c49", "No Candidato" = "#D45A26")) +
    
    # 4. Formato y etiquetas
    labs(
        title = "Intención de Voto Presidencial",
        subtitle = "Encuesta Nacional OPOL Octubre 2025",
        x = NULL, 
        y = "Porcentaje de Voto (%)",
        fill = "Tipo de Voto" # Título de la leyenda
    ) +
    
    # 5. Voltear las coordenadas
    coord_flip() +
    
    # 6. Ajuste del eje X
    scale_y_continuous(limits = c(0, max(resultados_candidatos$`Voto (%)`) * 1.15)) +
    
    # 7. Tema limpio
    theme_minimal() +
    theme(legend.position = "bottom")

# Mostrar el gráfico
print(grafico_voto_mejorado)


# ==============================================================================
# 1. GRÁFICO: PARTIDO PREFERENTE (Base Votantes Válidos)
# ==============================================================================

library(dplyr)
library(ggplot2)
library(forcats)
library(tibble)

# 1.1. Formatear los resultados de la estimación (svymean)
partido_preferente_df <- as.data.frame(partido_preferente_resultado)

resultados_partido <- partido_preferente_df %>%
    rownames_to_column(var = "Partido") %>%
    rename(Proporcion = mean) %>%
    mutate(Partido = gsub("^partido_preferente", "", Partido)) %>%
    mutate(`Voto (%)` = round(Proporcion * 100, 2)) %>%
    select(Partido, `Voto (%)`)

# 1.2. Reordenar y clasificar (Similar al voto presidencial)
categorias_especiales_partido <- c("No Responde", "Ninguno", "NS/NR", "No Sabe")

resultados_partido <- resultados_partido %>%
    mutate(tipo = ifelse(Partido %in% categorias_especiales_partido, "No Identificado", "Identificado")) %>%
    mutate(Partido = fct_reorder(Partido, `Voto (%)`, .fun = sum, .desc = FALSE)) %>%
    mutate(Partido = fct_relevel(Partido, categorias_especiales_partido))


# 1.3. Generar el Gráfico
grafico_partido_preferente <- ggplot(resultados_partido, 
                                     aes(x = Partido, y = `Voto (%)`)) +
    geom_col(aes(fill = tipo), width = 0.8) +
    geom_text(aes(label = paste0(`Voto (%)`, "%")), 
              hjust = -0.1, size = 4, color = "black", fontface = "bold") +
    scale_fill_manual(values = c("Identificado" = "#1d1c49", "No Identificado" = "#D45A26")) +
    labs(
        title = "Preferencia o Identificación con Partido Político",
        subtitle = "Encuesta Nacional OPOL Octubre 2025",
        x = NULL, y = "Porcentaje (%)", fill = "Clasificación"
    ) +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(resultados_partido$`Voto (%)`) * 1.15)) +
    theme_minimal() +
    theme(legend.position = "bottom")

print(grafico_partido_preferente)

# ==============================================================================
# 2. GRÁFICO: VOTO DIPUTADO (Base Votantes Válidos)
# ==============================================================================

# 2.1. Formatear los resultados de la estimación (svymean)
voto_diputado_df <- as.data.frame(diputado_resultado)

resultados_diputado <- voto_diputado_df %>%
    rownames_to_column(var = "Partido") %>%
    rename(Proporcion = mean) %>%
    mutate(Partido = gsub("^voto_diputado", "", Partido)) %>%
    mutate(`Voto (%)` = round(Proporcion * 100, 2)) %>%
    select(Partido, `Voto (%)`)

# 2.2. Reordenar y clasificar
categorias_especiales_diputado <- c("Nulo", "En Blanco", "No Sabe", "No Responde", "NS/NR")

resultados_diputado <- resultados_diputado %>%
    mutate(tipo = ifelse(Partido %in% categorias_especiales_diputado, "Voto No Válido/Indeciso", "Intención Partidaria")) %>%
    mutate(Partido = fct_reorder(Partido, `Voto (%)`, .fun = sum, .desc = FALSE)) %>%
    mutate(Partido = fct_relevel(Partido, categorias_especiales_diputado))


# 2.3. Generar el Gráfico
grafico_voto_diputado <- ggplot(resultados_diputado, 
                                aes(x = Partido, y = `Voto (%)`)) +
    geom_col(aes(fill = tipo), width = 0.8) +
    geom_text(aes(label = paste0(`Voto (%)`, "%")), 
              hjust = -0.1, size = 4, color = "black", fontface = "bold") +
    scale_fill_manual(values = c("Intención Partidaria" = "#1d1c49", "Voto No Válido/Indeciso" = "#D45A26")) +
    labs(
        title = "Intención de Voto para Diputados",
        subtitle = "Encuesta Nacional OPOL Octubre 2025",
        x = NULL, y = "Porcentaje de Voto (%)", fill = "Clasificación"
    ) +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(resultados_diputado$`Voto (%)`) * 1.15)) +
    theme_minimal() +
    theme(legend.position = "bottom")

print(grafico_voto_diputado)


# ==============================================================================
# 3. GRÁFICO: VOTARÁ (Base Encuestas Válidas Totales)
# ==============================================================================

# 3.1. Formatear los resultados de la estimación (svymean)
votara_df <- as.data.frame(votara_resultado)

resultados_votara <- votara_df %>%
    rownames_to_column(var = "Respuesta") %>%
    rename(Proporcion = mean) %>%
    mutate(Respuesta = gsub("^votara", "", Respuesta)) %>%
    mutate(`Voto (%)` = round(Proporcion * 100, 2)) %>%
    select(Respuesta, `Voto (%)`)

# 3.2. Reordenar (Aquí no hay categorías especiales, solo ordenamos para mejor visualización)
resultados_votara <- resultados_votara %>%
    mutate(tipo = ifelse(Respuesta == "Sí", "Votará", "No Votará / No Responde")) %>%
    # Ordenar Sí, No, No Responde
    mutate(Respuesta = fct_relevel(Respuesta, "No Responde", "No", "Sí")) 


# 3.3. Generar el Gráfico
grafico_votara <- ggplot(resultados_votara, 
                         aes(x = Respuesta, y = `Voto (%)`)) +
    geom_col(aes(fill = tipo), width = 0.8) +
    geom_text(aes(label = paste0(`Voto (%)`, "%")), 
              hjust = -0.1, size = 5, color = "black", fontface = "bold") +
    scale_fill_manual(values = c("Votará" = "#1d1c49", "No Votará / No Responde" = "#D45A26")) +
    labs(
        title = "¿Usted votará en las próximas elecciones?",
        subtitle = "Encuesta Nacional OPOL Octubre 2025",
        x = NULL, y = "Porcentaje (%)", fill = NULL
    ) +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(resultados_votara$`Voto (%)`) * 1.1)) +
    theme_minimal() +
    theme(legend.position = "none")

print(grafico_votara)


# ==============================================================================
# 5. GRÁFICO: DISTRIBUCIÓN DE RELIGIÓN (Base Encuestas Válidas Totales)
# ==============================================================================


# 2. Cálculo de la Estimación Ponderada para 'religion'
religion_resultado <- svymean(~religion, design = encuesta_dsn_total, na.rm = TRUE)

# 3. Formatear los resultados
religion_df <- as.data.frame(religion_resultado)

resultados_religion <- religion_df %>%
    rownames_to_column(var = "Religion") %>%
    rename(Proporcion = mean) %>%
    mutate(Religion = gsub("^religion", "", Religion)) %>%
    mutate(`Porcentaje (%)` = round(Proporcion * 100, 2)) %>%
    select(Religion, `Porcentaje (%)`)

# 4. Reordenar y clasificar
resultados_religion <- resultados_religion %>%
    mutate(tipo = ifelse(Religion %in% c("No Responde", "Otro"), "Otras/No Definido", "Mayorías")) %>%
    # Ordenar por Porcentaje de mayor a menor
    mutate(Religion = fct_reorder(Religion, `Porcentaje (%)`, .fun = sum, .desc = FALSE)) 


# 5. Generar el Gráfico
grafico_religion <- ggplot(resultados_religion, 
                           aes(x = Religion, y = `Porcentaje (%)`)) +
    geom_col(aes(fill = tipo), width = 0.8) +
    geom_text(aes(label = paste0(`Porcentaje (%)`, "%")), 
              hjust = -0.1, size = 4, color = "black", fontface = "bold") +
    scale_fill_manual(values = c("Mayorías" = "#1d1c49", "Otras/No Definido" = "#D45A26")) +
    labs(
        title = "Distribución Ponderada por Religión",
        subtitle = "Base: Total Encuestas Válidas (Ponderado)",
        x = NULL, y = "Porcentaje (%)", fill = NULL
    ) +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(resultados_religion$`Porcentaje (%)`) * 1.15)) +
    theme_minimal() +
    theme(legend.position = "bottom")

print(grafico_religion)

# ==============================================================================
# 6. GRÁFICO: DISTRIBUCIÓN DE EDUCACIÓN (Base Encuestas Válidas Totales)
# ==============================================================================

library(ggplot2)
library(dplyr)
library(forcats)
library(tibble)
library(survey) # Aseguramos que survey esté cargado

# NOTA: Asumimos que 'df_analisis_total' y 'encuesta_dsn_total' del paso anterior
# (el que usó la base total para calcular la religión) están disponibles.

# 1. Cálculo de la Estimación Ponderada para 'educacion'
educacion_resultado <- svymean(~educacion, design = encuesta_dsn_total, na.rm = TRUE)

# 2. Formatear los resultados
educacion_df <- as.data.frame(educacion_resultado)

resultados_educacion <- educacion_df %>%
    rownames_to_column(var = "Nivel_Educacion") %>%
    rename(Proporcion = mean) %>%
    # Eliminar el prefijo de la variable
    mutate(Nivel_Educacion = gsub("^educacion", "", Nivel_Educacion)) %>%
    mutate(`Porcentaje (%)` = round(Proporcion * 100, 2)) %>%
    select(Nivel_Educacion, `Porcentaje (%)`)

# 3. Reordenar y clasificar
# Se ordenarán por porcentaje, y se marcarán categorías especiales como 'No Responde'
categorias_especiales_edu <- c("No Responde", "NS/NR")

resultados_educacion <- resultados_educacion %>%
    mutate(tipo = ifelse(Nivel_Educacion %in% categorias_especiales_edu, "No Definido", "Definido")) %>%
    # Ordenar por Porcentaje de menor a mayor
    mutate(Nivel_Educacion = fct_reorder(Nivel_Educacion, `Porcentaje (%)`, .fun = sum, .desc = FALSE)) %>%
    # Mover las categorías especiales al inicio para que queden al final en el gráfico horizontal
    mutate(Nivel_Educacion = fct_relevel(Nivel_Educacion, categorias_especiales_edu))


# 4. Generar el Gráfico
grafico_educacion <- ggplot(resultados_educacion, 
                           aes(x = Nivel_Educacion, y = `Porcentaje (%)`)) +
    geom_col(aes(fill = tipo), width = 0.8) +
    geom_text(aes(label = paste0(`Porcentaje (%)`, "%")), 
              hjust = -0.1, size = 4, color = "black", fontface = "bold") +
    # Usando los colores consistentes: Definido (#1d1c49), No Definido (#D45A26)
    scale_fill_manual(values = c("Definido" = "#1d1c49", "No Definido" = "#D45A26")) +
    labs(
        title = "Distribución Ponderada por Nivel de Educación",
        subtitle = "Base: Total Encuestas Válidas (Ponderado)",
        x = NULL, y = "Porcentaje (%)", fill = NULL
    ) +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(resultados_educacion$`Porcentaje (%)`) * 1.15)) +
    theme_minimal() +
    theme(legend.position = "none")

print(grafico_educacion)
