"""
Unit tests for the AI Listing Service.
Tests both mock mode and structure of responses.
"""
import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock

from services.ai_listing_service import (
    PetAnalysisResult,
    MOCK_RESPONSES,
    _encode_image_to_base64,
    _get_image_media_type,
    _mock_analyze
)


class TestPetAnalysisResult(unittest.TestCase):
    """Test the PetAnalysisResult dataclass."""
    
    def test_to_dict_returns_all_fields(self):
        """Test that to_dict includes all expected fields."""
        result = PetAnalysisResult(
            breed_primary="Golden Retriever",
            breed_secondary=None,
            estimated_age_years=2.5,
            age_confidence="young",
            size_estimate="large",
            gender_guess="male",
            detected_traits=["friendly", "playful"],
            generated_title="Meet Buddy: A Friendly Golden",
            emotional_description="A wonderful companion.",
            seo_keywords=["golden retriever", "adoption"],
            categories=["Large Dogs", "Family Friendly"],
            tags=["golden-retriever", "young"],
            adoption_highlights=["Great with kids"],
            missing_info_flags=[]
        )
        
        data = result.to_dict()
        
        self.assertEqual(data['breed_primary'], "Golden Retriever")
        self.assertEqual(data['breed_secondary'], None)
        self.assertEqual(data['estimated_age_years'], 2.5)
        self.assertEqual(data['age_confidence'], "young")
        self.assertEqual(data['size_estimate'], "large")
        self.assertEqual(data['gender_guess'], "male")
        self.assertEqual(data['detected_traits'], ["friendly", "playful"])
        self.assertIn("Buddy", data['generated_title'])
        self.assertIsInstance(data['seo_keywords'], list)
        self.assertIsInstance(data['categories'], list)
        self.assertIsInstance(data['tags'], list)
        self.assertIsInstance(data['adoption_highlights'], list)


class TestMockResponses(unittest.TestCase):
    """Test that mock responses are properly structured."""
    
    def test_mock_responses_exist(self):
        """Test that we have mock responses available."""
        self.assertGreater(len(MOCK_RESPONSES), 0)
    
    def test_mock_responses_have_required_fields(self):
        """Test all mock responses have required fields."""
        required_fields = [
            'breed_primary', 'estimated_age_years', 'age_confidence',
            'size_estimate', 'gender_guess', 'detected_traits',
            'generated_title', 'emotional_description', 'seo_keywords',
            'categories', 'tags', 'adoption_highlights', 'missing_info_flags'
        ]
        
        for i, mock in enumerate(MOCK_RESPONSES):
            data = mock.to_dict()
            for field in required_fields:
                self.assertIn(field, data, f"Mock response {i} missing field: {field}")
    
    def test_mock_responses_have_valid_values(self):
        """Test mock responses have valid enum values."""
        valid_age_confidence = ['puppy', 'young', 'adult', 'senior']
        valid_size = ['small', 'medium', 'large', 'extra-large']
        valid_gender = ['male', 'female', 'unknown']
        
        for mock in MOCK_RESPONSES:
            self.assertIn(mock.age_confidence, valid_age_confidence)
            self.assertIn(mock.size_estimate, valid_size)
            self.assertIn(mock.gender_guess, valid_gender)


class TestAnalyzePetImage(unittest.TestCase):
    """Test the analyze functions (using mock mode)."""
    
    def setUp(self):
        """Create a temporary test image."""
        # Create a minimal valid JPEG file
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, 'test_dog.jpg')
        
        # Minimal JPEG header (will be enough for our tests)
        jpeg_header = bytes([
            0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46,
            0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01,
            0x00, 0x01, 0x00, 0x00, 0xFF, 0xD9
        ])
        with open(self.test_image_path, 'wb') as f:
            f.write(jpeg_header)
    
    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_mock_analyze_returns_pet_analysis_result(self):
        """Test that mock analyze returns a PetAnalysisResult."""
        result = _mock_analyze(self.test_image_path)
        self.assertIsInstance(result, PetAnalysisResult)
    
    def test_mock_analyze_with_notes(self):
        """Test that mock analyze accepts additional notes."""
        result = _mock_analyze(
            self.test_image_path, 
            additional_notes="Name: Buddy, breed: Golden Retriever"
        )
        self.assertIsInstance(result, PetAnalysisResult)
    
    def test_mock_analyze_returns_valid_structure(self):
        """Test that mock analyze returns properly structured data."""
        result = _mock_analyze(self.test_image_path)
        
        # Check all required fields are present
        self.assertIsNotNone(result.breed_primary)
        self.assertIsNotNone(result.estimated_age_years)
        self.assertIn(result.age_confidence, ['puppy', 'young', 'adult', 'senior'])
        self.assertIn(result.size_estimate, ['small', 'medium', 'large', 'extra-large'])
        self.assertIn(result.gender_guess, ['male', 'female', 'unknown'])
        self.assertIsInstance(result.detected_traits, list)
        self.assertIsInstance(result.seo_keywords, list)
        self.assertIsInstance(result.tags, list)


class TestImageHelpers(unittest.TestCase):
    """Test image helper functions."""
    
    def test_get_image_media_type_jpeg(self):
        """Test JPEG media type detection."""
        self.assertEqual(_get_image_media_type('dog.jpg'), 'image/jpeg')
        self.assertEqual(_get_image_media_type('dog.jpeg'), 'image/jpeg')
    
    def test_get_image_media_type_png(self):
        """Test PNG media type detection."""
        self.assertEqual(_get_image_media_type('dog.png'), 'image/png')
    
    def test_get_image_media_type_gif(self):
        """Test GIF media type detection."""
        self.assertEqual(_get_image_media_type('dog.gif'), 'image/gif')
    
    def test_get_image_media_type_webp(self):
        """Test WebP media type detection."""
        self.assertEqual(_get_image_media_type('dog.webp'), 'image/webp')
    
    def test_encode_image_to_base64(self):
        """Test image encoding to base64."""
        # Create a temp file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(b'test image data')
            temp_path = f.name
        
        try:
            result = _encode_image_to_base64(temp_path)
            self.assertIsInstance(result, str)
            # Should be valid base64
            import base64
            decoded = base64.b64decode(result)
            self.assertEqual(decoded, b'test image data')
        finally:
            os.remove(temp_path)


if __name__ == '__main__':
    unittest.main()
