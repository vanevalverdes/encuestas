dict_fields = {
    "name": "AugustSurvey",
    "label": "Encuesta Agosto",
    "plural": "augustsurveys",
    'clazz_representation': '|id|,- |created_at|',
    "sort_field_results":"created_at|desc",
    "table_fields": " ID|id,Fecha|created_at",
    "search_fields": "id,created_at",
    "containers": {
        'AugustSurveyContainer': {
            'type': 'row',
            'class': 'col-sm-12',
            'title': None,
            'connected_table': '',
            'connected_table_fields': '',
            'fields': {
                'age': {
                    'id': 'age',
                    'type': 'String',
                    'maxlength': '',
                    'label': 'Edad',
                    'input': 'text',
                    'class': '',
                    'select_options': '',
                    'connected_table': '',
                    'required': '',
                    'hidden': '',
                    'defaultValue': ''
                },
                'gender': {
                    'id': 'gender',
                    'type': 'String',
                    'maxlength': '',
                    'label': 'Genero',
                    'input': 'text',
                    'class': '',
                    'select_options': '',
                    'connected_table': '',
                    'required': '',
                    'hidden': '',
                    'defaultValue': ''
                },
                'county': {
                    'id': 'county',
                    'type': 'String',
                    'maxlength': '',
                    'label': 'Cantón',
                    'input': 'text',
                    'class': '',
                    'select_options': '',
                    'connected_table': '',
                    'required': '',
                    'hidden': '',
                    'defaultValue': ''
                },
                'party': {
                    'id': 'party',
                    'type': 'String',
                    'maxlength': '',
                    'label': 'Con qué partido se identifica',
                    'input': 'text',
                    'class': '',
                    'select_options': '',
                    'connected_table': '',
                    'required': '',
                    'hidden': '',
                    'defaultValue': ''
                },
                'chavesSupport': {
                    'id': 'chavesSupport',
                    'type': 'String',
                    'maxlength': '',
                    'label': '¿Apoya la gestión del Presidente Rodrigo Chaves?',
                    'input': 'text',
                    'class': '',
                    'select_options': '',
                    'connected_table': '',
                    'required': '',
                    'hidden': '',
                    'defaultValue': ''
                },
                'nationalElection': {
                    'id': 'nationalElection',
                    'type': 'String',
                    'maxlength': '',
                    'label': 'Si las elecciones nacionales fueran hoy, ¿por quién votaría?',
                    'input': 'text',
                    'class': '',
                    'select_options': '',
                    'connected_table': '',
                    'required': '',
                    'hidden': '',
                    'defaultValue': ''
                },
                'congressParty': {
                    'id': 'congressParty',
                    'type': 'String',
                    'maxlength': '',
                    'label': 'Votaría por el mismo partido para diputados?',
                    'input': 'text',
                    'class': '',
                    'select_options': '',
                    'connected_table': '',
                    'required': '',
                    'hidden': '',
                    'defaultValue': ''
                },
                'contact': {
                    'id': 'contact',
                    'type': 'String',
                    'maxlength': '',
                    'label': 'Contacto',
                    'input': 'text',
                    'class': '',
                    'select_options': '',
                    'connected_table': '',
                    'required': '',
                    'hidden': '',
                    'defaultValue': ''
                },
                'userCreation': {
                    'id': 'userCreation',
                    'type': 'createdby',
                    'maxlength': '',
                    'label': 'Encuestador',
                    'input': 'text',
                    'class': '',
                    'select_options': '',
                    'connected_table': '',
                    'required': '',
                    'hidden': '',
                    'defaultValue': ''
                }
            }
        }
    }
}
