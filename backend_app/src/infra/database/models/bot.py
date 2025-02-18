import uuid

from tortoise import fields
from tortoise.models import Model

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from infra.database.models.api_key import APIKey
  from infra.database.models.user import User


class Bot(Model):
  id = fields.UUIDField(primary_key=True, default=uuid.uuid4)
  name = fields.CharField()
  token = fields.CharField()
  owner: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
      "models.user",
      on_delete=fields.CASCADE,
      related_name="bots"
  )
  created_at = fields.DatetimeField()
  updated_at = fields.DatetimeField()

  api_keys: fields.ReverseRelation["APIKey"]

  class Meta:
    table = "bot"


