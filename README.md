# Tarea 2 - Procesamiento de datos Crossref con Apache Spark

Programa en PySpark que lee los archivos JSON del dataset Crossref (artículos
sobre COVID-19), los convierte a Parquet y a partir de ese Parquet genera una
serie de salidas con agregaciones y métricas.

## Requisitos

- Java 17 (Spark necesita una JVM).
- Python 3.9 o superior.
- PySpark y pytest (ver `requirements.txt`).

Instalación de las dependencias de Python:

```bash
pip3 install -r requirements.txt
```

Si no se tiene Java instalado, se puede usar un JDK (por ejemplo Temurin 17) y
apuntar `JAVA_HOME` hacia él antes de ejecutar:

```bash
export JAVA_HOME=/ruta/al/jdk-17/Contents/Home
export PATH="$JAVA_HOME/bin:$PATH"
```

## Ejecución

```bash
spark-submit programaestudiante.py crossref/*.json
```

El programa recibe las rutas de los archivos de entrada como argumentos. Cuando
la carpeta contiene muchos archivos, el patrón `crossref/*.json` puede superar
el límite de argumentos del shell. En ese caso se puede pasar la carpeta
directamente y Spark leerá todos los archivos:

```bash
spark-submit programaestudiante.py crossref
```

También funciona pasando el patrón entre comillas para que lo resuelva Spark:

```bash
spark-submit programaestudiante.py 'crossref/*.json'
```

Los archivos son JSON con formato multilínea (un objeto por archivo), por lo que
se leen con la opción `multiLine`.

## Salidas

Todas las salidas se escriben dentro de la carpeta `output`:

- `output/crossref-parquet`: los datos originales convertidos a Parquet con el
  esquema reducido (doi, author, inst, groupTitle, createdDate, prefix,
  reference, link, subtype). El resto de operaciones lee desde este Parquet.
- `output/articles_month_year`: cantidad de artículos creados por año y mes
  (`created_year`, `created_month`, `total_articles`), ordenado por año y mes.
- `output/research_group`: cantidad de artículos distintos por research group
  (`group_title`, `total`).
- `output/research_areas_per_person`: por persona, la lista de research groups
  distintos y su cantidad (`full_name`, `research_areas`, `total`), ordenado por
  `total`. El nombre vacío se reemplaza por `unknown`.
- `output/person_most_references`: la persona cuyos artículos acumulan más
  referencias distintas que contienen DOI (`full_name`, `total_references`).
- `output/percentil_25`, `output/percentil_50`, `output/percentil_75`: el valor
  de `total_references` que corresponde a cada percentil sobre la distribución
  de referencias por persona.

Cada salida se guarda como un único archivo usando `coalesce(1)`.

## Pruebas

```bash
pytest
```

Las pruebas construyen DataFrames pequeños con el mismo esquema del Parquet y
validan cada función del módulo `crossref_processing`, incluyendo casos como
fechas nulas, DOIs repetidos, nombres vacíos y referencias sin DOI.

## Notas sobre las decisiones

- En `research_group` y `research_areas_per_person` los conteos descartan
  repetidos: artículos distintos por DOI en el primer caso y research groups
  distintos por persona en el segundo.
- En `person_most_references` se cuentan las referencias distintas por DOI a lo
  largo de todos los artículos de la persona. El valor de referencia de la tarea
  (Florian Krammer con 2701) coincide con este conteo. El grupo `unknown`
  (nombres vacíos) no representa a una persona real, por lo que se excluye de
  este resultado y del cálculo de percentiles.
- Los percentiles usan la función exacta `percentile` de Spark sobre la columna
  `total_references`.
