import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    ArrayType,
)


@pytest.fixture(scope="session")
def spark():
    session = (
        SparkSession.builder
        .master("local[1]")
        .appName("tests")
        .config("spark.sql.shuffle.partitions", "1")
        .getOrCreate()
    )
    yield session
    session.stop()


author_type = ArrayType(StructType([
    StructField("given", StringType()),
    StructField("family", StringType()),
]))

reference_type = ArrayType(StructType([
    StructField("DOI", StringType()),
]))

parquet_schema = StructType([
    StructField("doi", StringType()),
    StructField("author", author_type),
    StructField("groupTitle", StringType()),
    StructField("createdDate", StringType()),
    StructField("reference", reference_type),
])


@pytest.fixture
def make_df(spark):
    def _make(rows):
        return spark.createDataFrame(rows, parquet_schema)
    return _make
