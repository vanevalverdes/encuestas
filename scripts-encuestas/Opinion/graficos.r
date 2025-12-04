# ==============================================================================
# 10. GENERACIÓN DE GRÁFICOS (FORMULARIO V1)
# ==============================================================================

library(ggplot2)
library(dplyr)
library(forcats)
library(scales)
library(stringi)

# CARPETA DE SALIDA (Asegúrate de crearla o cambiar la ruta)
DIR_GRAFICOS <- "C:\\Users\\vanev\\Documents\\Opol\\Encuesta de Opinion\\Graficos"
dir.create(DIR_GRAFICOS, showWarnings = FALSE, recursive = TRUE)

# COLORES CORPORATIVOS
COLOR_PRINCIPAL <- "#1d1c49"  # Azul oscuro
COLOR_SECUNDARIO <- "#D45A26" # Naranja
COLOR_NEUTRO <- "#808080"     # Gris

# -----------------------------------------------------------------------------
# FUNCIÓN MAESTRA PARA GRÁFICOS DE BARRAS SIMPLES
# -----------------------------------------------------------------------------
plot_barras_simple <- function(variable, disenio, titulo, subtitulo, nombre_archivo) {
  
  # === 1. DEFINICIÓN DE LÓGICA DE ORDENAMIENTO ===
  # Usamos el nombre limpio de la variable sin "factor()"
  var_limpia <- gsub("factor\\(|\\)", "", variable)
  
  # Bandera para saber si es la calificación Q2
  es_calificacion_q2 <- (var_limpia == "q2_calif_chaves")
  
  # === 2. CÁLCULO PONDERADO ===
  formula <- as.formula(paste0("~", variable))
  res <- svymean(formula, design = disenio, na.rm = TRUE)
  
  # === 3. CONVERTIR Y LIMPIAR DATAFRAME ===
  df_plot <- as.data.frame(res) %>%
    rownames_to_column("Respuesta") %>%
    rename(Proporcion = mean) %>%
    mutate(
      # Limpieza robusta (maneja el caso de factor() o solo la variable)
      Respuesta = stringr::str_remove(Respuesta, paste0("factor\\(", var_limpia, "\\)")),
      Respuesta = stringr::str_remove(Respuesta, var_limpia),
      Respuesta = stringr::str_trim(Respuesta), 
      Porcentaje = round(Proporcion * 100, 1)
    )
  
  # === 4. ORDENAMIENTO CONDICIONAL ===
  if (es_calificacion_q2) {
    # CASO ESPECIAL: Q2 (Calificación 1 a 10)
    df_plot <- df_plot %>%
      mutate(
        # Convertir a numérico para hallar min/max y forzar el orden 1, 2, 3...
        Respuesta_Ordenada = factor(Respuesta, 
                                    levels = min(as.numeric(Respuesta), na.rm = TRUE):max(as.numeric(Respuesta), na.rm = TRUE), 
                                    ordered = TRUE)
      )
    eje_x_plot <- "Respuesta_Ordenada" # Usar la columna ordenada 1-10
    
  } else {
    # CASO GENERAL: Voto, Apoyo, Sí/No (Ordenar por Frecuencia: Mayor a Menor)
    df_plot <- df_plot %>%
      mutate(
        # fct_reorder ordena el factor Respuesta en base al valor de Porcentaje
        Respuesta_Ordenada = fct_reorder(Respuesta, Porcentaje, .fun=sum, .desc = FALSE)
      )
    eje_x_plot <- "Respuesta_Ordenada" # Usar la columna reordenada
  }

  # === 5. GENERAR GRÁFICO ===
  g <- ggplot(df_plot, aes(x = .data[[eje_x_plot]], y = Porcentaje)) + # Usa .data[[eje_x_plot]] para variables dinámicas
    geom_col(fill = "#1d1c49", width = 0.7) +
    geom_text(aes(label = paste0(Porcentaje, "%")), 
              hjust = -0.1, size = 4, fontface = "bold") +
    labs(
      title = titulo,
      subtitle = subtitulo,
      x = NULL, y = "%"
    ) +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(df_plot$Porcentaje, na.rm = TRUE) * 1.15)) +
    theme_minimal() +
    theme(
      plot.title = element_text(face = "bold", size = 14),
      axis.text = element_text(size = 11)
    )
  
  # 6. Guardar y mostrar
  ggsave(paste0(DIR_GRAFICOS, nombre_archivo, ".png"), g, width = 10, height = 6)
  print(g) 
}

