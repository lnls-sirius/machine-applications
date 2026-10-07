"""ID conv database."""


def get_propty_database(idname):
    """Return property database."""
    _ = idname
    dbase = {
        idname + ':Kx-Mon': {
            'type': 'float', 'value': 0, 'unit': '[K]', 'prec': 6
        },
    }
    return dbase
