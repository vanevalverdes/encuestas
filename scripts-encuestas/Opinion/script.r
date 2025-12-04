# ==============================================================================
# SCRIPT ADAPTADO: ENCUESTA OPOL (FORMULARIO V1 - CHAVES/FIGURAS)
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
library(stringr)  # Contiene str_trim()
library(stringi)  # Contiene stri_trans_general() para quitar tildes

options(survey.lonely.psu = "adjust") 

# -----------------------------------------------------------------------------
# 2. DEFINICIÓN DE DATOS POBLACIONALES (SE MANTIENE IGUAL)
# -----------------------------------------------------------------------------
# Asumimos que la población meta (Padrón) no ha cambiado para este estudio.
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

poblacion_provincia <- data.frame(
  estrato_provincia = c("san-jose", "alajuela", "cartago", "heredia", "guanacaste", "puntarenas", "limon"),
  N_provincia = c(1192706, 723861, 429191, 378289, 278818, 351197, 313972)
)

# -----------------------------------------------------------------------------
# 2. DEFINICIÓN DE CÓDIGOS DE RESPUESTA (Para etiquetas de gráficos/tablas)
# -----------------------------------------------------------------------------

# --- CÓDIGOS Q4: RAZÓN DE CAMBIO (C1 a C8) ---
# Base: Dejó de apoyar este mes
dic_q4_razon_cambio <- data.frame(
  q4_razon_cambio_code = c("c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8"),
  Q4_Etiqueta = c(
    "Estilo y Comunicación", 
    "Incumplimiento de Promesas", 
    "Economía/Costo de Vida", 
    "Ética/Corrupción", 
    "Ataque a Instituciones", 
    "Seguridad", 
    "Agricultores", 
    "Otros/No Especifica"
  ),
  stringsAsFactors = FALSE
)

# --- CÓDIGOS Q6: RAZONES PARA SÍ APOYAR (A1 a A7) ---
# Base: Quienes SÍ apoyan hoy
dic_q6_razon_apoyo <- data.frame(
  approveReasonCode = c("A1", "A2", "A3", "A4", "A5", "A6", "A7"),
  Q6_Etiqueta = c(
    "Estilo Fuerte/Decidido", 
    "Lucha contra Corrupción", 
    "Resultados Económicos", 
    "Orden y Hacienda Pública", 
    "Manejo de Seguridad", 
    "Acercamiento al Pueblo", 
    "Otros/Varios/No Sabe"
  ),
  stringsAsFactors = FALSE
)

# --- CÓDIGOS Q5: RAZONES PARA NO APOYAR (R1 a R8) ---
# Base: Quienes NO apoyan hoy
dic_q5_razon_no_apoyo <- data.frame(
  q5_razon_no_apoyo_code = c("R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"),
  Q5_Etiqueta = c(
    "Estilo Personal/Confrontación", 
    "Corrupción/Ética (Histórico)", 
    "Mal Manejo Económico", 
    "Costo de Vida/Inflación", 
    "Falta de Resultados (General)", 
    "Ataque a Instituciones/Democracia", 
    "Seguridad", 
    "Otros/Varios/No Sabe"
  ),
  stringsAsFactors = FALSE
)

# -----------------------------------------------------------------------------
# 3. CARGA Y LIMPIEZA (ADAPTADO AL NUEVO FORMULARIO)
# -----------------------------------------------------------------------------

# !!! ACTUALIZAR RUTA
RUTA_BASE_DATOS <- "C:\\Users\\vanev\\Documents\\Opol\\Encuesta de Opinion\\survey.csv"
# Detectamos si es coma o punto y coma
#df <- read_csv(RUTA_BASE_DATOS, show_col_types = FALSE) 
df <- readr::read_delim(RUTA_BASE_DATOS, delim = ";", show_col_types = FALSE)