# -----------------------------------------------------------------------------
# GRÁFICO Q1: APOYO A CHAVES
# -----------------------------------------------------------------------------
plot_barras_simple(
  variable = "q1_apoyo_chaves",
  disenio = encuesta_dsn_total,
  titulo = "1. ¿Apoya usted la gestión del presidente Rodrigo Chaves?",
  subtitulo = "Base: Total Muestra Ponderada",
  nombre_archivo = "Q1_Apoyo_Chaves"
)

# -----------------------------------------------------------------------------
# GRÁFICO Q2: CALIFICACIÓN PRESIDENTE (DISTRIBUCIÓN 1-10)
# -----------------------------------------------------------------------------
# Tratamos la calificación como categoría para ver cuántos dieron 10, 9, etc.
plot_barras_simple(
  variable = "factor(q2_calif_chaves)", 
  disenio = encuesta_dsn_total,
  titulo = "2. Calificación del Presidente (Escala 1 a 10)",
  subtitulo = "Base: Total Muestra Ponderada",
  nombre_archivo = "Q2_Calif_Chaves_Dist"
)

# ==============================================================================
# GRÁFICO Q3: APOYO ANTERIOR (FILTRO: NO APOYAN HOY)
# ==============================================================================

# Se asume que este sub-diseño se creó previamente en la sección de Análisis de Preguntas Condicionales:
# dsn_no_apoyan <- subset(encuesta_dsn_total, q1_apoyo_chaves == "No") 
dsn_no_apoyan <- subset(encuesta_dsn_total, q1_apoyo_chaves == "No")
# El subtítulo es muy importante para indicar la base de análisis
plot_barras_simple(
  variable = "q3_apoyo_antes",
  disenio = dsn_no_apoyan,
  titulo = "3. ¿Hace un mes apoyaba usted la gestión del presidente Rodrigo Chaves?",
  subtitulo = "Base: Quienes NO apoyan la gestión actual (Q1='No').",
  nombre_archivo = "Q3_Apoyo_Anterior_Chaves"
)

# -----------------------------------------------------------------------------
# [cite_start]GRÁFICO Q7: OPINIÓN DE FIGURAS (MATRIZ CON FILTRO) [cite: 13-25]
# -----------------------------------------------------------------------------
# Solo graficamos la opinión de quienes dijeron "Sí" lo conocen.

# Definir la lista de mapeo (Nombre Figura, Col Conoce, Col Opinion)
figuras_map <- list(
  list(nombre="Rodrigo Chaves", conoce="q7_rodrigo_conoce", opin="q7_rodrigo_opinion"),
  list(nombre="Pilar Cisneros", conoce="q7_pilar_conoce",   opin="q7_pilar_opinion"),
  list(nombre="Laura Fernández", conoce="q7_laura_conoce",   opin="q7_laura_opinion"),
  list(nombre="Álvaro Ramos",    conoce="q7_alvaro_conoce",  opin="q7_alvaro_opinion"),
  list(nombre="Ariel Robles",    conoce="q7_ariel_conoce",  opin="q7_ariel_opinion"),
  list(nombre="Claudia Dobles",  conoce="q7_claudia_conoce", opin="q7_claudia_opinion"),
  list(nombre="Fabricio Alvarado", conoce="q7_fabricio_conoce", opin="q7_fabricio_opinion"),
  list(nombre="Juan Carlos",     conoce="q7_juanc_conoce",  opin="q7_juanc_opinion")
)

for(f in figuras_map) {
  
  # 1. Crear Subset Dinámico: Solo quienes CONOCEN a la figura
  # Usamos una expresión lógica construida dinámicamente
  filtro_expr <- bquote(.(as.name(f$conoce)) == "Sí")
  dsn_filtro <- subset(encuesta_dsn_total, eval(filtro_expr))
  
  # Verificar si hay datos suficientes
  if(nrow(dsn_filtro) > 0) {
    
    # 2. Calcular Opinión
    plot_barras_simple(
      variable = f$opin,
      disenio = dsn_filtro,
      titulo = paste0("Opinión sobre: ", f$nombre),
      subtitulo = paste0("Base: Quienes indican conocerlo/a"),
      nombre_archivo = paste0("Q7_Opinion_", make.names(f$nombre))
    )
    
  } else {
    cat(paste("⚠️ No hay suficientes datos para:", f$nombre, "\n"))
  }
}

