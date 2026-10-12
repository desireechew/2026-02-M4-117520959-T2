import crossref_processing as cp


def test_references_per_person_filters_missing_doi(make_df):
    rows = [
        ("10.1/a", [("Jane", "Doe")], None, None,
         [("10.1/x",), (None,), ("10.1/y",)]),
        ("10.1/b", [("Jane", "Doe")], None, None,
         [(None,)]),
        ("10.1/c", [("Bob", "Kim")], None, None, None),
    ]
    result = {r["full_name"]: r["total_references"]
              for r in cp.references_per_person(make_df(rows)).collect()}

    assert result["Jane Doe"] == 2
    assert "Bob Kim" not in result


def test_references_count_distinct_dois(make_df):
    rows = [
        ("10.1/a", [("Jane", "Doe")], None, None,
         [("10.1/x",), ("10.1/x",), ("10.1/y",)]),
        ("10.1/b", [("Jane", "Doe")], None, None,
         [("10.1/y",), ("10.1/z",)]),
    ]
    result = {r["full_name"]: r["total_references"]
              for r in cp.references_per_person(make_df(rows)).collect()}

    assert result["Jane Doe"] == 3


def test_references_credited_to_each_author(make_df):
    rows = [
        ("10.1/a", [("Jane", "Doe"), ("Bob", "Kim")], None, None,
         [("10.1/x",), ("10.1/y",)]),
    ]
    result = {r["full_name"]: r["total_references"]
              for r in cp.references_per_person(make_df(rows)).collect()}

    assert result["Jane Doe"] == 2
    assert result["Bob Kim"] == 2


def test_references_exclude_unknown(make_df):
    rows = [
        ("10.1/a", [(None, None)], None, None,
         [("10.1/x",), ("10.1/y",), ("10.1/z",)]),
        ("10.1/b", [("Jane", "Doe")], None, None, [("10.1/x",)]),
    ]
    result = {r["full_name"]: r["total_references"]
              for r in cp.references_per_person(make_df(rows)).collect()}

    assert "unknown" not in result
    assert result["Jane Doe"] == 1


def test_person_most_references_picks_top(make_df):
    rows = [
        ("10.1/a", [("Jane", "Doe")], None, None, [("10.1/x",), ("10.1/y",)]),
        ("10.1/b", [("Jane", "Doe")], None, None, [("10.1/z",)]),
        ("10.1/c", [("Bob", "Kim")], None, None, [("10.1/w",)]),
        ("10.1/d", [(None, None)], None, None,
         [("10.1/1",), ("10.1/2",), ("10.1/3",), ("10.1/4",), ("10.1/5",)]),
    ]
    result = cp.person_most_references(make_df(rows)).collect()

    assert len(result) == 1
    assert result[0]["full_name"] == "Jane Doe"
    assert result[0]["total_references"] == 3


def test_percentile_of_references(make_df):
    rows = [
        ("10.1/a", [("A", "A")], None, None, [("x",)]),
        ("10.1/b", [("B", "B")], None, None, [("x1",), ("y1",)]),
        ("10.1/c", [("C", "C")], None, None, [("x2",), ("y2",), ("z2",)]),
        ("10.1/d", [("D", "D")], None, None,
         [("x3",), ("y3",), ("z3",), ("w3",)]),
    ]
    df = make_df(rows)

    assert cp.percentile_of_references(df, 0.25).first()[0] == 1.75
    assert cp.percentile_of_references(df, 0.50).first()[0] == 2.5
    assert cp.percentile_of_references(df, 0.75).first()[0] == 3.25
