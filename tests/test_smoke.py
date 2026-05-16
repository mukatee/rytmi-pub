import rytmi


def test_version():
    assert rytmi.__version__ == "0.1.0"


def test_import():
    from rytmi import __version__

    assert isinstance(__version__, str)