# -----------------------------------------------------------------------------
# [cite_start]GRÁFICO Q8: CALIFICACIÓN INSTITUCIONES (RANKING PROMEDIOS) [cite: 26-28]
# -----------------------------------------------------------------------------
# Aquí no queremos porcentajes, queremos la MEDIA (promedio 1-10)

instituciones_cols <- c("q8_tse", "q8_poderJudicial", "q8_fiscaliaGeneral", "q8_ucr", "q8_universidades", "q8_asamblea", "q8_gobierno", "q8_contraloria", "q8_iglesia", "q8_sindicatos", "q8_partidos", "q8_ministros", "q8_medios") 
nombres_inst <- c("TSE", "Poder Judicial", "Fiscalía General", "UCR", "Universidades", "Asamblea Legislativa", "Gobierno", "Contraloría General", "Iglesia Católica", "Sindicatos", "Partidos Políticos", "Ministros de Gobierno", "Medios de Comunicación")  

df_promedios <- data.frame(Institucion = character(), Promedio = double())

for(i in seq_along(instituciones_cols)) {
  var <- instituciones_cols[i]
  # Calcular promedio ponderado
  res <- svymean(as.formula(paste0("~", var)), design = encuesta_dsn_total, na.rm = TRUE)
  
  df_promedios <- rbind(df_promedios, data.frame(
    Institucion = nombres_inst[i],
    Promedio = as.numeric(res)
  ))
}

# Graficar Ranking
g_inst <- ggplot(df_promedios, aes(x = reorder(Institucion, Promedio), y = Promedio)) +
  geom_col(fill = "#2E86C1", width = 0.6) +
  geom_text(aes(label = round(Promedio, 2)), hjust = -0.2, fontface = "bold") +
  scale_y_continuous(limits = c(0, 10)) + # Escala fija de 0 a 10
  coord_flip() +
  labs(
    title = "8. Calificación Promedio de Instituciones (Escala 1-10)",
    subtitle = "Base: Total Muestra Ponderada",
    x = NULL, y = "Promedio (1=Pésima, 10=Excelente)"
  ) +
  theme_minimal()

print(g_inst)
ggsave(paste0(DIR_GRAFICOS, "Q8_Ranking_Instituciones.png"), g_inst, width = 10, height = 8)


# -----------------------------------------------------------------------------
# GRÁFICO Q9: TEMAS PAÍS (BARRAS APILADAS FAVOR/CONTRA)
# -----------------------------------------------------------------------------

# Asegúrate de que los colores estén definidos previamente en tu script
COLOR_FAVOR <- "#1d1c49"   # Azul oscuro
COLOR_CONTRA <- "#D45A26"  # Naranja

temas_cols <- c("q9_topicAsamblea","q9_topicSubasta","q9_topicTSE","q9_topicFiscalia") 
temas_labels <- c("Que la Asamblea Legislativa le levante la inmunidad al presidente Rodrigo Chaves", "La subasta de frecuencias de radio y televisión", "Labor del TSE, respecto a solicitar levantar la inmunidad del presidente Rodrigo Chaves", "La labor de la fiscalía respecto al presidente Rodrigo Chaves")

df_temas <- data.frame()

for(i in seq_along(temas_cols)) {
  var <- temas_cols[i]
  res <- svymean(as.formula(paste0("~", var)), design = encuesta_dsn_total, na.rm = TRUE)
  
  df_temp <- as.data.frame(res) %>%
    rownames_to_column("Respuesta_Raw") %>%
    mutate(
      Tema = temas_labels[i],
      # Limpieza Robusta: Usamos stringr::str_remove para quitar el prefijo de la variable
      Respuesta = stringr::str_remove(Respuesta_Raw, var),
      # CRÍTICO: Usamos str_trim para eliminar cualquier espacio residual
      Respuesta = stringr::str_trim(Respuesta), 
      Porcentaje = mean * 100
    ) %>%
    select(Tema, Respuesta, Porcentaje)
    
  df_temas <- rbind(df_temas, df_temp)
}

