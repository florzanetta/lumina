# -*- coding: utf-8 -*-


def year_month_iterator(year_from, month_from, year_until, month_until):
    assert 1 <= month_from <= 12
    assert 1 <= month_until <= 12
    assert year_from <= year_until

    if year_from == year_until:
        assert month_from <= month_until

    month = month_from
    year = year_from

    while year < year_until or (year == year_until and month <= month_until):
        yield (year, month)
        month += 1
        if month > 12:
            month = 1
            year += 1