# ### CAMBIO IMPORTANTE: AQUÍ DEBES MAPEAR TUS COLUMNAS DEL CSV A LAS VARIABLES
df <- df %>%
  rename(
    # Demográficas (Igual que antes)
    sexo_raw = gender,
    edad_raw = age,
    estrato_provincia = state,
    conglomerado_canton = county,
    educacion = education,
    religion = religion,
    
    q1_apoyo_chaves = chavesSupport,           # 1. Apoyo gestión
    q2_calif_chaves = chavesScale,           # 2. Calificación 1-10
    q3_apoyo_antes = lastMonth,            # 3. Apoyaba hace un mes? (Filtro: No en Q1)

# NUEVAS VARIABLES CODIFICADAS (Q4, Q5, Q6)
    q4_razon_cambio_code = lastMonthOpinionCode, # Q4 (Razón por la que dejó de apoyar)
    q5_razon_no_apoyo_code = rejectReasonCode,   # Q5 (Razón principal para NO apoyar)
    q6_razon_si_apoyo_code = approveReasonCode,  # Q6 (Razón principal para SÍ apoyar)
    
    # Q7 Personajes (Conocimiento y Opinión)
    # Asume que tu CSV tiene cols tipo: q7_rodrigo_conoce, q7_rodrigo_opinion, etc.
    q7_rodrigo_conoce = conoceChaves, q7_rodrigo_opinion = opinionChaves,
    q7_pilar_conoce = conocePilar,   q7_pilar_opinion = opinionPilar,
    q7_laura_conoce = conoceLaura,   q7_laura_opinion = opinionLaura,
    q7_alvaro_conoce = conoceRamos,  q7_alvaro_opinion = opinionRamos,
    q7_ariel_conoce = conoceAriel,   q7_ariel_opinion = opinionAriel,
    q7_claudia_conoce = conoceClaudia, q7_claudia_opinion = opinionClaudia,
    q7_fabricio_conoce = conoceFabricio,q7_fabricio_opinion = opinionFabricio,
    q7_juanc_conoce = conoceJuanCarlos,   q7_juanc_opinion = opinionJuanCarlos,
    
    # Q8 Instituciones (1-10)
    q8_tse = tse,
    q8_poderJudicial = poderJudicial,
    q8_fiscaliaGeneral = fiscaliaGeneral,
    q8_ucr = ucr,
    q8_universidades = universidades,
    q8_asamblea = asamblea,
    q8_gobierno = gobierno,
    q8_contraloria = contraloria,
    q8_iglesia = iglesia,
    q8_sindicatos = sindicatos,
    q8_partidos = partidos,
    q8_ministros = ministros,
    q8_medios = medios,
    
    # Q9 Temas (Favor/Contra)
    q9_topicAsamblea = topicAsamblea,
    q9_topicSubasta = topicSubasta,
    q9_topicTSE = topicTSE,
    q9_topicFiscalia = topicFiscalia,
    
    # Q10 Voto
    voto_presidente = nationalElection,
    
    # Q11 y Q12 ROP
    q11_sabe_rop = conoceROP,
    q12_favor_rop = opinionROP # (Filtro: Sí en Q11)
  ) %>% 
  mutate(
    # Normalización demográfica (Igual que tu script original)
    sexo = case_when(
      grepl("Femenino|Mujer|M", sexo_raw, ignore.case = TRUE) ~ "M",
      grepl("Masculino|Hombre|H", sexo_raw, ignore.case = TRUE) ~ "H",
      TRUE ~ "NA_SEXO"
    ),
    provincia = tolower(estrato_provincia),
    grupo_edad = case_when(
      edad_raw %in% c("18-20", "21-24", "25-29", "30-34") ~ "Joven",
      edad_raw %in% c("35-39", "40-44", "45-49", "50-54", "55-59", "60-64") ~ "Adulto",
      edad_raw %in% c("65-69", "70-79", "+80") ~ "AdultoMayor",
      TRUE ~ "NA_EDAD"
    ),
    # Celda de ponderación
    celda_ponderacion = paste(sexo, grupo_edad, provincia, sep = "_")
  )

# -----------------------------------------------------------------------------
# 4. PONDERACIÓN Y DISEÑO (SE MANTIENE IGUAL)
# -----------------------------------------------------------------------------

frecuencia_muestral <- df %>%
  group_by(celda_ponderacion) %>%
  summarise(n_j = n()) %>%
  ungroup() %>%
  mutate(p_j = n_j / sum(n_j))

df_ajustada <- frecuencia_muestral %>%
  left_join(poblacion_tse, by = "celda_ponderacion") %>%
  mutate(ponderador_final = P_j / p_j)

df <- df %>%
  left_join(df_ajustada %>% select(celda_ponderacion, ponderador_final), by = "celda_ponderacion") %>%
  mutate(ponderador_final = if_else(is.na(ponderador_final), 1.0, ponderador_final))

