import uuid
from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
  from infra.database.models.api_key import APIKey
  from infra.database.models.user import User


class Bot(Model):
  id = fields.UUIDField(primary_key=True, default=uuid.uuid4)
  name = fields.CharField(max_length=255)
  token = fields.CharField(max_length=255)
  owner: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
      "models.User",
      on_delete=fields.CASCADE,
      related_name="bots",
  )
  created_at = fields.DatetimeField()
  updated_at = fields.DatetimeField()

  api_keys: fields.ReverseRelation["APIKey"]

  class Meta:
    table = "bot"


