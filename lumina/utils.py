# -*- coding: utf-8 -*-


def year_month_iterator(year_from, month_from, year_until, month_until):
    assert 1 <= month_from <= 12
    assert 1 <= month_until <= 12
    assert year_from <= year_until

    if year_from == year_until:
        assert month_from <= month_until

    yield "ok"
