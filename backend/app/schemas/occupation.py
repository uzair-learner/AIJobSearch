from pydantic import BaseModel


class OccupationMetadataItem(BaseModel):
    id: int
    socCode: str
    socTitle: str
    professionCategory: str | None