# Solución Principal: Filtrar usando la capitalización exacta y excluir NS/NR
df_temas_clean <- df_temas %>%
  filter(Respuesta %in% c("A Favor", "En Contra")) 

g_temas <- ggplot(df_temas_clean, aes(x = Tema, y = Porcentaje, fill = Respuesta)) +
  geom_col(stat = "identity", position = "fill", width = 0.6) +
  geom_text(aes(label = paste0(round(Porcentaje, 1), "%")), 
            position = position_fill(vjust = 0.5), color = "white", fontface = "bold") +
  scale_y_continuous(labels = scales::percent) +
  # Mapeo de colores usando la respuesta exacta del CSV
  scale_fill_manual(values = c("A Favor"=COLOR_FAVOR, "En Contra"=COLOR_CONTRA)) + 
  coord_flip() +
  labs(
    title = "9. Postura sobre temas de actualidad",
    subtitle = "Porcentaje de apoyo o rechazo (Base: Excluye NS/NR)",
    x = NULL, y = NULL, fill = "Postura"
  ) +
  theme_minimal() +
  theme(legend.position = "bottom")

print(g_temas)
ggsave(paste0(DIR_GRAFICOS, "Q9_Temas_Pais_Apilado.png"), g_temas, width = 10, height = 6)

# -----------------------------------------------------------------------------
# [cite_start]GRÁFICO Q10: INTENCIÓN DE VOTO (VOTO VÁLIDO) [cite: 39]
# -----------------------------------------------------------------------------
# Similar a tu script anterior, filtramos nulos/blancos para el gráfico principal

categorias_invalidas <- c("Nulo", "En Blanco", "No Sabe", "No Responde", "Ninguno")

# Crear subset de voto válido
dsn_voto_valido <- subset(encuesta_dsn_total, !voto_presidente %in% categorias_invalidas)

plot_barras_simple(
  variable = "voto_presidente",
  disenio = dsn_voto_valido,
  titulo = "10. Intención de Voto Presidencial (Voto Válido)",
  subtitulo = "Base: Decididos con candidato (Excluye Nulos/Blancos/NSNR)",
  nombre_archivo = "Q10_Voto_Presidente_Valido"
)

# ==============================================================================
# 10. GENERACIÓN DE GRÁFICOS (Q11 Y Q12 - ROP)
# ==============================================================================

# Se asume que la función plot_barras_simple() y la variable DIR_GRAFICOS están definidas

# -----------------------------------------------------------------------------
# GRÁFICO Q11: CONOCIMIENTO DEL ROP (Base Total)
# -----------------------------------------------------------------------------
# Esta pregunta se grafica sobre la base total ponderada (encuesta_dsn_total)

plot_barras_simple(
  variable = "q11_sabe_rop",
  disenio = encuesta_dsn_total,
  titulo = "11. ¿Sabe usted qué es el ROP (Régimen Obligatorio de Pensiones)?",
  subtitulo = "Base: Total Muestra Ponderada",
  nombre_archivo = "Q11_Conocimiento_ROP"
)

# -----------------------------------------------------------------------------
# GRÁFICO Q12: ROP ANTICIPADO (FILTRO: CONOCEN ROP)
# -----------------------------------------------------------------------------
# Filtro: Solo quienes dijeron "Sí" en Q11 (q11_sabe_rop)

dsn_conocen_rop <- subset(encuesta_dsn_total, q11_sabe_rop == "Sí") 

# Se utiliza el sub-diseño (dsn_conocen_rop) para calcular los porcentajes
plot_barras_simple(
  variable = "q12_favor_rop",
  disenio = dsn_conocen_rop,
  titulo = "12. ¿A favor o en contra del retiro anticipado del ROP?",
  subtitulo = "Base: Quienes saben qué es el ROP .",
  nombre_archivo = "Q12_Postura_ROP"
)

cat("\n✅ ¡Generación de gráficos de ROP completada! Revisa la carpeta:", DIR_GRAFICOS, "\n")

# ==============================================================================
# 11. GENERACIÓN DE GRÁFICOS (VOTO Y PREGUNTAS ABIERTAS CODIFICADAS Q4, Q5, Q6)
# ==============================================================================

