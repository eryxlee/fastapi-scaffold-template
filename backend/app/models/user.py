from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from . import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # 用户与TODO的关联关系可以在这里定义
    # todos = relationship("Todo", back_populates="owner")

    # def verify_password(self, raw_password):
    #     # 使用passlib验证密码
    #     return verify_password(raw_password, self.hashed_password)
