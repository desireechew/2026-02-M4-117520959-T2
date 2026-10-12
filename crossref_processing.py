from pyspark.sql import functions as F


def read_raw(spark, paths):
    return spark.read.option("multiLine", True).json(paths)


def to_parquet_schema(df):
    return df.select(
        F.col("message.DOI").alias("doi"),
        F.col("message.author").alias("author"),
        F.col("message.institution").alias("inst"),
        F.col("message.`group-title`").alias("groupTitle"),
        F.col("message.created.`date-time`").alias("createdDate"),
        F.col("message.prefix").alias("prefix"),
        F.col("message.reference").alias("reference"),
        F.col("message.link").alias("link"),
        F.col("message.subtype").alias("subtype"),
    )


def articles_month_year(df):
    ts = F.to_timestamp("createdDate")
    return (
        df.withColumn("ts", ts)
        .filter(F.col("ts").isNotNull())
        .withColumn("created_year", F.year("ts"))
        .withColumn("created_month", F.month("ts"))
        .groupBy("created_year", "created_month")
        .count()
        .withColumnRenamed("count", "total_articles")
        .orderBy("created_year", "created_month")
    )


def research_group(df):
    return (
        df.filter(F.col("groupTitle").isNotNull())
        .select("groupTitle", "doi")
        .distinct()
        .groupBy("groupTitle")
        .count()
        .select(
            F.col("groupTitle").alias("group_title"),
            F.col("count").alias("total"),
        )
        .orderBy(F.desc("total"), "group_title")
    )


def authors_with_names(df):
    author = F.explode("author").alias("a")
    exploded = df.select(author, "groupTitle", "reference")
    name = F.trim(F.concat_ws(" ", F.col("a.given"), F.col("a.family")))
    full_name = F.when(name == "", "unknown").otherwise(name)
    return exploded.withColumn("full_name", full_name)


def research_areas_per_person(df):
    return (
        authors_with_names(df)
        .groupBy("full_name")
        .agg(F.collect_set("groupTitle").alias("research_areas"))
        .withColumn("total", F.size("research_areas"))
        .orderBy(F.desc("total"), "full_name")
    )


def references_per_person(df):
    refs = (
        authors_with_names(df)
        .select("full_name", F.explode("reference").alias("ref"))
        .filter(F.col("ref.DOI").isNotNull())
        .filter(F.col("full_name") != "unknown")
    )
    return (
        refs.groupBy("full_name")
        .agg(F.countDistinct("ref.DOI").alias("total_references"))
    )


def person_most_references(df):
    return (
        references_per_person(df)
        .orderBy(F.desc("total_references"))
        .limit(1)
        .select("full_name", "total_references")
    )


def percentile_of_references(df, q):
    value = F.expr("percentile(total_references, {})".format(q))
    return references_per_person(df).select(value.alias("total_references"))
