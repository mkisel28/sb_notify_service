import uuid
from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
  from infra.database.models.bot import Bot


class APIKey(Model):
  id = fields.UUIDField(primary_key=True, default=uuid.uuid4)
  key = fields.CharField(max_length=255)
  bot: fields.ForeignKeyRelation["Bot"] = fields.ForeignKeyField(
      "models.Bot",
      on_delete=fields.CASCADE,
      related_name="api_keys",
  )
  is_active = fields.BooleanField()
  created_at = fields.DatetimeField()
  updated_at = fields.DatetimeField()

  class Meta:
    table = "api_key"
