# ==============================================================================
# 7. CÁLCULO DE TASAS DE RECHAZO PONDERADAS (ACTUALIZADO)
# ==============================================================================

# NOTA: Usamos las estimaciones de proporción (svymean) ya calculadas,
# y extraemos la categoría 'No Responde'.

# --- 7.1. Base Total de Encuestas Válidas (df_analisis, para 'votara') ---

# 1. Tasa de Rechazo Ponderada en Votación (Pregunta: ¿Usted Votará?)
# La Tasa de Rechazo para esta pregunta es la proporción ponderada de 'No Responde'.
rechazo_votara_df <- as.data.frame(votara_resultado)
rechazo_votara_ponderada <- rechazo_votara_df %>%
    filter(grepl("No Responde", rownames(.), ignore.case = TRUE)) %>%
    pull(mean)

# --- 7.2. Base Votantes Válidos (df_analisis_nacional, para intención de voto) ---

# 2. Tasa de Rechazo Ponderada en Voto Presidencial (Pregunta: ¿Por quién votaría?)
rechazo_presidente_df <- as.data.frame(presidente_resultado)
rechazo_presidente_ponderada <- rechazo_presidente_df %>%
    filter(grepl("No Responde", rownames(.), ignore.case = TRUE)) %>%
    pull(mean)

# 3. Tasa de Rechazo Ponderada en Voto Diputados (Pregunta: ¿Por quién votaría a Diputado?)
rechazo_diputado_df <- as.data.frame(diputado_resultado)
rechazo_diputado_ponderada <- rechazo_diputado_df %>%
    filter(grepl("No Responde", rownames(.), ignore.case = TRUE)) %>%
    pull(mean)

# 4. Tasa de Rechazo Ponderada en Partido Preferente
rechazo_partido_preferente_df <- as.data.frame(partido_preferente_resultado)
rechazo_partido_preferente_ponderada <- rechazo_partido_preferente_df %>%
    filter(grepl("No Responde", rownames(.), ignore.case = TRUE)) %>%
    pull(mean)

# Cálculo de la Tasa de Respuesta como complemento
respuesta_votara_ponderada <- 1 - rechazo_votara_ponderada
respuesta_presidente_ponderada <- 1 - rechazo_presidente_ponderada
respuesta_diputado_ponderada <- 1 - rechazo_diputado_ponderada
respuesta_partido_preferente_ponderada <- 1 - rechazo_partido_preferente_ponderada


cat("\n
======================================================\n
    TASAS DE NO RESPUESTA (RECHAZO) Y RESPUESTA PONDERADAS\n
======================================================\n")

# TASA DE RESPUESTA Y RECHAZO PARA LA PREGUNTA: ¿USTED VOTARÁ? (BASE VÁLIDA TOTAL)
cat("1. Base Total Válida (Pregunta Votará):\n")
cat(paste("   - Tasa de Respuesta Ponderada (Sí/No):", 
          round(respuesta_votara_ponderada * 100, 2), "%\n"))
cat(paste("   - Tasa de Rechazo Ponderada (No Responde):", 
          round(rechazo_votara_ponderada * 100, 2), "%\n\n"))

# TASA DE RESPUESTA Y RECHAZO PARA LAS PREGUNTAS DE INTENCIÓN DE VOTO (BASE VOTANTES VÁLIDOS)
cat("2. Base Votantes Válidos (Intención de Voto):\n")
cat("   - Voto Presidencial:\n")
cat(paste("     - Tasa de Respuesta Ponderada (Candidato/Nulo/Blanco/NS):", 
          round(respuesta_presidente_ponderada * 100, 2), "%\n"))
cat(paste("     - Tasa de Rechazo Ponderada (No Responde):", 
          round(rechazo_presidente_ponderada * 100, 2), "%\n"))
cat("   - Voto Diputados:\n")
cat(paste("     - Tasa de Respuesta Ponderada (Partido/Nulo/Blanco/NS):", 
          round(respuesta_diputado_ponderada * 100, 2), "%\n"))
cat(paste("     - Tasa de Rechazo Ponderada (No Responde):", 
          round(rechazo_diputado_ponderada * 100, 2), "%\n"))
cat("   - Partido Preferente:\n")
cat(paste("     - Tasa de Respuesta Ponderada (Partido/Ninguno):", 
          round(respuesta_partido_preferente_ponderada * 100, 2), "%\n"))
cat(paste("     - Tasa de Rechazo Ponderada (No Responde):", 
          round(rechazo_partido_preferente_ponderada * 100, 2), "%\n"))

cat("======================================================\n")

