import sys
from pyspark.sql import SparkSession

import crossref_processing as cp


def main(paths):
    spark = SparkSession.builder.appName("crossref").getOrCreate()

    raw = cp.read_raw(spark, paths)
    parquet_path = "output/crossref-parquet"
    cp.to_parquet_schema(raw).write.mode("overwrite").parquet(parquet_path)

    df = spark.read.parquet(parquet_path)

    (cp.articles_month_year(df)
        .coalesce(1).write.mode("overwrite").option("header", True)
        .csv("output/articles_month_year"))

    (cp.research_group(df)
        .coalesce(1).write.mode("overwrite").option("header", True)
        .csv("output/research_group"))

    (cp.research_areas_per_person(df)
        .coalesce(1).write.mode("overwrite")
        .json("output/research_areas_per_person"))

    (cp.person_most_references(df)
        .coalesce(1).write.mode("overwrite")
        .json("output/person_most_references"))

    (cp.percentile_of_references(df, 0.25)
        .coalesce(1).write.mode("overwrite").option("header", True)
        .csv("output/percentil_25"))

    (cp.percentile_of_references(df, 0.50)
        .coalesce(1).write.mode("overwrite").option("header", True)
        .csv("output/percentil_50"))

    (cp.percentile_of_references(df, 0.75)
        .coalesce(1).write.mode("overwrite").option("header", True)
        .csv("output/percentil_75"))

    spark.stop()


if __name__ == "__main__":
    paths = sys.argv[1:]
    if not paths:
        print("Uso: spark-submit programaestudiante.py crossref/*.json")
        sys.exit(1)
    main(paths)
