from peewee import BlobField


class LongBlogField(BlobField):
    field_type = 'LONGBLOB'
