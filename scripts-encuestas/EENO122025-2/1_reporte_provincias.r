# ==============================================================================
# SCRIPT DE EXPORTACIÓN: REPORTES PROVINCIALES DESAGREGADOS (12 CSVs)
# ==============================================================================

# 1. CONFIGURACIÓN DEL DIRECTORIO DE EXPORTACIÓN
# -----------------------------------------------

# !!! IMPORTANTE: Define la ruta base donde se guardarán los 12 archivos CSV.
# He creado una subcarpeta "Reportes_Analisis" para organizarlos.
ROOT_EXPORT_PATH <- "C:\\Users\\vanev\\Documents\\Opol\\Opol Segunda EEN - NOV25\\Reportes_Analisis\\" 


# 2. DEFINICIÓN DE CONFIGURACIONES DE ANÁLISIS
# ---------------------------------------------

# Definición de las variables de análisis y el diseño de encuesta (Base) a usar
analysis_config <- list(
    list(var = "voto_presidente", dsn = encuesta_dsn, base_name = "Voto_Presidente", note = "Base Votantes Válidos"),
    list(var = "voto_diputado", dsn = encuesta_dsn, base_name = "Voto_Diputado", note = "Base Votantes Válidos"),
    list(var = "partido_preferente", dsn = encuesta_dsn_total, base_name = "Filiacion_Partidaria", note = "Base Total Válida")
)

# Variables demográficas para desagregación
demographic_vars <- c("religion", "educacion", "sexo", "grupo_edad")


# 3. FUNCIÓN DE CÁLCULO Y EXPORTACIÓN
# -----------------------------------

process_and_export <- function(var_name, survey_design, group_var, base_name) {
    
    # A. Define las fórmulas de agrupamiento: ~provincia + variable_demográfica
    group_formula <- as.formula(paste("~provincia +", group_var))
    var_formula <- as.formula(paste("~", var_name))
    
    # B. Calcula la media ponderada (svymean) para el cruce de variables
    results_svyby <- svyby(var_formula, 
                           by = group_formula, 
                           design = survey_design, 
                           FUN = svymean, 
                           na.rm = TRUE)
    
    # C. Limpieza y formateo del resultado
    results_df <- results_svyby %>%
        select(-starts_with("se.")) %>% # Eliminar las columnas de Error Estándar (SE)
        as_tibble() %>%
        # Convertir a formato largo para mejor exportación
        pivot_longer(cols = starts_with(var_name),
                     names_to = "Categoria_Respuesta_Raw",
                     values_to = "Proporcion") %>%
        # Limpiar el nombre de la categoría de respuesta
        mutate(Categoria = gsub(paste0("^", var_name), "", Categoria_Respuesta_Raw)) %>%
        # Calcular el porcentaje final
        mutate(`Porcentaje (%)` = round(Proporcion * 100, 2)) %>%
        # Seleccionar columnas finales y renombrar
        select(
            Provincia = provincia, 
            Segmento_Demografico = !!sym(group_var), 
            Categoria, 
            `Porcentaje (%)`
        ) %>%
        arrange(Provincia, Segmento_Demografico, desc(`Porcentaje (%)`))
    
    # D. Define el nombre de archivo y exporta
    file_name <- paste0(base_name, "_by_", group_var, "_por_Provincia.csv")
    full_path <- file.path(ROOT_EXPORT_PATH, file_name)
    
    readr::write_csv(
        x = results_df, 
        file = full_path, 
        na = "",
        append = FALSE
    )
    
    cat(paste0("   - Exportado: ", file_name, "\n"))
}

# 4. BUCLE PRINCIPAL PARA EJECUTAR TODAS LAS COMBINACIONES
# --------------------------------------------------------

cat("======================================================================\n")
cat("  INICIANDO EXPORTACIÓN DE REPORTES PROVINCIALES DESAGREGADOS\n")
cat("======================================================================\n")

# Crear el directorio si no existe
dir.create(ROOT_EXPORT_PATH, recursive = TRUE, showWarnings = FALSE)
cat(paste0("Directorio de Exportación: ", ROOT_EXPORT_PATH, "\n\n"))

for (analysis in analysis_config) {
    cat(paste0("Analizando: ", analysis$base_name, " (", analysis$note, ")\n"))
    
    for (dem_var in demographic_vars) {
        process_and_export(
            var_name = analysis$var,
            survey_design = analysis$dsn,
            group_var = dem_var,
            base_name = analysis$base_name
        )
    }
    cat("\n")
}

cat("======================================================================\n")
cat("           ✅ PROCESO DE EXPORTACIÓN FINALIZADO\n")
cat("======================================================================\n")