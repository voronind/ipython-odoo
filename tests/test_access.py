from ipython_odoo.access import from_polish_notation


def test_soma():
    access_node = from_polish_notation(['&', '1', '2'])
    assert access_node.value == '&'
    assert access_node.left.value == '1'
    assert access_node.right.value == '2'


def test_soma2():
    node = from_polish_notation(['|', '&', '1', '2', '3'])

    assert node.value == '|'
    assert node.left.value == '&'
    assert node.left.left.value == '1'
    assert node.left.right.value == '2'
    assert node.right.value == '3'
