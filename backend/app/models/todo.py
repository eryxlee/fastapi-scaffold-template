from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref
from . import Base

class Todo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(127), nullable=False)
    description = Column(String(1000), nullable=True)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, nullable=False)

    # owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    # owner = relationship("User", back_populates="todos")
