import json

import crossref_processing as cp


sample = {
    "status": "ok",
    "message-type": "work",
    "message-version": "1.0.0",
    "message": {
        "DOI": "10.1101/sample",
        "prefix": "10.1101",
        "subtype": "preprint",
        "group-title": "Epidemiology",
        "created": {"date-time": "2020-05-14T22:46:23Z"},
        "author": [{"given": "Jane", "family": "Doe"}],
        "institution": [{"name": "Some University"}],
        "reference": [{"DOI": "10.1/a"}, {"DOI": None}],
        "link": [{"URL": "http://example.org"}],
    },
}


def write_sample(tmp_path, name, record):
    path = tmp_path / name
    path.write_text(json.dumps(record))
    return str(path)


def test_read_raw_loads_records(spark, tmp_path):
    f1 = write_sample(tmp_path, "a.json", sample)
    f2 = write_sample(tmp_path, "b.json", sample)

    df = cp.read_raw(spark, [f1, f2])

    assert df.count() == 2
    assert df.select("message.DOI").first()[0] == "10.1101/sample"


def test_to_parquet_schema_columns_and_values(spark, tmp_path):
    f1 = write_sample(tmp_path, "a.json", sample)

    df = cp.to_parquet_schema(cp.read_raw(spark, [f1]))

    expected = ["doi", "author", "inst", "groupTitle", "createdDate",
                "prefix", "reference", "link", "subtype"]
    assert df.columns == expected

    row = df.first()
    assert row["doi"] == "10.1101/sample"
    assert row["groupTitle"] == "Epidemiology"
    assert row["createdDate"] == "2020-05-14T22:46:23Z"
    assert row["subtype"] == "preprint"
