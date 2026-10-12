import crossref_processing as cp


def test_articles_month_year_counts_and_order(make_df):
    rows = [
        ("10.1/a", None, "Epidemiology", "2020-05-14T22:46:23Z", None),
        ("10.1/b", None, "Epidemiology", "2020-05-20T10:00:00Z", None),
        ("10.1/c", None, "Biochemistry", "2020-03-01T10:00:00Z", None),
        ("10.1/d", None, "Biochemistry", None, None),
    ]
    result = cp.articles_month_year(make_df(rows)).collect()

    assert [(r["created_year"], r["created_month"], r["total_articles"]) for r in result] == [
        (2020, 3, 1),
        (2020, 5, 2),
    ]


def test_research_group_counts_distinct_articles(make_df):
    rows = [
        ("10.1/a", None, "Epidemiology", None, None),
        ("10.1/a", None, "Epidemiology", None, None),
        ("10.1/b", None, "Epidemiology", None, None),
        ("10.1/c", None, "Biochemistry", None, None),
        ("10.1/d", None, None, None, None),
    ]
    result = {r["group_title"]: r["total"] for r in cp.research_group(make_df(rows)).collect()}

    assert result == {"Epidemiology": 2, "Biochemistry": 1}


def test_research_areas_per_person(make_df):
    rows = [
        ("10.1/a", [("Jane", "Doe")], "Epidemiology", None, None),
        ("10.1/b", [("Jane", "Doe")], "Epidemiology", None, None),
        ("10.1/c", [("Jane", "Doe")], "Biochemistry", None, None),
        ("10.1/d", [(None, None)], "Virology", None, None),
    ]
    result = {r["full_name"]: (sorted(r["research_areas"]), r["total"])
              for r in cp.research_areas_per_person(make_df(rows)).collect()}

    assert result["Jane Doe"] == (["Biochemistry", "Epidemiology"], 2)
    assert result["unknown"] == (["Virology"], 1)


def test_research_areas_sorted_by_total_desc(make_df):
    rows = [
        ("10.1/a", [("Ann", "Lee")], "A", None, None),
        ("10.1/b", [("Ann", "Lee")], "B", None, None),
        ("10.1/c", [("Bob", "Kim")], "A", None, None),
    ]
    result = cp.research_areas_per_person(make_df(rows)).collect()

    assert result[0]["full_name"] == "Ann Lee"
    assert result[0]["total"] == 2
