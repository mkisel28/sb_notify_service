import uuid
from typing import TYPE_CHECKING

from tortoise import fields
from tortoise.models import Model

if TYPE_CHECKING:
  from infra.database.models.bot import Bot

class User(Model):
  id = fields.UUIDField(primary_key=True, default=uuid.uuid4)
  bots: fields.ReverseRelation["Bot"]

  class Meta:
    table = "user"
