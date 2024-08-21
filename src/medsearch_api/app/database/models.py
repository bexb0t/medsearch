from typing import cast
from medsearch_api.app.db import db
from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    DateTime,
    Date,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func

from sqlalchemy.orm import relationship

from medsearch_api.app.custom_types import OperationType


class MedSearchBaseModel(db.Model):  # type: ignore
    __abstract__ = True


class SPL(MedSearchBaseModel):
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
    spl_parsing_issues = relationship("SPLParsingIssue", back_populates="spl")  # type: ignore
    spl_data_issues = relationship("SPLDataIssue", back_populates="spl")  # type: ignore


class MedForm(MedSearchBaseModel):
    __tablename__ = "med_forms"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(255))
    code_system = Column(String(255))
    name = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<MedForm(id='{self.id}', code='{self.code}', code_system='{self.code_system}', name='{self.name}')>"

    __table_args__ = (UniqueConstraint("code", "code_system"),)

    # relationships
    meds = relationship("Med", back_populates="form")  # type: ignore


class Med(MedSearchBaseModel):
    __tablename__ = "meds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    spl_id = Column(Integer, ForeignKey("spls.id"), nullable=False, unique=True)
    med_form_id = Column(Integer, ForeignKey("med_forms.id"))
    code = Column(String(255))
    code_system = Column(String(255))
    name = Column(String(255))
    generic_name = Column(String(255))
    effective_date = Column(Date)
    version_number = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Med(id='{self.id}', spl_id='{self.spl_id}', med_form_id='{self.med_form_id}', code='{self.code}', code_system='{self.code_system}', name='{self.name}', generic_name='{self.generic_name}', effective_date='{self.effective_date}', version_number='{self.version_number}')>"

    # relationships
    form = relationship("MedForm", back_populates="meds")  # type: ignore
    spl = relationship("SPL", back_populates="meds", foreign_keys=[spl_id])  # type: ignore
    organization_maps = relationship("MedOrganizationMap", back_populates="med")  # type: ignore
    ingredient_maps = relationship("MedIngredientMap", back_populates="med")  # type: ignore


class Organization(MedSearchBaseModel):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    nih_id_extension = Column(String(255))
    nih_id_root = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Organization(id='{self.id}', name='{self.name}', nih_id_extension='{self.nih_id_extension}', nih_id_root='{self.nih_id_root}')>"

    __table_args__ = (UniqueConstraint("nih_id_extension", "nih_id_root"),)
    # relationships
    med_organization_maps = relationship(  # type: ignore
        "MedOrganizationMap", back_populates="organization"
    )


class MedOrganizationMap(MedSearchBaseModel):
    __tablename__ = "med_organization_map"

    med_id = Column(Integer, ForeignKey("meds.id"), primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), primary_key=True)

    def __repr__(self):
        return f"<MedOrganizationMap(med_id='{self.med_id}', org_id='{self.org_id}')>"

    # relationships
    med = relationship("Med", back_populates="organization_maps", foreign_keys=[med_id])  # type: ignore
    organization = relationship(  # type: ignore
        "Organization", back_populates="med_organization_maps", foreign_keys=[org_id]
    )


class Ingredient(MedSearchBaseModel):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    code = Column(String(255))
    code_system = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Ingredient(id='{self.id}', name='{self.name}', code='{self.code}', code_system='{self.code_system}')>"

    __table_args__ = (UniqueConstraint("code", "code_system"),)
    # relationships
    med_ingredient_maps = relationship("MedIngredientMap", back_populates="ingredient")  # type: ignore


class MedIngredientMap(MedSearchBaseModel):
    __tablename__ = "med_ingredient_map"

    med_id = Column(Integer, ForeignKey("meds.id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), primary_key=True)

    def __repr__(self):
        return f"<MedIngredientMap(med_id='{self.med_id}', ingredient_id='{self.ingredient_id}')>"

    # relationships
    med = relationship("Med", back_populates="ingredient_maps", foreign_keys=[med_id])  # type: ignore
    ingredient = relationship(  # type: ignore
        "Ingredient", back_populates="med_ingredient_maps", foreign_keys=[ingredient_id]
    )


class SPLParsingIssue(MedSearchBaseModel):
    __tablename__ = "spl_parsing_issues"
    id = Column(Integer, primary_key=True, autoincrement=True)
    spl_id = Column(Integer, ForeignKey("spls.id"))
    error = Column(Text)
    xml_content: Column = Column(LONGTEXT)
    xml_structure: Column = Column(LONGTEXT)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<SPLParsingIssue(id='{self.id}', spl_id='{self.spl_id}', error='{self.error}', xml_content='{self.xml_content}', xml_structure='{self.xml_structure}')>"

    # relationships
    spl = relationship("SPL", back_populates="spl_parsing_issues")  # type: ignore


class SPLDataIssue(MedSearchBaseModel):
    __tablename__ = "spl_data_issues"
    id = Column(Integer, primary_key=True, autoincrement=True)
    spl_id = Column(Integer, ForeignKey("spls.id"))
    operation_type: OperationType = cast(OperationType, Column(Enum(OperationType)))
    table_name = Column(String(128))
    error_message = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    # relationships
    spl = relationship("SPL", back_populates="spl_data_issues")  # type: ignore
