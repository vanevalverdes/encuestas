def setup_jinja2(app):
    env = app.jinja_env
    env.trim_blocks = True
    env.lstrip_blocks = True
    def _safe_getattr(obj, attr):
        method_name = f'helper_{attr}'
        if hasattr(obj, method_name):
            print(f"Calling helper method: {method_name}")
            helper_function = getattr(obj, method_name)
            if callable(helper_function):
                print(f"Calling helper function: {helper_function}")
                result = helper_function()
                return result
        if hasattr(obj, attr):
            return getattr(obj, attr)
    env.filters['safe_getattr'] = _safe_getattr
    
    def urlencode_filter(s):
        if isinstance(s, dict):
            return urlencode(s)
        elif hasattr(s, 'to_dict'):
            return urlencode(s.to_dict(flat=False))
        return s
    env.filters['urlencode_filter'] = urlencode_filter

    def from_json_filter(s):
        import json
        try:
            return json.loads(s)
        except Exception:
            return {}
    env.filters['from_json'] = from_json_filter

    def to_json(s):
        import json
        try:
            return json.dumps(s)
        except Exception:
            return {}
    env.filters['to_json'] = to_json

    def get_connected_records(record,table_name):
        from utils.packages.application import getClazz
        plural = getClazz(table_name).getPlural()
        try:
            return getattr(record, plural)
        except Exception:
            return {}
    env.filters['get_connected_records'] = get_connected_records

    def get_clazz_fields(table_name):
        from utils.view_class_container_fields import get_clazz_fields
        #print(f"Getting fields for {table_name}")
        try:
            fields = get_clazz_fields(table_name)
            #print(f"Fields for {table_name}: {fields}")
            return fields
        except Exception:
            return {}
    env.filters['get_clazz_fields'] = get_clazz_fields

    def get_search_fields(table_name):
        from utils.packages.application import getClazz
        searchFields = getClazz(table_name).getSearchFields()
        return searchFields
    env.filters['get_search_fields'] = get_search_fields

    def get_clazz_details(table_name):
        from utils.packages.application import getClazzDetails
        searchFields = getClazzDetails(table_name)
        return searchFields
    env.filters['get_clazz_details'] = get_clazz_details

    def treeView(s):
        from utils.packages.application import getClazzName, getFieldTreeView
        from utils.packages.session import treeViewJson
        classname = getClazzName(s)
        #print(classname)
        #print(s)

        treeView = getFieldTreeView(s)
        #print(f"TreeView for {classname}: {treeView}")
        if not treeView.endswith("_id"):
            treeView = f"{treeView}_id"
        try:
            tree = treeViewJson(classname, treeView)
            return tree
        except Exception:
            return []
    env.filters['treeView'] = treeView
    
    def get_table_options(s):
        from utils.packages.session import getTable
        from utils.packages.application import getClazzName
        dict_options = {}
        try:
            class_table = getTable(s)
            print(f"Found {len(class_table)} records ")
            for record in class_table:
                dict_options[record.getORMRecord().__repr__()] = record.get("id")
            return dict_options
        except Exception:
            return {}
    env.filters['get_table_options'] = get_table_options

    def get_edit_url(s):
        from utils.packages.session import getEditUrlFromRecord
        try:
            edit_url = getEditUrlFromRecord(s)
            return edit_url
        except Exception:
            return {}
    env.filters['get_edit_url'] = get_edit_url

    def get_view_url(s):
        from utils.packages.session import getViewUrlFromRecord
        try:
            view_url = getViewUrlFromRecord(s)
            return view_url
        except Exception:
            return {}
    env.filters['get_view_url'] = get_view_url
    
    def money_format(amount,locale=False,symbol=False,grouping=False):
        from utils.packages.engine import newMoney
        if not amount:
            return ""
        money = newMoney(int(amount)).format(locale,symbol,grouping)
        return money
    env.filters['money_format'] = money_format

    def split_string(string, delimiter=","):
        originArray = string.split(delimiter)
        return originArray
    env.filters['split_string'] = split_string
    
    def get_values(array,value):
        result = []
        for item in array:
            result.append(getattr(item,value))
        return result
    env.filters['get_values'] = get_values

    def format_incomplete_date(date_str):
        """
        Toma una cadena de fecha de hasta 8 dígitos (AAAAMMDD), la rellena 
        con ceros a la derecha hasta 8 si es incompleta, y devuelve un array 
        [YYYY, MM, DD].
        
        Ejemplos:
        "2025"      -> "20250000" -> ["2025", "00", "00"]
        "202506"    -> "20250600" -> ["2025", "06", "00"]
        "20250630"  -> "20250630" -> ["2025", "06", "30"]
        """
        if not date_str or not isinstance(date_str, str):
            # Manejo de entrada no válida
            return ["0000", "00", "00"]

        # 1. Rellenar la cadena con ceros a la derecha hasta 8 dígitos
        padded_str = date_str.ljust(8, '0')

        # 2. Asegurarse de que no exceda los 8 dígitos
        if len(padded_str) > 8:
            padded_str = padded_str[:8]

        # 3. Extraer los componentes [YYYY, MM, DD]
        year = padded_str[0:4]
        month = padded_str[4:6]
        day = padded_str[6:8]
        
        # 4. Devolver la lista
        return [year, month, day]
    env.filters['format_incomplete_date'] = format_incomplete_date

    def size(s):
        size = len(s)
        return size
    env.filters['size'] = size

    def split_table_fields_definition(string):
        originArray = string.split(",")
        labels = []
        fields = []
        for i in originArray:
            item = i.split("|")
            labels.append(item)
            fields.append(item[1])
        result = {
            "labels": labels,
            "fields": fields
        }
        print(result)
        return result
    env.filters['split_table_fields_definition'] = split_table_fields_definition
