# Instructivo de Lectura · Dashboard de Ventas Semanal Gran Plaza

## Estructura general

El dashboard tiene **dos vistas** seleccionables en la barra superior:
- **Vista Gerencia**: consolidado de todo el portafolio Gran Plaza.
- **Por Centro Comercial (CECO)**: detalle de un centro comercial específico, seleccionable mediante pestañas.

---

## Filtros disponibles

| Filtro | Descripción |
|---|---|
| **Semanas** (botones SEM #) | Selecciona una o varias semanas. Al activar múltiples semanas, los datos se acumulan. |
| **Foco** | Filtra entre: todas las marcas / solo Marcas Foco / sin Marcas Foco. |

---

## Indicadores KPI

### Vista Gerencia (portafolio completo)

| KPI | Qué mide | Cómo se calcula |
|---|---|---|
| **Venta Total Portafolio** | Ventas reales del período seleccionado | Suma de ventas de todos los CECOs y marcas en las semanas activas |
| **vs Año Anterior** | Variación porcentual respecto al mismo período del año anterior | `(venta actual / venta año anterior − 1) × 100` |
| **vs Presupuesto** | Nivel de cumplimiento del presupuesto asignado | `(venta actual / presupuesto) × 100` |
| **Marcas Reportando** | Marcas que enviaron ventas sobre el total esperado | Conteo de marcas con venta > 0 / meta total de marcas |
| **Marcas Foco** | Cobertura específica de las marcas estratégicas (foco) | Marcas foco con venta / total marcas foco definidas |
| **Tráfico** | Visitas acumuladas al centro comercial | Suma de tráfico por semana vs mismo período año anterior |
| **Mejor CECO** | Centro comercial con mayor crecimiento vs año anterior | CECO con el % más alto de variación vs año anterior |
| **CECO a Reforzar** | Centro comercial con peor desempeño relativo | CECO con el % más bajo (o mayor caída) vs año anterior |

### Vista Por Centro Comercial

Muestra los mismos KPIs de Venta, vs Año Anterior, vs Presupuesto, Marcas Reportando y Tráfico, pero filtrados exclusivamente para el CECO seleccionado.

---

## Semáforo de colores

Los chips de color en los KPIs y tablas siguen esta lógica:

| Color | vs Año Anterior | vs Presupuesto |
|---|---|---|
| **Verde** | ≥ 0 % | ≥ 100 % |
| **Amarillo** | Entre −5 % y 0 % | Entre 90 % y 100 % |
| **Rojo** | < −5 % | < 90 % |

---

## Gráficos y tablas principales

| Sección | Qué muestra |
|---|---|
| **Evolución Semanal** | Barras (venta real) + líneas (año anterior y presupuesto) semana a semana. El tooltip incluye el número de marcas comparables (mismas marcas que el año anterior). |
| **Ranking de CECOs** | Ordena los centros comerciales por venta real del período, con su % vs año anterior y vs presupuesto. |
| **Participación por Categoría** | Distribución de la venta total entre categorías (Moda, Comidas, Servicios, etc.) con barra proporcional. |
| **Cumplimiento de Presupuesto por CECO** | Barra horizontal por centro comercial, coloreada según el semáforo de presupuesto. |
| **Comparativo entre Centros** | Líneas de venta por semana para todos los CECOs superpuestas. |
| **Top 10 Mayor Crecimiento / Caída** | Marcas con mayor variación positiva o negativa vs año anterior en el período seleccionado. |
| **Marcas en Riesgo** | Marcas con mayor caída vs año anterior en la semana actual, dentro del CECO seleccionado. |
| **Tabla Todas las Marcas** | Detalle marca a marca con: Venta, vs Año Anterior, vs Presupuesto y **Días con venta** (días en que registró venta sobre días transcurridos en la semana). Permite ordenar por cualquier columna. |

---

## Notas clave de interpretación

- **Acumulado multi-semana**: al seleccionar varias semanas, todos los KPIs y gráficos reflejan la suma acumulada de ese rango, no el promedio.
- **Días con venta**: indica cuántos días de la semana la marca tuvo facturación registrada (ej. `4/5d` = reportó 4 de 5 días). Un valor bajo puede indicar cierre parcial o falta de reporte.
- **Mismas marcas**: el tooltip de Evolución Semanal muestra cuántas marcas son comparables con el año anterior, para dar contexto al dato de crecimiento.
- **Marcas Foco**: son marcas estratégicas predefinidas. Su cobertura se monitorea de forma independiente al total de marcas.
