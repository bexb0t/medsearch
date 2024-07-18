from medsearch_api.app.db import db
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
    Date,
    Text,
)
from sqlalchemy.sql import func

from sqlalchemy.orm import relationship


class SPL(db.Model):  # type: ignore
    __tablename__ = "spls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    set_id = Column(String(255), nullable=False, unique=True)
    title = Column(Text, nullable=False)
    published_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<SPL(set_id='{self.set_id}', title='{self.title}', published_date='{self.published_date}')>"

    # relationships
    meds = relationship("Med", back_populates="spl")  # type: ignore


class MedForm(db.Model):  # type: ignore
    __tablename__ = "med_forms"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(255))
    code_system = Column(String(255))
    name = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    # relationships
    meds = relationship("Med", back_populates="form")  # type: ignore


class Med(db.Model):  # type: ignore
    __tablename__ = "meds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    spl_id = Column(Integer, ForeignKey("spls.id"), nullable=False)
    med_form_id = Column(Integer, ForeignKey("med_forms.id"), nullable=False)
    code = Column(String(255))
    code_system = Column(String(255))
    name = Column(String(255))
    generic_name = Column(String(255))
    effective_date = Column(Date)
    version_number = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    # relationships
    form = relationship("MedForm", back_populates="meds")  # type: ignore
    spl = relationship("SPL", back_populates="meds", foreign_keys=[spl_id])  # type: ignore
    organization_maps = relationship("MedOrganizationMap", back_populates="med")  # type: ignore
    ingredient_maps = relationship("MedIngredientMap", back_populates="med")  # type: ignore


class Organization(db.Model):  # type: ignore
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    nih_id_extension = Column(String(255))
    nih_id_root = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    # relationships
    med_organization_maps = relationship(  # type: ignore
        "MedOrganizationMap", back_populates="organization"
    )


class MedOrganizationMap(db.Model):  # type: ignore
    __tablename__ = "med_organization_map"

    med_id = Column(Integer, ForeignKey("meds.id"), primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), primary_key=True)

    # relationships
    med = relationship("Med", back_populates="organization_maps", foreign_keys=[med_id])  # type: ignore
    organization = relationship(  # type: ignore
        "Organization", back_populates="med_organization_maps", foreign_keys=[org_id]
    )


class Ingredient(db.Model):  # type: ignore
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    code = Column(String(255))
    code_system = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    # relationships
    med_ingredient_maps = relationship("MedIngredientMap", back_populates="ingredient")  # type: ignore


class MedIngredientMap(db.Model):  # type: ignore
    __tablename__ = "med_ingredient_map"

    med_id = Column(Integer, ForeignKey("meds.id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), primary_key=True)

    # relationships
    med = relationship("Med", back_populates="ingredient_maps", foreign_keys=[med_id])  # type: ignore
    ingredient = relationship(  # type: ignore
        "Ingredient", back_populates="med_ingredient_maps", foreign_keys=[ingredient_id]
    )
