#!/usr/bin/env python
# -*- coding: utf-8 -*-
import typing

import pandas as pd
from django.db import connection, connections


def close_connections():
    [conn.close_if_unusable_or_obsolete() for conn in connections.all()]


def read_sql_with_pandas(sql: str, params: typing.Union[typing.Tuple, typing.Dict] = ()) -> pd.DataFrame:
    with connection.cursor() as cursor:
        cursor.execute(sql, params=params)
        return pd.DataFrame([dict(zip([k[0] for k in cursor.description], result)) for result in cursor.fetchall()])
