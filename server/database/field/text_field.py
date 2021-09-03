from peewee import TextField


class LongTextField(TextField):
    field_type = 'LONGTEXT'
