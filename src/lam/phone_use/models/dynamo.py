from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, BooleanAttribute
from .. import table_name, region


class DynamoModel(Model):
    class Meta:
        table_name = table_name
        region = region

    phone_id = UnicodeAttribute(hash_key=True)
    epoch = NumberAttribute(range_key=True)
    uptime = NumberAttribute()
    battery = NumberAttribute()
    screen_state = BooleanAttribute()