# Base Total Válida
df_analisis_total <- df %>%
  # Si tienes columna 'category', filtra aquí. Si no, omite el filter.
  # filter(category == 1) %>% 
  mutate(conglomerado_unico = paste(estrato_provincia, conglomerado_canton, sep = "_")) %>%
  left_join(poblacion_provincia, by = c("provincia" = "estrato_provincia")) %>%
  filter(!is.na(ponderador_final) & !is.na(conglomerado_unico) & !is.na(N_provincia))

# FPC
tamanio_muestral_provincia_total <- df_analisis_total %>%
  group_by(provincia) %>%
  summarise(n_provincia = n()) %>%
  ungroup()

df_analisis_total <- df_analisis_total %>%
  left_join(tamanio_muestral_provincia_total, by = "provincia")

# DISEÑO PRINCIPAL (BASE TOTAL)
encuesta_dsn_total <- svydesign(
  ids = ~conglomerado_unico,
  strata = ~provincia,
  weights = ~ponderador_final,
  data = df_analisis_total,
  fpc = ~N_provincia
)

# -----------------------------------------------------------------------------
# 5. CÁLCULO DE ERROR Y DEFF (USANDO VARIABLE PRINCIPAL)
# -----------------------------------------------------------------------------
# Usamos q1_apoyo_chaves o voto_presidente como proxy para el DEFF
proxy_deff <- svymean(~voto_presidente, design = encuesta_dsn_total, na.rm = TRUE)

deff_real_array <- tryCatch({
  deff(proxy_deff)
}, warning = function(w) {
  # Fallback manual si falla survey
  SE_ajustado <- SE(proxy_deff)
  varianza_compleja <- SE_ajustado^2
  p_hat <- as.numeric(proxy_deff)[1]
  n_total <- nrow(df_analisis_total)
  varianza_mas <- (p_hat * (1 - p_hat)) / (n_total - 1)
  return(c(varianza_compleja / varianza_mas))
})

DEFF_VALOR <- as.numeric(deff_real_array)[1]
n_valido <- nrow(df_analisis_total)
Z <- 1.96
ME_MAXIMO <- Z * sqrt((0.5 * 0.5 * DEFF_VALOR) / n_valido) * 100

cat("\n=== MÉTRICAS GLOBALES ===\n")
cat("N Válido:", n_valido, "\n")
cat("DEFF Real:", round(DEFF_VALOR, 3), "\n")
cat("Margen de Error Máximo (95%): ±", round(ME_MAXIMO, 2), "%\n")


# -----------------------------------------------------------------------------
# 6. ANÁLISIS DE PREGUNTAS SIMPLES (TOTAL MUESTRA)
# -----------------------------------------------------------------------------
# Pregunta 1: Apoyo a Chaves [cite: 7]
print(svymean(~q1_apoyo_chaves, design = encuesta_dsn_total, na.rm = TRUE))

# Pregunta 10: Intención de Voto (Base Total) [cite: 39]
# Nota: Si quieres quitar nulos/blancos, crea un subset como en tu script anterior
print(svymean(~voto_presidente, design = encuesta_dsn_total, na.rm = TRUE))


# -----------------------------------------------------------------------------
# 7. ANÁLISIS DE PREGUNTAS CONDICIONALES (SUBSETS Y CÓDIGOS ABIERTOS)
# -----------------------------------------------------------------------------


# --- DISEÑOS CONDICIONALES NECESARIOS ---
# Base: Quienes NO apoyan hoy (Necesario para Q3, Q4, Q5)
dsn_no_apoyan <- subset(encuesta_dsn_total, q1_apoyo_chaves == "No")
# Base: Quienes SÍ apoyan hoy (Necesario para Q6)
dsn_apoyan <- subset(encuesta_dsn_total, q1_apoyo_chaves == "Sí")

# --- Q3: Apoyo hace un mes (Filtro: NO apoyan hoy) ---
cat("\n--- Q3: Apoyo hace un mes (Base: No apoyan actualmente) ---\n")
print(svymean(~q3_apoyo_antes, design = dsn_no_apoyan, na.rm = TRUE))

# --- Q4: Razón del cambio (Base: Dejó de apoyar este mes) ---
dsn_dejo_apoyar <- subset(encuesta_dsn_total, 
                          q1_apoyo_chaves == "No" & q3_apoyo_antes == "Sí") # Usamos el valor exacto: Sí

cat("\n--- DIAGNÓSTICO Q4 (CORREGIDO) ---\n")
cat(paste0("Tamaño de la base dsn_dejo_apoyar (N): ", nrow(dsn_dejo_apoyar$variables), "\n"))

