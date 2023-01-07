from os import environ

region = environ.get("AWS_REGION", None)
table_name = environ.get("DYNAMO_TABLE_NAME", None)
