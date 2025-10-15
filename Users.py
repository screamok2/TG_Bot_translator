from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.mutable import MutableDict

# База (файл users.db в папке проекта)
engine = create_engine("sqlite:///users.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Модель пользователя
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    vocabular = Column(MutableDict.as_mutable(JSON), default={})

    def __repr__(self):
        return f"User(id={self.user_id}, name={self.name}, vocabular={self.vocabular})"

# Создание таблиц
    Base.metadata.create_all(engine)

    @staticmethod
    def create_user(user_id: int, name: str, vocabular: dict = None):
        if vocabular is None:
            vocabular = {}
        user = User(user_id=user_id, name=name, vocabular=vocabular)
        session.add(user)
        session.commit()
        return user

    @staticmethod
    def search_user(user_id: int):
        return session.query(User).filter_by(user_id=user_id).first()

    @staticmethod
    def get_all_users():
        return session.query(User).all()

    def add_word(self, word: str, meaning: str):
        if not self.vocabular:
            self.vocabular = {}
        self.vocabular[word] = {

            "meaning" : meaning,
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        session.add(self)
        session.commit()



    def delete_last_word(self):

        last_word = list(self.vocabular.keys())[-1]

        # Удаляем его
        del self.vocabular[last_word]

        session.add(self)
        session.commit()
        return last_word

# Создание таблиц
Base.metadata.create_all(engine)