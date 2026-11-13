"""Departamentos del Perú (código INEI) y provincias de Lima.

El MVP guarda el ubigeo a nivel de provincia ("DDPP00"); el distrito se pide
como texto. Suficiente para calcular la zona de envío.
"""

DEPARTMENTS = [
    ("01", "Amazonas"),
    ("02", "Áncash"),
    ("03", "Apurímac"),
    ("04", "Arequipa"),
    ("05", "Ayacucho"),
    ("06", "Cajamarca"),
    ("07", "Callao"),
    ("08", "Cusco"),
    ("09", "Huancavelica"),
    ("10", "Huánuco"),
    ("11", "Ica"),
    ("12", "Junín"),
    ("13", "La Libertad"),
    ("14", "Lambayeque"),
    ("15", "Lima"),
    ("16", "Loreto"),
    ("17", "Madre de Dios"),
    ("18", "Moquegua"),
    ("19", "Pasco"),
    ("20", "Piura"),
    ("21", "Puno"),
    ("22", "San Martín"),
    ("23", "Tacna"),
    ("24", "Tumbes"),
    ("25", "Ucayali"),
]

LIMA_PROVINCES = [
    ("01", "Lima (Lima Metropolitana)"),
    ("02", "Barranca"),
    ("03", "Cajatambo"),
    ("04", "Canta"),
    ("05", "Cañete"),
    ("06", "Huaral"),
    ("07", "Huarochirí"),
    ("08", "Huaura"),
    ("09", "Oyón"),
    ("10", "Yauyos"),
]

DEPARTMENT_NAMES = dict(DEPARTMENTS)


def build_ubigeo(department: str, lima_province: str | None) -> str:
    if department not in DEPARTMENT_NAMES:
        raise ValueError("Departamento inválido.")
    if department == "15":
        if lima_province not in dict(LIMA_PROVINCES):
            raise ValueError("Elige la provincia de Lima.")
        return f"15{lima_province}00"
    if department == "07":
        return "070100"
    return f"{department}0000"


def describe(ubigeo: str) -> str:
    name = DEPARTMENT_NAMES.get(ubigeo[:2], "")
    if ubigeo[:2] == "15":
        name = f"{dict(LIMA_PROVINCES).get(ubigeo[2:4], '')}, Lima"
    return name
