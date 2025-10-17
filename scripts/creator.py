def fullname(record):
    type = record.type
    name = record.name
    lastname = record.lastname
    firstname = record.firstname
    alias = record.alias
    collective = record.collectiveName

    if type == 2:
        return collective
    else:
        if name:
            if alias:
                return name + ' (' + alias + ')'
            elif lastname:
                if firstname:
                    return name + ' (' + lastname + ', ' + firstname + ')'
                else:
                    return name + ' ' + lastname
            else:
                return name
        elif lastname:
            if firstname:
                return lastname + ', ' + firstname
            else:
                return lastname
        elif firstname:
            return firstname
        else:
            return ''
        
def objectQty(record):
    return len(record.objects)
    #return False

def textsearch(record):
    fields = ["alias", "collectiveName", "name", "lastname", "firstname","fullname"]
    textsearch = ""
    for field in fields:
        if getattr(record, field) and getattr(record, field) != "":
            textsearch += getattr(record, field) + " "
    return textsearch.strip()