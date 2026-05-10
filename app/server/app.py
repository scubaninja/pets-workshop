import os
import uuid
from functools import wraps
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, request, Response, session, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from models import init_db, db, Dog, Breed, User
from services.ai_listing_service import analyze_pet_image, PetAnalysisResult

# Get the server directory path
base_dir: str = os.path.abspath(os.path.dirname(__file__))

# Configure uploads folder
UPLOAD_FOLDER = os.path.join(base_dir, 'uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app: Flask = Flask(__name__)
db_path: str = os.environ.get('DATABASE_PATH', os.path.join(base_dir, 'dogshelter.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'tailspin-demo-secret-key')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for Astro frontend
CORS(app, supports_credentials=True, origins=['http://localhost:4321', 'http://127.0.0.1:4321'])

# Initialize the database with the app
init_db(app)

def current_user() -> Optional[User]:
    user_id = session.get('user_id')
    if not user_id:
        return None
    return db.session.get(User, user_id)


def staff_required(route):
    @wraps(route)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        if user.role != 'staff':
            return jsonify({'error': 'Staff access required'}), 403
        return route(*args, **kwargs)
    return wrapper


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_or_create_breed(breed_name: str) -> Breed:
    """Get existing breed or create new one if not found."""
    breed = Breed.query.filter(db.func.lower(Breed.name) == breed_name.lower()).first()
    if not breed:
        breed = Breed(name=breed_name, description=f"Auto-created breed: {breed_name}")
        db.session.add(breed)
        db.session.flush()  # Get the ID without committing
    return breed


@app.route('/api/auth/login', methods=['POST'])
def login() -> tuple[Response, int] | Response:
    payload = request.get_json(silent=True) or {}
    email = str(payload.get('email', '')).strip().lower()
    password = str(payload.get('password', ''))

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    session.clear()
    session['user_id'] = user.id
    return jsonify({'user': user.to_dict()})


@app.route('/api/auth/logout', methods=['POST'])
def logout() -> Response:
    session.clear()
    return jsonify({'ok': True})


@app.route('/api/auth/me', methods=['GET'])
def me() -> tuple[Response, int] | Response:
    user = current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    return jsonify({'user': user.to_dict()})


@app.route('/api/dogs', methods=['GET'])
def get_dogs() -> Response:
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 6, type=int)
    page = max(1, page)
    per_page = max(1, min(per_page, 100))

    query = db.session.query(
        Dog.id, 
        Dog.name, 
        Breed.name.label('breed'),
        Dog.ai_generated,
        Dog.image_path,
        Dog.seo_title
    ).join(Breed, Dog.breed_id == Breed.id).order_by(Dog.id.desc())
    
    total = query.count()
    dogs_query = query.offset((page - 1) * per_page).limit(per_page).all()
    
    dogs_list: List[Dict[str, Any]] = [
        {
            'id': dog.id,
            'name': dog.name,
            'breed': dog.breed,
            'ai_generated': dog.ai_generated or False,
            'image_path': dog.image_path,
            'seo_title': dog.seo_title
        }
        for dog in dogs_query
    ]
    
    return jsonify({
        'dogs': dogs_list,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': max(1, -(-total // per_page))
    })

@app.route('/api/dogs/<int:id>', methods=['GET'])
def get_dog(id: int) -> tuple[Response, int] | Response:
    # Query the specific dog by ID and join with breed to get breed name
    dog_query = db.session.query(
        Dog.id,
        Dog.name,
        Breed.name.label('breed'),
        Dog.age,
        Dog.description,
        Dog.gender,
        Dog.status,
        Dog.ai_generated,
        Dog.image_path,
        Dog.seo_title,
        Dog.seo_keywords,
        Dog.tags,
        Dog.traits,
        Dog.adoption_highlights,
        Dog.categories,
        Dog.size_estimate,
        Dog.age_confidence
    ).join(Breed, Dog.breed_id == Breed.id).filter(Dog.id == id).first()
    
    # Return 404 if dog not found
    if not dog_query:
        return jsonify({"error": "Dog not found"}), 404
    
    # Convert the result to a dictionary
    dog: Dict[str, Any] = {
        'id': dog_query.id,
        'name': dog_query.name,
        'breed': dog_query.breed,
        'age': dog_query.age,
        'description': dog_query.description,
        'gender': dog_query.gender,
        'status': dog_query.status.name
    }
    
    # Include AI-generated fields if present
    if dog_query.ai_generated:
        dog.update({
            'ai_generated': True,
            'image_path': dog_query.image_path,
            'seo_title': dog_query.seo_title,
            'seo_keywords': dog_query.seo_keywords or [],
            'tags': dog_query.tags or [],
            'traits': dog_query.traits or [],
            'adoption_highlights': dog_query.adoption_highlights or [],
            'categories': dog_query.categories or [],
            'size_estimate': dog_query.size_estimate,
            'age_confidence': dog_query.age_confidence
        })
    
    return jsonify(dog)


@app.route('/api/listing-agent/analyze', methods=['POST'])
@staff_required
def analyze_listing() -> tuple[Response, int]:
    """
    Analyze a pet image and return AI-generated listing data.
    
    Expects multipart/form-data with:
    - image: The pet image file
    - notes: Optional additional notes about the pet
    
    Returns structured AI analysis for preview before creating listing.
    """
    print("[API] /api/listing-agent/analyze called")
    print(f"[API] Files: {list(request.files.keys())}")
    print(f"[API] Form data: {dict(request.form)}")
    
    # Check if image was uploaded
    if 'image' not in request.files:
        print("[API] ERROR: No image in request")
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    print(f"[API] Image filename: {file.filename}")
    
    if file.filename == '':
        return jsonify({'error': 'No image file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: jpg, jpeg, png, gif, webp'}), 400
    
    # Generate unique filename and save
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)
    print(f"[API] Saved image to: {filepath}")
    
    # Get optional notes
    notes = request.form.get('notes', '')
    print(f"[API] Notes received: '{notes}'")
    
    try:
        # Analyze with AI service
        print("[API] Calling analyze_pet_image...")
        result: PetAnalysisResult = analyze_pet_image(filepath, notes)
        print(f"[API] Analysis complete. Title: {result.generated_title}")
        print(f"[API] Breed: {result.breed_primary}")
        
        return jsonify({
            'success': True,
            'image_filename': unique_filename,
            'analysis': result.to_dict()
        }), 200
        
    except ValueError as e:
        print(f"[API] ValueError: {e}")
        return jsonify({'error': str(e)}), 400
    except RuntimeError as e:
        print(f"[API] RuntimeError: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        print(f"[API] Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/dogs', methods=['POST'])
@staff_required
def create_dog() -> tuple[Response, int]:
    """
    Create a new dog listing from AI analysis.
    
    Expects JSON with:
    - name: Dog's name (required)
    - image_filename: Filename from analyze response (required)
    - analysis: The AI analysis object (required)
    - Override fields are optional (will use AI values if not provided)
    
    Auto-creates breed records if breed doesn't exist.
    """
    data = request.get_json(silent=True) or {}
    
    # Validate required fields
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Pet name is required'}), 400
    
    image_filename = data.get('image_filename', '').strip()
    if not image_filename:
        return jsonify({'error': 'Image filename is required'}), 400
    
    analysis = data.get('analysis')
    if not analysis:
        return jsonify({'error': 'Analysis data is required'}), 400
    
    # Verify image exists
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
    if not os.path.exists(image_path):
        return jsonify({'error': 'Image file not found'}), 400
    
    try:
        # Get or create breed
        breed_name = data.get('breed') or analysis.get('breed_primary', 'Unknown')
        breed = get_or_create_breed(breed_name)
        
        # Map gender from AI to model format
        gender_map = {'male': 'Male', 'female': 'Female', 'unknown': 'Unknown'}
        gender = gender_map.get(analysis.get('gender_guess', 'unknown').lower(), 'Unknown')
        
        # Calculate age in years (rounded to integer for the model)
        age_years = analysis.get('estimated_age_years', 1)
        age = max(1, round(age_years))
        
        # Create the dog record
        dog = Dog(
            name=name,
            breed_id=breed.id,
            age=age,
            gender=gender,
            description=analysis.get('emotional_description', ''),
            ai_generated=True,
            image_path=image_filename,
            seo_title=analysis.get('generated_title', ''),
            seo_keywords=analysis.get('seo_keywords', []),
            tags=analysis.get('tags', []),
            traits=analysis.get('detected_traits', []),
            adoption_highlights=analysis.get('adoption_highlights', []),
            categories=analysis.get('categories', []),
            size_estimate=analysis.get('size_estimate', ''),
            age_confidence=analysis.get('age_confidence', '')
        )
        
        db.session.add(dog)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'dog': dog.to_dict()
        }), 201
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create listing: {str(e)}'}), 500


@app.route('/api/images/<filename>')
def serve_image(filename: str) -> Response:
    """Serve uploaded pet images."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

## HERE

if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('FLASK_PORT', '5100'))) # Port 5100 to avoid macOS conflicts
