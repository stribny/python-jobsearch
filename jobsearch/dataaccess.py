from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy import (
    Column,
    Integer,
    String,
)

SQLALCHEMY_DATABASE_URL = "sqlite:///./instance/jobposts.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@contextmanager
def get_session() -> Session:
    session = SessionLocal()
    yield session
    session.close()


class JobPost(Base):
    __tablename__ = "job_posts"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    company = Column(String, nullable=False)
    position = Column(String, nullable=False)
    description = Column(String, nullable=False)
    location = Column(String, nullable=False)
    tags = Column(String, nullable=False)
    label = Column(Integer)

    @property
    def text(self):
        return "\n".join([
            self.company,
            self.position,
            self.description,
            self.tags,
            self.location
        ])


class JobPostLabel:
    NOT_INTERESTED = 0
    INTERESTED = 1


Base.metadata.create_all(bind=engine)





