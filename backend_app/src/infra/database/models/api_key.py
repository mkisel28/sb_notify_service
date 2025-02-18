import uuid

from tortoise import fields
from tortoise.models import Model
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from infra.database.models.bot import Bot


class APIKey(Model):
  id = fields.UUIDField(primary_key=True, default=uuid.uuid4)
  key = fields.CharField("API-key", max_length=255, unique=True)
  bot: fields.ForeignKeyRelation["Bot"] = fields.ForeignKeyField(
      "models.bot",
      on_delete=fields.CASCADE,
      related_name="api_keys"
  )
  is_active = fields.BooleanField()
  created_at = fields.DatetimeField()
  updated_at = fields.DatetimeField()

  class Meta:
    table = "api_key"