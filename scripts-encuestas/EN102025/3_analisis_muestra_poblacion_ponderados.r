
# ==============================================================================
# 7. TABLA COMPARATIVA: MUESTRA BRUTA vs POBLACIÓN vs PONDERADA
# ==============================================================================

# NOTA: df_analisis (la base filtrada, category=1) ya tiene el ponderador_final.
# Reutilizaremos los objetos 'poblacion_conteo' y 'df_analisis'.

# 1. Distribución de la Muestra Bruta (n)
muestra_raw <- df_analisis_total %>% # Usamos la base total válida
    group_by(provincia, grupo_edad, sexo) %>%
    summarise(`Muestra Bruta (n)` = n(), .groups = 'drop')

# 2. Distribución de la Población (Conteo N)
poblacion_teorica <- poblacion_conteo %>%
    rename(`Población (N)` = conteo) %>%
    select(provincia, grupo_edad, sexo, `Población (N)`)

# 3. Distribución de la Muestra Ponderada (n_ponderada)
muestra_ponderada <- df_analisis_total %>% # Usamos la base total válida
    group_by(provincia, grupo_edad, sexo) %>%
    summarise(`Muestra Ponderada` = sum(ponderador_final), .groups = 'drop')

# 4. Merge y Formato

tabla_final <- muestra_raw %>%
    full_join(poblacion_teorica, by = c("provincia", "grupo_edad", "sexo")) %>%
    full_join(muestra_ponderada, by = c("provincia", "grupo_edad", "sexo")) %>%
    rename(
        Provincia = provincia,
        `Grupo Edad` = grupo_edad,
        Sexo = sexo
    )

# 5. Calcular Totales y Porcentajes
Total_Muestra_Bruta <- sum(tabla_final$`Muestra Bruta (n)`, na.rm = TRUE)
Total_Poblacion <- sum(tabla_final$`Población (N)`, na.rm = TRUE)
Total_Muestra_Ponderada <- sum(tabla_final$`Muestra Ponderada`, na.rm = TRUE)

tabla_final_distribucion <- tabla_final %>%
    mutate(
        `% Muestra Bruta` = round((`Muestra Bruta (n)` / Total_Muestra_Bruta) * 100, 2),
        `% Población` = round((`Población (N)` / Total_Poblacion) * 100, 2),
        `% Muestra Ponderada` = round((`Muestra Ponderada` / Total_Muestra_Ponderada) * 100, 2)
    ) %>%
    select(
        Provincia, `Grupo Edad`, Sexo,
        `Muestra Bruta (n)`, `% Muestra Bruta`,
        `Población (N)`, `% Población`,
        `Muestra Ponderada`, `% Muestra Ponderada`
    ) %>%
    arrange(Provincia, `Grupo Edad`, Sexo)

# 6. Agregar la fila de TOTALES
totales_row <- data.frame(
    Provincia = "TOTAL", `Grupo Edad` = "TOTAL", Sexo = "TOTAL",
    `Muestra Bruta (n)` = Total_Muestra_Bruta, `% Muestra Bruta` = 100.00,
    `Población (N)` = Total_Poblacion, `% Población` = 100.00,
    `Muestra Ponderada` = Total_Muestra_Ponderada, `% Muestra Ponderada` = 100.00
)

tabla_final_con_totales <- bind_rows(tabla_final_distribucion, totales_row)

# 7. IMPRIMIR TABLA FINAL USANDO KNITR
names(tabla_final_con_totales) <- gsub("\\.", " ", names(tabla_final_con_totales))

# cat("\n
# =================================================================================================\n
#    TABLA 7: DISTRIBUCIÓN DE MUESTRA BRUTA, POBLACIÓN Y MUESTRA PONDERADA POR CELDA DE PONDERACIÓN\n
# =================================================================================================\n")
# 
# kable(tabla_final_con_totales, 
#       digits = 2, 
#       format.args = list(big.mark = ",", decimal.mark = "."),
#       caption = "Distribución de la Muestra Bruta, Población y Muestra Ponderada (Post-Estratificación Sexo x Edad x Provincia)")


# ==============================================================================
# 8. EXPORTAR TABLA A CSV
# ==============================================================================

# 1. Reemplazar espacios por guiones bajos para que Excel los maneje mejor, y eliminamos el punto.
tabla_exportar <- tabla_final_con_totales
names(tabla_exportar) <- gsub(" ", "_", names(tabla_exportar))
names(tabla_exportar) <- gsub("\\.", "", names(tabla_exportar))

# 2. DEFINICIÓN DE LA RUTA Y EXPORTACIÓN
# ---
# IMPORTANTE: Cambia "C:/ruta/a/tu/carpeta/" por la ruta real donde quieres guardar el archivo.
ruta_archivo <- "C:\\Users\\vanev\\Downloads\\Opol EN102025\\DISTRIBUCION_MUESTRA_PONDERADA_FINAL.csv"

# Usamos write_csv para exportar. Especificamos el separador (;) para compatibilidad
# con versiones de Excel en español, y el decimal (.) que ya usamos.
write_csv(
    x = tabla_exportar,
    file = ruta_archivo,
    na = "", # Deja las celdas vacías si hay NA
    append = FALSE
)

# 3. Mensaje de Confirmación
cat(paste0("\n¡Exportación completada! El archivo ha sido guardado en:\n", ruta_archivo, "\n"))
