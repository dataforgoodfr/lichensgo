from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey, ARRAY, Boolean, Date, Text, Float, text
from sqlalchemy.orm import declarative_base, relationship
from my_data.db_connect import engine

Base = declarative_base()

class Environment(Base):
    __tablename__ = 'main_environment'
    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    name_en = Column(String)
    name_fr = Column(String)

    observations = relationship("Observation", back_populates="environment")

class Lichen(Base):
    __tablename__ = 'main_lichen'
    id = Column(BigInteger, primary_key=True)
    species_id = Column(BigInteger, ForeignKey('main_lichenspecies.id'), nullable=True)
    picture = Column(String(100))
    certitude = Column(Boolean, nullable=False)
    observation_id = Column(BigInteger, ForeignKey('main_observation.id'), nullable=False)

    species = relationship("LichenSpecies", back_populates="lichens")
    observation = relationship("Observation", back_populates="lichens")
    table_entries = relationship("Table", back_populates="lichen")

class LichenSpecies(Base):
    __tablename__ = 'main_lichenspecies'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    unique = Column(Boolean)
    name_en = Column(String(255))
    name_fr = Column(String(255))

    lichens = relationship("Lichen", back_populates="species")

class Observation(Base):
    __tablename__ = 'main_observation'
    id = Column(BigInteger, primary_key=True)
    date_obs = Column(Date, nullable=False)
    weather_cond = Column(String(255), nullable=False)
    school_obs = Column(Boolean, nullable=False)
    localisation_lat = Column(Float, nullable=False)
    localisation_long = Column(Float, nullable=False)
    comment = Column(Text)
    user_id = Column(BigInteger)
    validation = Column(String(100), nullable=False)
    env_type_link_id = Column(BigInteger, ForeignKey('main_environment.id'))

    environment = relationship("Environment", back_populates="observations")
    lichens = relationship("Lichen", back_populates="observation")
    trees = relationship("Tree", back_populates="observation")

class Table(Base):
    __tablename__ = "main_table"
    id = Column(BigInteger, primary_key=True)
    sq1 = Column(Boolean)
    sq2 = Column(Boolean)
    sq3 = Column(Boolean)
    sq4 = Column(Boolean)
    sq5 = Column(Boolean)
    lichen_id = Column(BigInteger, ForeignKey('main_lichen.id'))
    tree_id = Column(BigInteger, ForeignKey('main_tree.id'))

    lichen = relationship("Lichen", back_populates="table_entries")
    tree = relationship("Tree", back_populates="table_entries")

class Tree(Base):
    __tablename__ = 'main_tree'
    id = Column(BigInteger, primary_key=True)
    species_id = Column(BigInteger, ForeignKey('main_treespecies.id'))
    circonference = Column(Integer, nullable=False)
    shadow_face = Column(ARRAY(String(1)))
    young_lichens = Column(ARRAY(String(1)))
    dead_lichens = Column(ARRAY(String(1)))
    moss = Column(ARRAY(String(1)))
    observation_id = Column(BigInteger, ForeignKey('main_observation.id'), nullable=False)

    observation = relationship("Observation", back_populates="trees")
    species = relationship("TreeSpecies", back_populates="trees")
    table_entries = relationship("Table", back_populates="tree")

class TreeSpecies(Base):
    __tablename__ = 'main_treespecies'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255))
    name_fr = Column(String(255))

    trees = relationship("Tree", back_populates="species")

class LichenEcology(Base):
    __tablename__ = 'lichen_ecology'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    taxon = Column(String(255))
    pH = Column(String(255))
    aridity = Column(String(255))
    eutrophication = Column(String(255))
    poleotolerance = Column(String(255))
    cleaned_taxon = Column(String(255))

# Vue pour les fréquences
class LichenFrequency(Base):
    __tablename__ = 'lichen_frequency'
    __table_args__ = {'autoload_with': engine} 

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    id_site = Column(BigInteger)
    lichen = Column(String(255))
    ph = Column(String(255))
    freq = Column(Integer)
    eutrophication = Column(String(255))
    poleotolerance = Column(String(255))
    
    