# NOTA: Se asume que plot_barras_simple() fue corregida y encuesta_dsn_total está cargado.

# -----------------------------------------------------------------------------
# GRÁFICO Q10: INTENCIÓN DE VOTO PRESIDENCIAL (TOTAL MUESTRA) - VERSIÓN FINAL
# -----------------------------------------------------------------------------

# 1. CÁLCULO Y LIMPIEZA DE DATOS
presidente_resultado_raw <- svymean(~as.factor(voto_presidente), design = encuesta_dsn_total, na.rm = TRUE)

presidente_resultado_df <- as.data.frame(presidente_resultado_raw) %>%
    rownames_to_column(var = "Candidato") %>%
    rename(Proporcion = mean, Error_Estandar = SE) %>%
    
    # Extracción robusta del nombre del candidato (CORREGIDA)
    mutate(Candidato = gsub(".*voto_presidente", "", Candidato)) %>%
    mutate(Candidato = gsub("[\\(\\)]", "", Candidato)) %>% 
    mutate(Candidato = stringr::str_trim(Candidato)) %>%
    
    # 🚨 FILTRO ADICIONAL: Eliminar filas vacías o NA que podrían alterar el orden
    filter(Candidato != "" & !is.na(Candidato)) %>%
    
    # Formato y cálculo final
    mutate(`Voto (%)` = round(Proporcion * 100, 1)) 

# 2. CLASIFICACIÓN
categorias_especiales_limpias <- c("No Sabe", "NS/NR", "Nulo", "No Responde", "En blanco", "En Blanco", "No tiene", "NS/NC")

resultados_clasificados <- presidente_resultado_df %>%
    mutate(tipo = ifelse(Candidato %in% categorias_especiales_limpias, "Ninguna persona definida", "Persona candidata"))

# 3. ORDENAMIENTO ESTRICTO Y CONCATENACIÓN (Mayor a Menor en cada grupo)

# 3.1. Candidatos: Ordenados de Mayor a Menor
candidatos_ordenados <- resultados_clasificados %>%
    filter(tipo == "Persona candidata") %>%
    # Usar desc() para asegurar Mayor a Menor (Descendente)
    arrange(`Voto (%)`)

# 3.2. Especiales: Ordenados de Mayor a Menor
especiales_ordenados <- resultados_clasificados %>%
    filter(tipo == "Ninguna persona definida") %>%
    # Usar desc() para asegurar Mayor a Menor (Descendente)
    arrange(`Voto (%)`)

# 3.3. Concatenar: CANDIDATOS primero, ESPECIALES después.
# Esto hace que los niveles de factor para Candidatos (que están al inicio de la tabla) 
# se muestren ARRIBA en el gráfico volteado.
resultados_ordenados <- bind_rows(especiales_ordenados,candidatos_ordenados)

# 3.4. Aplicar el orden resultante al factor
resultados_final <- resultados_ordenados %>%
    mutate(Candidato = forcats::fct_inorder(Candidato))

# 4. CREACIÓN DEL GRÁFICO (PERSONALIZADO)

grafico_voto_presidencial <- ggplot(resultados_final, aes(x = Candidato, y = `Voto (%)`)) +
    geom_col(aes(fill = tipo), width = 0.8) +
    
    geom_text(aes(label = paste0(round(`Voto (%)`, 1), "%")), 
              hjust = -0.1, size = 4, color = "black", fontface = "bold") +
              
    # Colores definidos
    scale_fill_manual(values = c("Persona candidata" = COLOR_PRINCIPAL, "Ninguna persona definida" = COLOR_SECUNDARIO)) +
    
    labs(
        title = "10. ¿Si las elecciones fueran hoy por quién votaría?",
        subtitle = "Base: Total Muestra Ponderada (Incluye Nulo, Blanco, NS/NR).",
        x = NULL, 
        y = "Porcentaje (%)", 
        fill = "Tipo de Voto"
    ) +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(resultados_final$`Voto (%)`) * 1.15)) +
    theme_minimal() +
    theme(legend.position = "bottom")

print(grafico_voto_presidencial)

