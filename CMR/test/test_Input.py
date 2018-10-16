import pytest
import CMR.Input

@pytest.mark.parametrize("test_input,expected", [
    (1, '1'),
    (123, '123'),
    (-1, '-1'),
    ('1', '1'),
    ('-1', '-1'),
    ('-100', '-100'),
    (12345678901234567890123456789012345678901234567890, '12345678901234567890123456789012345678901234567890'),
    (-12345678901234567890123456789012345678901234567890, '-12345678901234567890123456789012345678901234567890'),
    (1.0, '1.0'),
    (1.2, '1.2'),
    ('1.0', '1.0'),
    ('1.2', '1.2'),
    ('1a', '1a'),
    ('a', 'a'),
    ('', ''),
    (' ', ' '),
    ('$', '$'),
    ('@', '@'),
    ('™', '™'),
    ('😕', '😕'),
    ([1, 2, 3], '[1, 2, 3]'),
    ({1, 2, 3}, '{1, 2, 3}')
])
def test_parse_string(test_input, expected):
    a = CMR.Input.parse_string(test_input)
    assert isinstance(a, str)
    assert a == expected
    
@pytest.mark.parametrize("test_input,expected", [
    (1, 1),
    (123, 123),
    (-1, -1),
    ('1', 1),
    ('-1', -1),
    ('-100', -100),
    (12345678901234567890123456789012345678901234567890, 12345678901234567890123456789012345678901234567890),
    (-12345678901234567890123456789012345678901234567890, -12345678901234567890123456789012345678901234567890),
    pytest.param(1.0, 1, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param(1.2, 1, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('1.0', 1, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('1.2', 1, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('1a', 1, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('a', 1, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('', 1, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param(' ', 1, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('$', 1, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('@', 1, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('™', 1, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('😕', 1, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param([1], 1, marks=pytest.mark.xfail(raises=TypeError)),
    pytest.param([1, 2, 3], 1, marks=pytest.mark.xfail(raises=TypeError))
])
def test_parse_int(test_input, expected):
    a = CMR.Input.parse_int(test_input)
    assert isinstance(a, int)
    assert a == expected
    
@pytest.mark.parametrize("test_input,expected", [
    (1, 1.0),
    (123, 123.0),
    (-1, -1.0),
    ('1', 1.0),
    ('-1', -1.0),
    ('-100', -100.0),
    (12345678901234567890123456789012345678901234567890, 12345678901234567890123456789012345678901234567890.0),
    (-12345678901234567890123456789012345678901234567890, -12345678901234567890123456789012345678901234567890.0),
    pytest.param(1.0, 1.0, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param(1.2, 1.2, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('1.0', 1.0, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('1.2', 1.2, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('1a', 1.0, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('a', 1.0, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('', 1.0, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param(' ', 1.0, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('$', 1.0, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('@', 1.0, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('™', 1.0, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param('😕', 1.0, marks=pytest.mark.xfail(raises=ValueError)),
    pytest.param([1], 1.0, marks=pytest.mark.xfail(raises=TypeError)),
    pytest.param([1, 2, 3], 1.0, marks=pytest.mark.xfail(raises=TypeError))
])
def test_parse_float(test_input, expected):
    a = CMR.Input.parse_float(test_input)
    assert isinstance(a, float)
    assert a == expected
    