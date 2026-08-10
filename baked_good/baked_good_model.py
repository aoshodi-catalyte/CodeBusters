from pydantic import BaseModel, Field, field_validator, model_validator

class BakedGood(BaseModel):
    id: int
    active: bool
    name: str
    description: str
    purchasing_cost: float = Field(gt=0)
    retail_price: float = Field(gt=0)

    @field_validator("name")
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError("Name cannot be empty")
        return value


    @field_validator("description")
    def validate_description(cls, value):
        if not value.strip():
            raise ValueError("Description cannot be empty")
        return value

    @model_validator(mode="after")
    def validate_retail_price(self):
        if self.retail_price <= self.purchasing_cost:
            raise ValueError("Retail price must be greater than purchasing cost")
        return self

