# -*- coding: utf-8 -*-
"""Define os modelos SQLAlchemy para a aplicação."""
import os

import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, JSON, Date, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

Base = declarative_base()

# Caminho absoluto para garantir persistência
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'rpg_panel.db')}"
engine = create_engine(DATABASE_URL, echo=False)


class Character(Base):
    """Modelo para representar um personagem."""
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True) # Nome deve ser único
    hp = Column(Integer, nullable=False, default=0)
    ac = Column(Integer, nullable=False, default=10)
    inspiration = Column(Boolean, default=False)
    slots = Column(JSON) # Armazena a estrutura de slots de magia
    abilities = Column(JSON) # Armazena a estrutura de habilidades
    notes = Column(String)

    def __repr__(self):
        return f"<Character(name='{self.name}', hp={self.hp}, ac={self.ac})>"

class Session(Base):
    """Modelo para representar uma sessão de jogo."""
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    number = Column(Integer, nullable=False, unique=True) # Número da sessão deve ser único
    floorName = Column(String)
    date = Column(Date, default=datetime.date.today)
    notes = Column(String)

    def __repr__(self):
        return f"<Session(number={self.number}, floorName='{self.floorName}', date='{self.date}')>"


import os

# Caminho absoluto para o banco de dados na mesma pasta deste arquivo
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'rpg_panel.db')}"

engine = create_engine(DATABASE_URL, echo=False)  # echo=True se quiser ver as queries no console

# Cria uma fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Função utilitária para obter uma sessão do banco de dados."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
