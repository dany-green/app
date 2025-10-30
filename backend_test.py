#!/usr/bin/env python3
"""
Backend API Test Suite for SLS1 Organizational Platform
Comprehensive testing for project lists functionality (preliminary_list, final_list, dismantling_list)
"""

import requests
import json
import time
from io import BytesIO
from PIL import Image
import os
from pathlib import Path
import uuid

# Configuration
BACKEND_URL = "https://project-audit-tool-2.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@sls1.com"
ADMIN_PASSWORD = "admin123"

class ProjectListsTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.test_results = []
        
        # Test data storage
        self.project_a_id = None
        self.project_b_id = None
        self.project_c_id = None
        self.inventory_items = []
        self.equipment_items = []
        
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
        
    def create_test_image(self):
        """Create a test image (100x100 red square)"""
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes.getvalue()
        
    def test_database_initialization(self):
        """Test 1: Database initialization"""
        start_time = time.time()
        try:
            response = requests.post(f"{self.base_url}/init")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Database Initialization", 
                    True, 
                    f"Database initialized: {data.get('message', 'Success')}", 
                    response_time
                )
                return True
            else:
                self.log_test(
                    "Database Initialization", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("Database Initialization", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_authentication(self):
        """Test 2: Authentication"""
        start_time = time.time()
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                if self.token:
                    self.log_test(
                        "Authentication", 
                        True, 
                        "Successfully logged in and received token", 
                        response_time
                    )
                    return True
                else:
                    self.log_test(
                        "Authentication", 
                        False, 
                        "No access token in response", 
                        response_time
                    )
                    return False
            else:
                self.log_test(
                    "Authentication", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("Authentication", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_create_inventory_item(self):
        """Test 3: Create test inventory item"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            item_data = {
                "category": "Тестовая категория",
                "name": "Тестовый элемент для фото",
                "total_quantity": 5,
                "visual_marker": "📷",
                "description": "Элемент для тестирования фотографий"
            }
            
            response = requests.post(f"{self.base_url}/inventory", json=item_data, headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 201:
                data = response.json()
                self.test_item_id = data.get("id")
                if self.test_item_id:
                    self.log_test(
                        "Create Inventory Item", 
                        True, 
                        f"Created item with ID: {self.test_item_id}", 
                        response_time
                    )
                    return True
                else:
                    self.log_test(
                        "Create Inventory Item", 
                        False, 
                        "No item ID in response", 
                        response_time
                    )
                    return False
            else:
                self.log_test(
                    "Create Inventory Item", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("Create Inventory Item", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_image_upload(self):
        """Test 4: Upload image to inventory item"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Create test image
            image_data = self.create_test_image()
            
            files = {
                'file': ('test_image.png', image_data, 'image/png')
            }
            
            response = requests.post(
                f"{self.base_url}/inventory/{self.test_item_id}/images", 
                files=files, 
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.uploaded_image_url = data.get("image_url")
                if self.uploaded_image_url:
                    self.log_test(
                        "Image Upload", 
                        True, 
                        f"Image uploaded successfully: {self.uploaded_image_url}", 
                        response_time
                    )
                    return True
                else:
                    self.log_test(
                        "Image Upload", 
                        False, 
                        "No image URL in response", 
                        response_time
                    )
                    return False
            else:
                self.log_test(
                    "Image Upload", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("Image Upload", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_inventory_item_with_image(self):
        """Test 5: Verify image appears in inventory item"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.get(f"{self.base_url}/inventory/{self.test_item_id}", headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                images = data.get("images", [])
                if self.uploaded_image_url in images:
                    self.log_test(
                        "Inventory Item Image Check", 
                        True, 
                        f"Image found in inventory item: {len(images)} image(s)", 
                        response_time
                    )
                    return True
                else:
                    self.log_test(
                        "Inventory Item Image Check", 
                        False, 
                        f"Image not found in inventory item. Images: {images}", 
                        response_time
                    )
                    return False
            else:
                self.log_test(
                    "Inventory Item Image Check", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("Inventory Item Image Check", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_image_retrieval(self):
        """Test 6: Retrieve uploaded image"""
        start_time = time.time()
        try:
            # Extract the path from the image URL
            # URL format: /api/uploads/{item_id}/{filename}
            if not self.uploaded_image_url:
                self.log_test("Image Retrieval", False, "No uploaded image URL available", 0)
                return False
                
            # The uploaded_image_url should be a relative path like /api/uploads/{item_id}/{filename}
            # We need to make a request to the full URL
            image_url = f"{self.base_url.replace('/api', '')}{self.uploaded_image_url}"
            
            response = requests.get(image_url)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # Check if it's actually an image
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type or len(response.content) > 0:
                    self.log_test(
                        "Image Retrieval", 
                        True, 
                        f"Image retrieved successfully, size: {len(response.content)} bytes", 
                        response_time
                    )
                    return True
                else:
                    self.log_test(
                        "Image Retrieval", 
                        False, 
                        f"Response not an image. Content-Type: {content_type}", 
                        response_time
                    )
                    return False
            else:
                self.log_test(
                    "Image Retrieval", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("Image Retrieval", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_image_deletion(self):
        """Test 7: Delete uploaded image"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            params = {"image_url": self.uploaded_image_url}
            
            response = requests.delete(
                f"{self.base_url}/inventory/{self.test_item_id}/images", 
                params=params, 
                headers=headers
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Image Deletion", 
                    True, 
                    f"Image deleted successfully: {data.get('message', 'Success')}", 
                    response_time
                )
                return True
            else:
                self.log_test(
                    "Image Deletion", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("Image Deletion", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_image_deleted_from_inventory(self):
        """Test 8: Verify image is removed from inventory item"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.get(f"{self.base_url}/inventory/{self.test_item_id}", headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                images = data.get("images", [])
                if self.uploaded_image_url not in images:
                    self.log_test(
                        "Image Deletion Verification", 
                        True, 
                        f"Image successfully removed from inventory item. Remaining: {len(images)} image(s)", 
                        response_time
                    )
                    return True
                else:
                    self.log_test(
                        "Image Deletion Verification", 
                        False, 
                        f"Image still found in inventory item. Images: {images}", 
                        response_time
                    )
                    return False
            else:
                self.log_test(
                    "Image Deletion Verification", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("Image Deletion Verification", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_unauthorized_access(self):
        """Test 9: Test access control (unauthorized request)"""
        start_time = time.time()
        try:
            # Try to upload image without token
            image_data = self.create_test_image()
            files = {
                'file': ('test_image.png', image_data, 'image/png')
            }
            
            response = requests.post(
                f"{self.base_url}/inventory/{self.test_item_id}/images", 
                files=files
                # No Authorization header
            )
            response_time = time.time() - start_time
            
            if response.status_code in [401, 403]:
                self.log_test(
                    "Unauthorized Access Control", 
                    True, 
                    f"Correctly rejected unauthorized request (HTTP {response.status_code})", 
                    response_time
                )
                return True
            else:
                self.log_test(
                    "Unauthorized Access Control", 
                    False, 
                    f"Expected 401 or 403, got HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("Unauthorized Access Control", False, f"Exception: {str(e)}", response_time)
            return False
            
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 80)
        print("SLS1 Backend API Image Functionality Test Suite")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Admin Credentials: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print("=" * 80)
        
        tests = [
            self.test_database_initialization,
            self.test_authentication,
            self.test_create_inventory_item,
            self.test_image_upload,
            self.test_inventory_item_with_image,
            self.test_image_retrieval,
            self.test_image_deletion,
            self.test_image_deleted_from_inventory,
            self.test_unauthorized_access
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Empty line between tests
            
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Image functionality is working correctly.")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. See details above.")
            
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            time_info = f" ({result['response_time']:.3f}s)" if result.get("response_time") else ""
            print(f"{status} {result['test']}: {result['message']}{time_info}")
            
        return passed == total

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)