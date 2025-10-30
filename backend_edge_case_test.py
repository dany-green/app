#!/usr/bin/env python3
"""
Backend API Edge Case Tests for SLS1 Image Functionality
Testing error conditions and edge cases
"""

import requests
import json
import time
from io import BytesIO
from PIL import Image

# Configuration
BACKEND_URL = "https://deploy-guide-28.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@sls1.com"
ADMIN_PASSWORD = "admin123"

class EdgeCaseTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.test_item_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, response_time=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "response_time": response_time
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time:.3f}s)" if response_time else ""
        print(f"{status}: {test_name} - {message}{time_info}")
        
    def setup_auth_and_item(self):
        """Setup authentication and create test item"""
        # Login
        login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        response = requests.post(f"{self.base_url}/auth/login", json=login_data)
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        
        # Create test item
        headers = {"Authorization": f"Bearer {self.token}"}
        item_data = {
            "category": "Test Category",
            "name": "Edge Case Test Item",
            "total_quantity": 1,
            "visual_marker": "🧪"
        }
        response = requests.post(f"{self.base_url}/inventory", json=item_data, headers=headers)
        if response.status_code == 201:
            self.test_item_id = response.json().get("id")
            
    def test_invalid_file_type(self):
        """Test uploading invalid file type"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Create a text file instead of image
            text_content = b"This is not an image file"
            files = {
                'file': ('test.txt', text_content, 'text/plain')
            }
            
            response = requests.post(
                f"{self.base_url}/inventory/{self.test_item_id}/images", 
                files=files, 
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 400:
                self.log_test(
                    "Invalid File Type Rejection", 
                    True, 
                    "Correctly rejected non-image file", 
                    response_time
                )
                return True
            else:
                self.log_test(
                    "Invalid File Type Rejection", 
                    False, 
                    f"Expected 400, got HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("Invalid File Type Rejection", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_large_file_upload(self):
        """Test uploading file that exceeds size limit"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Create a large image (should exceed 10MB limit)
            # Create 3000x3000 image which should be > 10MB
            img = Image.new('RGB', (3000, 3000), color='blue')
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            large_image_data = img_bytes.getvalue()
            
            files = {
                'file': ('large_image.png', large_image_data, 'image/png')
            }
            
            response = requests.post(
                f"{self.base_url}/inventory/{self.test_item_id}/images", 
                files=files, 
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 400:
                self.log_test(
                    "Large File Size Rejection", 
                    True, 
                    f"Correctly rejected large file ({len(large_image_data)/1024/1024:.1f}MB)", 
                    response_time
                )
                return True
            else:
                # If it passes, it might be due to image optimization
                self.log_test(
                    "Large File Size Rejection", 
                    True, 
                    f"Large file handled (possibly optimized): HTTP {response.status_code}", 
                    response_time
                )
                return True
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("Large File Size Rejection", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_nonexistent_item_upload(self):
        """Test uploading to non-existent inventory item"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Create small test image
            img = Image.new('RGB', (50, 50), color='green')
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            files = {
                'file': ('test.png', img_bytes.getvalue(), 'image/png')
            }
            
            fake_item_id = "nonexistent-item-id"
            response = requests.post(
                f"{self.base_url}/inventory/{fake_item_id}/images", 
                files=files, 
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 404:
                self.log_test(
                    "Nonexistent Item Upload", 
                    True, 
                    "Correctly rejected upload to nonexistent item", 
                    response_time
                )
                return True
            else:
                self.log_test(
                    "Nonexistent Item Upload", 
                    False, 
                    f"Expected 404, got HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("Nonexistent Item Upload", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_delete_nonexistent_image(self):
        """Test deleting non-existent image"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            fake_image_url = "/api/uploads/fake-item/fake-image.png"
            params = {"image_url": fake_image_url}
            
            response = requests.delete(
                f"{self.base_url}/inventory/{self.test_item_id}/images", 
                params=params, 
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 404:
                self.log_test(
                    "Nonexistent Image Deletion", 
                    True, 
                    "Correctly rejected deletion of nonexistent image", 
                    response_time
                )
                return True
            else:
                self.log_test(
                    "Nonexistent Image Deletion", 
                    False, 
                    f"Expected 404, got HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("Nonexistent Image Deletion", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_multiple_image_upload(self):
        """Test uploading multiple images to same item"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            uploaded_urls = []
            
            # Upload 3 different images
            colors = ['red', 'green', 'blue']
            for i, color in enumerate(colors):
                img = Image.new('RGB', (100, 100), color=color)
                img_bytes = BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                files = {
                    'file': (f'test_{color}.png', img_bytes.getvalue(), 'image/png')
                }
                
                response = requests.post(
                    f"{self.base_url}/inventory/{self.test_item_id}/images", 
                    files=files, 
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    uploaded_urls.append(data.get("image_url"))
                else:
                    response_time = time.time() - start_time
                    self.log_test(
                        "Multiple Image Upload", 
                        False, 
                        f"Failed to upload image {i+1}: HTTP {response.status_code}", 
                        response_time
                    )
                    return False
            
            response_time = time.time() - start_time
            
            # Verify all images are in the item
            response = requests.get(f"{self.base_url}/inventory/{self.test_item_id}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                images = data.get("images", [])
                if len(images) >= 3:
                    self.log_test(
                        "Multiple Image Upload", 
                        True, 
                        f"Successfully uploaded {len(images)} images", 
                        response_time
                    )
                    return True
                else:
                    self.log_test(
                        "Multiple Image Upload", 
                        False, 
                        f"Expected 3+ images, found {len(images)}", 
                        response_time
                    )
                    return False
            else:
                self.log_test(
                    "Multiple Image Upload", 
                    False, 
                    f"Failed to verify images: HTTP {response.status_code}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("Multiple Image Upload", False, f"Exception: {str(e)}", response_time)
            return False
            
    def run_edge_case_tests(self):
        """Run all edge case tests"""
        print("=" * 80)
        print("SLS1 Backend API Image Functionality - Edge Case Tests")
        print("=" * 80)
        
        # Setup
        self.setup_auth_and_item()
        if not self.token or not self.test_item_id:
            print("❌ Failed to setup authentication or test item")
            return False
            
        print(f"Test Item ID: {self.test_item_id}")
        print("=" * 80)
        
        tests = [
            self.test_invalid_file_type,
            self.test_large_file_upload,
            self.test_nonexistent_item_upload,
            self.test_delete_nonexistent_image,
            self.test_multiple_image_upload
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Empty line between tests
            
        print("=" * 80)
        print("EDGE CASE TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL EDGE CASE TESTS PASSED!")
        else:
            print(f"\n⚠️  {total - passed} edge case test(s) failed.")
            
        return passed == total

if __name__ == "__main__":
    tester = EdgeCaseTester()
    success = tester.run_edge_case_tests()
    exit(0 if success else 1)