# --- EXPORTACIÓN (Si DIR_GRAFICOS existe) ---
if (exists("DIR_GRAFICOS")) {
    ggsave(
        filename = file.path(DIR_GRAFICOS, "Q10_Voto_Total_Personalizado.png"), 
        plot = grafico_voto_presidencial,
        width = 8, 
        height = 6, 
        units = "in"
    )
}

# -----------------------------------------------------------------------------
# GRÁFICO Q4: RAZÓN DE PÉRDIDA DE APOYO (CODIFICADO)
# -----------------------------------------------------------------------------

if (nrow(dsn_dejo_apoyar$variables) > 0) {
    # 1. Calcular frecuencias ponderadas
    freq_q4 <- svytable(~q4_razon_cambio_code, design = dsn_dejo_apoyar)
    df_q4_calc <- as.data.frame(prop.table(freq_q4)) %>%
        # Cambiar el nombre del factor a la clave del diccionario
        rename(q4_razon_cambio_code = q4_razon_cambio_code, 
               `Mención (%)` = Freq) %>%
        mutate(`Mención (%)` = `Mención (%)` * 100) %>%
        # 2. Unir con el diccionario
        left_join(dic_q4_razon_cambio, by = "q4_razon_cambio_code") %>%
        # Filtrar posibles NAs si el código no se encuentra
        filter(!is.na(Q4_Etiqueta))
    
    # 3. Preparar para el gráfico
    base_n_q4 <- sum(dsn_dejo_apoyar$variables$ponderador_final, na.rm = TRUE)
    
    df_grafico_q4 <- df_q4_calc %>%
        mutate(Q4_Etiqueta = forcats::fct_reorder(Q4_Etiqueta, `Mención (%)`))
    
    # 4. Crear el gráfico
    grafico_q4 <- ggplot(df_grafico_q4, aes(x = Q4_Etiqueta, y = `Mención (%)`)) +
        geom_col(fill = COLOR_SECUNDARIO, width = 0.8) +
        geom_text(aes(label = paste0(round(`Mención (%)`, 1), "%")), 
                  hjust = -0.1, size = 3.5, color = "black", fontface = "bold") +
        labs(
            title = "4. Razón Principal por la que DEJO de apoyar al Presidente (Q4)",
            subtitle = paste0("Base: Quienes NO apoyan hoy, pero SÍ hace un mes"),
            x = "Categoría Temática",
            y = "Porcentaje de Mención (%)"
        ) +
        coord_flip() +
        scale_y_continuous(limits = c(0, max(df_grafico_q4$`Mención (%)`) * 1.15)) +
        theme_minimal()

    print(grafico_q4)

    # Exportar gráfico
    ggsave(
        filename = file.path(DIR_GRAFICOS, "Q4_Razon_Perdida_Apoyo_Etiquetado.png"), 
        plot = grafico_q4,
        width = 8, 
        height = 6, 
        units = "in"
    )

} else {
    cat("\n-> Q4: No hay suficientes casos en la base 'Dejó de apoyar' para graficar.\n")
}
# -----------------------------------------------------------------------------
# GRÁFICO Q5: RAZONES PARA NO APOYAR (CODIFICADO)
# -----------------------------------------------------------------------------
# Se asume que la tabla df_q5 con las etiquetas Q5_Etiqueta ya fue generada 
# en la Sección 7 del script principal.
# Se asume que la base dsn_no_apoyan ya está disponible.

# Calcular Base Ponderada (si no está disponible en la variable 'base_n_q5')
base_n_q5 <- sum(dsn_no_apoyan$variables$ponderador_final, na.rm = TRUE)

# 1. Aseguramos el orden de las etiquetas
df_grafico_q5 <- df_q5 %>%
    mutate(Q5_Etiqueta = forcats::fct_reorder(Q5_Etiqueta, `Mención (%)`))

# 2. Crear el gráfico
grafico_q5 <- ggplot(df_grafico_q5, aes(x = Q5_Etiqueta, y = `Mención (%)`)) +
    geom_col(fill = COLOR_PRINCIPAL, width = 0.8) +
    geom_text(aes(label = paste0(round(`Mención (%)`, 1), "%")), 
              hjust = -0.1, size = 3.5, color = "black", fontface = "bold") +
    labs(
        title = "5. Razón Principal para NO apoyar la gestión (Q5)",
        subtitle = paste0("Base: Quienes NO apoyan la gestión actual"),
        x = "Categoría Temática",
        y = "Porcentaje de Mención (%)"
    ) +
    coord_flip() +
    scale_y_continuous(limits = c(0, max(df_grafico_q5$`Mención (%)`) * 1.15)) +
    theme_minimal()