cat("\n--- DIAGNÓSTICO Q4 (CORREGIDO) ---\n")
n_dejo_apoyar <- nrow(dsn_dejo_apoyar$variables)
cat(paste0("Tamaño de la base dsn_dejo_apoyar (N): ", n_dejo_apoyar, "\n"))

cat("\n--- Q4: Razón por la que dejó de apoyar (Etiquetado) ---\n")

if (n_dejo_apoyar == 0) {
    cat("  -> Base 'Dejó de apoyar' está vacía. No hay resultados para mostrar.\n")
} else {
    
    # 2. Manejo de NA en la Variable de Códigos (Copia de la lógica anterior)
    df_q4_base <- dsn_dejo_apoyar$variables
    
    # Normalizar y Limpiar (ya estaban en minúsculas en el código anterior)
    df_q4_base <- df_q4_base %>%
      mutate(q4_razon_cambio_code = stringr::str_trim(q4_razon_cambio_code)) %>% 
      mutate(q4_razon_cambio_code = stringr::str_to_lower(q4_razon_cambio_code))
      
    # Reemplazar NA/NULL/vacío con 'c8' (Otros/No Especifica)
    df_q4_base$q4_razon_cambio_code[
        is.na(df_q4_base$q4_razon_cambio_code) | df_q4_base$q4_razon_cambio_code == ""
    ] <- "c8"
    
    # Reemplazamos la data en el diseño temporalmente para el cálculo
    dsn_dejo_apoyar$variables <- df_q4_base

    tryCatch({
        # Intento de cálculo con SE (svymean)
        res_q4 <- svymean(~as.factor(q4_razon_cambio_code), design = dsn_dejo_apoyar, na.rm = TRUE)
        
        # 1. CONVERSIÓN Y ETIQUETADO del resultado de svymean
        df_q4_res <- as.data.frame(res_q4) %>%
            rownames_to_column(var = "Variable") %>%
            
            # 🚨 CORRECCIÓN CRÍTICA: Extracción Robusta del Código
            # Usa una expresión regular para remover todo lo que precede al código (incluyendo as.factor() )
            mutate(q4_razon_cambio_code = gsub(".*q4_razon_cambio_code", "", Variable)) %>%
            # Limpiamos paréntesis residuales
            mutate(q4_razon_cambio_code = gsub("[\\(\\)]", "", q4_razon_cambio_code)) %>% 
            mutate(q4_razon_cambio_code = stringr::str_trim(q4_razon_cambio_code)) %>% 
            
            mutate(`Mención (%)` = mean * 100) %>%
            left_join(dic_q4_razon_cambio, by = "q4_razon_cambio_code") %>%
            
            # Redondeo para la tabla
            mutate(`Mención (%)` = round(`Mención (%)`, 1), 
                   SE = round(SE, 4)) %>%
                   
            dplyr::select(Q4_Etiqueta, `Mención (%)`, SE) %>%
            filter(!is.na(Q4_Etiqueta)) %>%
            arrange(desc(`Mención (%)`))
            
        print(df_q4_res)
        
    }, error = function(e) {
        cat("\n⚠️ ADVERTENCIA Q4: Error al calcular SE. Se reporta la distribución ponderada y etiquetada.\n")
        
        # Fallback a tabla ponderada (svytable)
        freq_q4 <- svytable(~q4_razon_cambio_code, design = dsn_dejo_apoyar)
        
        # 2. CONVERSIÓN Y ETIQUETADO del resultado de svytable
        df_q4_fallback <- as.data.frame(prop.table(freq_q4) * 100) %>%
            rename(q4_razon_cambio_code = q4_razon_cambio_code, 
                   `Mención (%)` = Freq) %>%
            
            # La limpieza en svytable es más simple, pero aplicamos la misma lógica
            mutate(q4_razon_cambio_code = stringr::str_trim(q4_razon_cambio_code)) %>%
            
            left_join(dic_q4_razon_cambio, by = "q4_razon_cambio_code") %>%
            
            # Redondeo para la tabla
            mutate(`Mención (%)` = round(`Mención (%)`, 1)) %>%
            
            dplyr::select(Q4_Etiqueta, `Mención (%)`) %>%
            filter(!is.na(Q4_Etiqueta)) %>%
            arrange(desc(`Mención (%)`))
            
        print(df_q4_fallback)
    })
}

