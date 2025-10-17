def getFirstRecord(record):
    """
    Calcula y devuelve el objeto Blob asociado a la imagen más reciente.
    Se calcula automáticamente cada vez que se accede, pero requiere una consulta.
    """
    # Como la relación 'images' está ordenada por created_at.desc(),
    # el primer elemento [0] es el más reciente.
    if record.images:
        # record.images[0] es el objeto Image más reciente
        return record.images[0].image
    return None


def getLastLocation(record):
    """
    Calcula y devuelve el objeto Blob asociado a la imagen más reciente.
    Se calcula automáticamente cada vez que se accede, pero requiere una consulta.
    """
    # Como la relación 'images' está ordenada por created_at.desc(),
    # el primer elemento [0] es el más reciente.
    if record.locationlogs:
        # record.images[0] es el objeto Image más reciente
        return record.locationlogs[0]
    return None