print(grafico_q5)

# Exportar gráfico
ggsave(
    filename = file.path(DIR_GRAFICOS, "Q5_Razon_No_Apoyo_Etiquetado.png"), 
    plot = grafico_q5,
    width = 8, 
    height = 6, 
    units = "in"
)

# -----------------------------------------------------------------------------
# GRÁFICO Q6: RAZONES PARA SÍ APOYAR (RESPUESTA MÚLTIPLE)
# -----------------------------------------------------------------------------
# Usamos el resultado de la tabla ponderada (res_q6_ponderada)

# Aseguramos que los datos estén ordenados para el gráfico (del más largo al más corto)
# Usamos res_q6_final (que ya tiene las etiquetas)
df_grafico_q6 <- res_q6_final %>%
    # 🚨 CORRECCIÓN: Reordenar la ETIQUETA (Q6_Etiqueta) por el valor (`Mención (%)`)
    mutate(Q6_Etiqueta = forcats::fct_reorder(Q6_Etiqueta, `Mención (%)`))

grafico_q6 <- ggplot(df_grafico_q6, aes(x = Q6_Etiqueta, y = `Mención (%)`)) +
    geom_col(fill = COLOR_PRINCIPAL, width = 0.8) +
    geom_text(aes(label = paste0(`Mención (%)`, "%")), 
              hjust = -0.1, size = 3.5, color = "black", fontface = "bold") +
    labs(
        title = "6. Razones para SÍ apoyar al Presidente (Múltiple Respuesta)",
        subtitle = paste0("Base: Quienes SÍ apoyan"),
        x = "Categoría Temática", # ⬅️ Etiqueta de eje actualizada
        y = "Porcentaje de Mención (%)"
    ) +
    coord_flip() +
    # Usamos df_grafico_q6 para asegurar la consistencia del límite
    scale_y_continuous(limits = c(0, max(df_grafico_q6$`Mención (%)`) * 1.15)) +
    theme_minimal()

print(grafico_q6)

# Exportar gráfico (ajusta la ruta según tu configuración)
ggsave(
    filename = file.path(DIR_GRAFICOS, "Q6_Razon_Si_Apoyo_Multiple.png"), 
    plot = grafico_q6,
    width = 8, 
    height = 6, 
    units = "in"
)

# ==============================================================================
# 12. GENERACIÓN DE GRÁFICOS (Q7: CONOCIMIENTO DE FIGURAS PÚBLICAS)
# ==============================================================================

# 1. Definir la lista de variables de conocimiento y sus etiquetas
conoce_vars <- c("q7_rodrigo_conoce", "q7_pilar_conoce", "q7_laura_conoce", 
                 "q7_alvaro_conoce", "q7_ariel_conoce", "q7_claudia_conoce", 
                 "q7_fabricio_conoce", "q7_juanc_conoce")

nombres_figuras <- c("Rodrigo Chaves", "Pilar Cisneros", "Laura Fernández", 
                     "Álvaro Ramos", "Ariel Robles", "Claudia Dobles", 
                     "Fabricio Alvarado", "Juan Carlos Hidalgo")

df_figuras_conoce <- data.frame(variable = conoce_vars, nombre = nombres_figuras)

# 2. Bucle para generar cada gráfico
cat("\n--- Generando Gráficos de Conocimiento de Figuras (Q7) ---\n")

for (i in 1:nrow(df_figuras_conoce)) {
    
    var_name <- df_figuras_conoce$variable[i]
    figura_label <- df_figuras_conoce$nombre[i]
    
    plot_barras_simple(
        variable = var_name,
        disenio = encuesta_dsn_total,
        titulo = paste0("7. Conocimiento de la figura: ", figura_label),
        subtitulo = "Base: Total Muestra Ponderada",
        nombre_archivo = paste0("Q7_Conoce_", gsub(" ", "_", figura_label))
    )
}

cat("\n✅ Generación de gráficos de Conocimiento (Q7) completada.\n")