# --- Q5: Razones para NO apoyar (Codificado) ---
cat("\n--- Q5: Razón Principal para NO apoyar (Codificado) ---\n")
res_q5_raw <- svymean(~q5_razon_no_apoyo_code, design = dsn_no_apoyan, na.rm = TRUE)

# CONVERSIÓN Y ETIQUETADO
df_q5 <- as.data.frame(res_q5_raw) %>%
    rownames_to_column(var = "Variable") %>%
    mutate(q5_razon_no_apoyo_code = gsub("q5_razon_no_apoyo_code", "", Variable)) %>%
    mutate(`Mención (%)` = mean * 100) %>%
    left_join(dic_q5_razon_no_apoyo, by = "q5_razon_no_apoyo_code") %>%
    
    mutate(`Mención (%)` = round(`Mención (%)`, 1), # Redondea al primer decimal
           SE = round(SE, 4)) %>%                  # Opcional: Redondear el error estándar
           
    dplyr::select(Q5_Etiqueta, `Mención (%)`, SE) %>%
    filter(!is.na(Q5_Etiqueta)) %>%
    arrange(desc(`Mención (%)`))

print(df_q5)

# --- Q6: Razones para SÍ apoyar (Codificado) ---
cat("\n--- Q6: Razones para SÍ apoyar (Respuesta Múltiple) ---\n")

# VERIFICACIÓN CRÍTICA: Asegurar que la base de diseño no esté vacía
if (nrow(dsn_apoyan$variables) == 0) {
    cat("  -> Base de apoyo vacía (N=0). No hay casos para analizar.\n")
    return(invisible(NULL)) # Salir si no hay casos
}

# 1. Preparar la tabla de datos:
df_q6 <- dsn_apoyan$variables %>% 
  # Seleccionar la columna codificada y el peso
  dplyr::select(q6_razon_si_apoyo_code, ponderador_final) %>%
  rename(approveReasonCode = q6_razon_si_apoyo_code) %>%
  
  # Limpiar y desagregar
  mutate(approveReasonCode = str_trim(approveReasonCode)) %>%
  separate_rows(approveReasonCode, sep = "[,;\\s]+", convert = FALSE) %>%
  mutate(approveReasonCode = str_trim(approveReasonCode)) %>%
  filter(!is.na(approveReasonCode) & approveReasonCode != "" & approveReasonCode != "NULL")

# 2. Contar la frecuencia ponderada de cada código individual
if (nrow(df_q6) > 0) {
    
    # MANEJO DE ERROR: Usamos tryCatch para calcular la base_n de forma segura
    base_n <- tryCatch({
        # Intenta calcular N ponderado usando el diseño de encuesta
        as.numeric(svytotal(~1, design = dsn_apoyan))
    }, error = function(e) {
        cat("  -> ⚠️ Fallo en svytotal. Usando suma directa de la columna 'ponderador_final' como respaldo.\n")
        # Respaldo: Sumar la columna de peso directamente
        sum(dsn_apoyan$variables$ponderador_final, na.rm = TRUE)
    })
    
    # Verificación final de la base de cálculo
    if (is.na(base_n) || base_n < 1) {
        cat("  -> Base de apoyo sin ponderación válida. No hay resultados.\n")
        return(invisible(NULL))
    }
    
    res_q6_ponderada <- df_q6 %>%
        group_by(approveReasonCode) %>%
        summarise(Total_Ponderado = sum(ponderador_final)) %>%
        ungroup() %>%
        mutate(`Mención (%)` = (Total_Ponderado / base_n) * 100) %>%
        arrange(desc(`Mención (%)`)) %>%
        mutate(
            Total_Ponderado = round(Total_Ponderado, 0),
            `Mención (%)` = round(`Mención (%)`, 1)
        )
    res_q6_final <- res_q6_ponderada %>%
        # Unir por la columna approveReasonCode
        left_join(dic_q6_razon_apoyo, by = "approveReasonCode") %>%
        # Seleccionar las columnas para impresión/gráfico
        dplyr::select(Q6_Etiqueta, `Mención (%)`, Total_Ponderado) %>%
        # Eliminar las filas sin código si existen (Otros/Varios)
        filter(!is.na(Q6_Etiqueta))
    
    cat("  -> Base: Quienes SÍ apoyan (N ponderado:", round(base_n, 0), ")\n")
    print(res_q6_final) # Imprimir la tabla final con etiquetas

} else {
    cat("  -> La base tiene casos, pero ninguno con código válido en Q6.\n")
}

