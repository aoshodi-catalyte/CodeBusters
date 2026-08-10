from pydantic import BaseModel, Field, field_validator

class BakedGood(BaseModel):
    id: int
    active: bool
    name: str
    description: str
    purchasing_cost: float = Field(ge=0)
    retail_price: float = Field(ge=0)

    @field_validator("name")
    def validate_description(cls, value):
        if not value.strip():
            raise ValueError("Name cannot be empty")
        return value


    @field_validator("description")
    def validate_description(cls, value):
        if not value.strip():
            raise ValueError("Description cannot be empty")
        return value
