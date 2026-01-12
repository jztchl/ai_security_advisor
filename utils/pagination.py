from typing import Generic, TypeVar, List, Optional, Type
from pydantic import BaseModel
from math import ceil

T = TypeVar('T')

class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int

def paginate(query, page: int, per_page: int, out_model: Optional[Type[BaseModel]] = None):
    total = query.count()
    rows = query.offset((page - 1) * per_page).limit(per_page).all()
    pages = ceil(total / per_page) if per_page > 0 else 0

    if out_model is not None:
        items = [out_model.model_validate(r) for r in rows]
    else:
        items = rows

    return Page(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )