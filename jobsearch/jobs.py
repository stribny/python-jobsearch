from sqlalchemy.orm import Session
from jobsearch.dataaccess import JobPost


def save(session: Session, posts: list[JobPost]) -> None:
    session.bulk_save_objects(posts)
    session.commit()


def update(session: Session, post: JobPost) -> None:
    session.add(post)
    session.commit()


def get_last(session: Session) -> JobPost:
    return session.query(JobPost).order_by(JobPost.id.desc()).first()


def get_labeled(session: Session) -> list[JobPost]:
    return session.query(JobPost).filter(JobPost.label != None).all()


def get_not_labeled(session: Session) -> list[JobPost]:
    return session.query(JobPost).filter(JobPost.label == None).all()


def get_next_for_labelling(session: Session) -> JobPost:
    return session.query(JobPost).filter(JobPost.label == None).first()
