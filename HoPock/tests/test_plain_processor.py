from processors.plain import str2dict


def test_str2dict_coerces_numeric_overrides_to_numbers():
    overrides = str2dict('spaceAfter=10, textColor="green"')

    assert overrides == {'spaceAfter': 10, 'textColor': 'green'}
