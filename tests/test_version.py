import truffle


def test_version():
    assert truffle.__version__ == "0.1.0", "Version mismatch"
