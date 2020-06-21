# -*- coding: utf-8 -*-
import pytest
import pyqtgraph as pg
from pyqtgraph.parametertree import Parameter


@pytest.mark.parametrize('passdefault', [True, False])
def test_parameter_hasdefault(passdefault):
    # test that hasDefault represents whether or not a default value is set
    opts = {'name': 'param', 'type': int, 'value': 0}
    if passdefault:
        opts['default'] = None

    p = Parameter(**opts)
    assert p.hasDefault() == passdefault
    assert p.defaultValue() is None

    p.setDefault(1)
    assert p.hasDefault()
    assert p.defaultValue() == 1