# --- Q12: ROP Anticipado (Filtro: SÍ conocen el ROP) ---
dsn_conocen_rop <- subset(encuesta_dsn_total, q11_sabe_rop == "Sí")

cat("\n--- Q12: Favor/Contra ROP (Base: Conocen el ROP) ---\n")
print(svymean(~q12_favor_rop, design = dsn_conocen_rop, na.rm = TRUE))

# -----------------------------------------------------------------------------
# 8. ANÁLISIS DE MATRICES (FIGURAS POLÍTICAS - Q7)
# -----------------------------------------------------------------------------
# [cite: 13-25]
# Iteramos sobre la lista de figuras para generar Conocimiento y Opinión

lista_figuras <- list(
  c("Rodrigo Chaves", "q7_rodrigo_conoce", "q7_rodrigo_opinion"),
  c("Pilar Cisneros", "q7_pilar_conoce", "q7_pilar_opinion"),
  c("Laura Fernández", "q7_laura_conoce", "q7_laura_opinion"),
  c("Álvaro Ramos", "q7_alvaro_conoce", "q7_alvaro_opinion"),
  c("Ariel Robles", "q7_ariel_conoce", "q7_ariel_opinion"),
  c("Claudia Dobles", "q7_claudia_conoce", "q7_claudia_opinion"),
  c("Fabricio Alvarado", "q7_fabricio_conoce", "q7_fabricio_opinion"),
  c("Juan Carlos Hidalgo", "q7_juanc_conoce", "q7_juanc_opinion")
)

for(figura in lista_figuras) {
  nombre <- figura[1]
  col_conoce <- figura[2]
  col_opinion <- figura[3]
  
  cat(paste0("\n>>> ANALIZANDO: ", nombre, " <<<\n"))
  
  # 1. Conocimiento (Base Total)
  formula_conoce <- as.formula(paste0("~", col_conoce))
  res_conoce <- svymean(formula_conoce, design = encuesta_dsn_total, na.rm = TRUE)
  
  cat("  -> Conocimiento:\n")
  print(res_conoce)
  
  # 2. Opinión (Base: Solo los que conocen)
  # Creamos el subset dinámicamente. Asumimos que la respuesta positiva es 'Sí'
  # Nota: subset evalúa la expresión, necesitamos construirla con cuidado.
  # Una forma segura en bucles es crear una variable lógica temporal en el diseño
  
  # Truco: actualizamos el diseño temporalmente para filtrar fácil
  dsn_temp <- update(encuesta_dsn_total, filtro_temp = (get(col_conoce) == "Sí"))
  dsn_conocedores <- subset(dsn_temp, filtro_temp == TRUE)
  
  # Verificamos si hay datos suficientes
  if(nrow(dsn_conocedores) > 0) {
    formula_opinion <- as.formula(paste0("~", col_opinion))
    res_opinion <- svymean(formula_opinion, design = dsn_conocedores, na.rm = TRUE)
    
    cat("  -> Opinión (Entre quienes le conocen):\n")
    print(res_opinion)
    
  } else {
    cat("  -> No hay suficientes casos para opinar.\n")
  }
}

# -----------------------------------------------------------------------------
# 9. ANÁLISIS DE CALIFICACIONES (PROMEDIOS 1-10) - Q2 y Q8
# -----------------------------------------------------------------------------
# [cite: 8, 26-28]

# Función para calcular promedio ponderado
calc_promedio <- function(var_name, dsn) {
  form <- as.formula(paste0("~", var_name))
  # svymean calcula la media de una variable numérica
  res <- svymean(form, design = dsn, na.rm = TRUE)
  return(res)
}

cat("\n--- Calificación Presidente (1-10) ---\n")
# Asegúrate que q2_calif_chaves sea numérica en el dataframe inicial
print(calc_promedio("q2_calif_chaves", encuesta_dsn_total))

cat("\n--- Calificación Instituciones (1-10) ---\n")
cols_instituciones <- c("q8_tse", "q8_poderJudicial", "q8_fiscaliaGeneral", "q8_ucr", "q8_universidades", "q8_asamblea", "q8_gobierno", "q8_contraloria", "q8_iglesia", "q8_sindicatos", "q8_partidos", "q8_ministros", "q8_medios")

for(inst in cols_instituciones) {
  prom <- calc_promedio(inst, encuesta_dsn_total)
  cat(paste(inst, ": ", round(coef(prom), 2), "\n"))
}

# -----------------------------------------------------------------------------
# FIN DEL SCRIPT
# -----------------------------------------------------------------------------