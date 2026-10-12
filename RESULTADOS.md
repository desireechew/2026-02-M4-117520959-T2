# Resumen de resultados

Resultados obtenidos al ejecutar el programa sobre el dataset completo de
`crossref/`.

## Datos procesados

- 31458 artículos leídos y convertidos a Parquet con el esquema requerido.
- Las 8 salidas se generaron correctamente, cada una como archivo único.
- Las pruebas unitarias pasan: 12 de 12 con `pytest`.

## Resultados por salida

### articles_month_year

- 89 combinaciones de año y mes con artículos.
- Rango temporal: desde diciembre 2016 (1 artículo) hasta abril 2026 (50 artículos).
- La suma de `total_articles` es 31458, consistente con el total de artículos.

### research_group

- 74 research groups distintos.
- Grupos con más artículos distintos:

| group_title | total |
|-------------|-------|
| Infectious Diseases (except HIV/AIDS) | 8599 |
| Epidemiology | 5655 |
| Public and Global Health | 2850 |
| Microbiology | 2413 |
| Immunology | 1877 |

### research_areas_per_person

- 199592 personas (autores) en total.
- La fila con más áreas es `unknown` con 54, que es el agregado de nombres
  vacíos y no una persona real.
- La persona real con más áreas de investigación distintas es Yang Liu con 17,
  seguida de Yan Li y Yang Li con 16.

### person_most_references

- Florian Krammer con 2701 referencias distintas que contienen DOI.
- Coincide exactamente con el valor de control del enunciado, lo que valida la
  lógica de este apartado.

### Percentiles de total_references por persona

| percentil | total_references |
|-----------|------------------|
| 25 | 21 |
| 50 | 36 |
| 75 | 64 |

## Notas de interpretación

- En `research_group` y `research_areas_per_person` los conteos descartan
  repetidos: artículos distintos por DOI y research groups distintos por persona.
- En `person_most_references` y en los percentiles se excluye `unknown` por no
  representar a una persona real. Sin esa exclusión, `unknown` dominaría, ya que
  acumula 27588 referencias.
