from sqlalchemy import String, JSON, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base, TimestampMixin
import uuid

class DLQ(Base, TimestampMixin):
    __tablename__ = "sys_ingestion_dlq"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    origin_source: Mapped[str] = mapped_column(String(50))
    payload: Mapped[dict] = mapped_column(JSON)
    error_message: Mapped[str] = mapped_column(Text)
    error_type: Mapped[str | None] = mapped_column(String(50))
    retry_count: Mapped[int] = mapped_column(default=0)
    resolved: Mapped[bool] = mapped_column(default=False)
