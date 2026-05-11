from datetime import datetime
from enum import Enum
from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship
from sqlalchemy import JSON

# Define an Enum for dog status
class AdoptionStatus(Enum):
    AVAILABLE = 'Available'
    ADOPTED = 'Adopted'
    PENDING = 'Pending'

class Dog(BaseModel):
    __tablename__ = 'dogs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    breed_id = db.Column(db.Integer, db.ForeignKey('breeds.id'))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    description = db.Column(db.Text)
    
    # Relationship to Breed
    breed = relationship('Breed', backref='dogs')
    
    # Adoption status
    status = db.Column(db.Enum(AdoptionStatus), default=AdoptionStatus.AVAILABLE)
    intake_date = db.Column(db.DateTime, default=datetime.now)
    adoption_date = db.Column(db.DateTime, nullable=True)
    
    # AI-generated listing fields
    ai_generated = db.Column(db.Boolean, default=False)
    image_path = db.Column(db.String(500), nullable=True)
    seo_title = db.Column(db.String(200), nullable=True)
    seo_keywords = db.Column(JSON, nullable=True)  # List of keywords
    tags = db.Column(JSON, nullable=True)  # List of tags
    traits = db.Column(JSON, nullable=True)  # List of personality traits
    adoption_highlights = db.Column(JSON, nullable=True)  # Key selling points
    categories = db.Column(JSON, nullable=True)  # Listing categories
    size_estimate = db.Column(db.String(20), nullable=True)  # small/medium/large/extra-large
    age_confidence = db.Column(db.String(20), nullable=True)  # puppy/young/adult/senior
    
    @validates('name')
    def validate_name(self, key, name):
        return self.validate_string_length('Dog name', name, min_length=2)
    
    @validates('gender')
    def validate_gender(self, key, gender):
        if gender not in ['Male', 'Female', 'Unknown']:
            raise ValueError("Gender must be 'Male', 'Female', or 'Unknown'")
        return gender
    
    @validates('description')
    def validate_description(self, key, description):
        if description is not None:
            return self.validate_string_length('Description', description, min_length=10, allow_none=True)
        return description
    
    def __repr__(self):
        return f'<Dog {self.name}, ID: {self.id}, Status: {self.status.value}>'

    def to_dict(self):
        result = {
            'id': self.id,
            'name': self.name,
            'breed': self.breed.name if self.breed else None,
            'age': self.age,
            'gender': self.gender,
            'description': self.description,
            'status': self.status.name if self.status else 'UNKNOWN'
        }
        
        # Include AI-generated fields if present
        if self.ai_generated:
            result.update({
                'ai_generated': True,
                'image_path': self.image_path,
                'seo_title': self.seo_title,
                'seo_keywords': self.seo_keywords or [],
                'tags': self.tags or [],
                'traits': self.traits or [],
                'adoption_highlights': self.adoption_highlights or [],
                'categories': self.categories or [],
                'size_estimate': self.size_estimate,
                'age_confidence': self.age_confidence
            })
        
        return result