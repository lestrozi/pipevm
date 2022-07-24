from pathlib import Path

root = "/tmp/pipevm"

def getPath(p):
    newPath = root + "/" + p
    Path(newPath).resolve().relative_to(root).resolve()
    return str(Path(newPath).resolve())

def test(p, expected):
    try:
        assert getPath(p) == expected, f"getPath({p}) returned {getPath(p)} instead of {expected}"
    except Exception as e:
        if not isinstance(e, expected):
            raise Exception(f"got {e}, expected {expected}")


test("/", "/tmp/pipevm")
test("bla", "/tmp/pipevm/bla")
test("/bla", "/tmp/pipevm/bla")
test("//bla", "/tmp/pipevm/bla")
test("../bla", ValueError)
test("/../bla", ValueError)
test("/bla/ble", "/tmp/pipevm/bla/ble")
test("/bla/ble/..", "/tmp/pipevm/bla")
test("/bla/ble/../", "/tmp/pipevm/bla")
test("/bla/ble/../..", "/tmp/pipevm")
test("/bla/ble/../../", "/tmp/pipevm")
test("/bla/ble/../../..", ValueError)

