from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DeactivationLog(BaseModel):
    id: int

    entity_type: str
    entity_id: int
    entity_name: str

    related_entity_type: str
    related_entity_id: int
    related_entity_name: str

    reason: str
    error_message: str
    deactivated_at: datetime

    model_config = ConfigDict(from_attributes=True)
