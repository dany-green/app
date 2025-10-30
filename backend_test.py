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
        
    def log_test(self, test_name, success, message, response_time=None, request_data=None, response_data=None):
        """Log test result with detailed information"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "response_time": response_time,
            "request_data": request_data,
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time:.3f}s)" if response_time else ""
        print(f"{status}: {test_name} - {message}{time_info}")
        
    def create_sample_list_item(self, item_id, name, category, quantity, source):
        """Create a sample list item with proper structure"""
        return {
            "id": item_id,
            "name": name,
            "category": category,
            "quantity": quantity,
            "source": source
        }
        
    # ============== ФАЗА 1: ИНИЦИАЛИЗАЦИЯ И ПОДГОТОВКА ==============
    
    def test_database_initialization(self):
        """ФАЗА 1.1: Database initialization"""
        start_time = time.time()
        try:
            response = requests.post(f"{self.base_url}/init")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "ФАЗА 1.1: Database Initialization", 
                    True, 
                    f"Database initialized: {data.get('message', 'Success')}", 
                    response_time,
                    request_data=None,
                    response_data=data
                )
                return True
            else:
                self.log_test(
                    "ФАЗА 1.1: Database Initialization", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("ФАЗА 1.1: Database Initialization", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_authentication(self):
        """ФАЗА 1.2: Authentication"""
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
                        "ФАЗА 1.2: Authentication", 
                        True, 
                        "Successfully logged in and received JWT token", 
                        response_time,
                        request_data={"email": ADMIN_EMAIL, "password": "***"},
                        response_data={"access_token": "***", "token_type": data.get("token_type")}
                    )
                    return True
                else:
                    self.log_test(
                        "ФАЗА 1.2: Authentication", 
                        False, 
                        "No access token in response", 
                        response_time
                    )
                    return False
            else:
                self.log_test(
                    "ФАЗА 1.2: Authentication", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("ФАЗА 1.2: Authentication", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_create_projects(self):
        """ФАЗА 1.3: Create 3 test projects"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            projects_data = [
                {
                    "title": "Проект А - Тестирование списков",
                    "lead_decorator": "Декоратор А",
                    "project_date": "2024-01-15T10:00:00Z"
                },
                {
                    "title": "Проект Б - Изоляция данных",
                    "lead_decorator": "Декоратор Б", 
                    "project_date": "2024-01-20T14:00:00Z"
                },
                {
                    "title": "Проект В - Комплексное тестирование",
                    "lead_decorator": "Декоратор В",
                    "project_date": "2024-01-25T16:00:00Z"
                }
            ]
            
            created_projects = []
            
            for i, project_data in enumerate(projects_data):
                response = requests.post(f"{self.base_url}/projects", json=project_data, headers=headers)
                response_time = time.time() - start_time
                
                if response.status_code == 201:
                    data = response.json()
                    project_id = data.get("id")
                    if project_id:
                        created_projects.append(project_id)
                        if i == 0:
                            self.project_a_id = project_id
                        elif i == 1:
                            self.project_b_id = project_id
                        elif i == 2:
                            self.project_c_id = project_id
                    else:
                        self.log_test(
                            "ФАЗА 1.3: Create Projects", 
                            False, 
                            f"No project ID in response for project {i+1}", 
                            response_time
                        )
                        return False
                else:
                    self.log_test(
                        "ФАЗА 1.3: Create Projects", 
                        False, 
                        f"HTTP {response.status_code} for project {i+1}: {response.text}", 
                        response_time
                    )
                    return False
            
            self.log_test(
                "ФАЗА 1.3: Create Projects", 
                True, 
                f"Created 3 projects: А({self.project_a_id[:8]}...), Б({self.project_b_id[:8]}...), В({self.project_c_id[:8]}...)", 
                response_time,
                request_data=projects_data,
                response_data={"created_project_ids": created_projects}
            )
            return True
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("ФАЗА 1.3: Create Projects", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_create_inventory_items(self):
        """ФАЗА 1.4: Create 5 test inventory items"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            inventory_data = [
                {"category": "Вазы", "name": "Ваза хрустальная большая", "total_quantity": 8, "visual_marker": "🔴"},
                {"category": "Вазы", "name": "Ваза керамическая средняя", "total_quantity": 12, "visual_marker": "🔵"},
                {"category": "Текстиль", "name": "Скатерть льняная 2x3м", "total_quantity": 15, "visual_marker": "🟢"},
                {"category": "Декор", "name": "Свечи ароматические", "total_quantity": 25, "visual_marker": "🟡"},
                {"category": "Посуда", "name": "Тарелки фарфоровые", "total_quantity": 30, "visual_marker": "⚪"}
            ]
            
            for item_data in inventory_data:
                response = requests.post(f"{self.base_url}/inventory", json=item_data, headers=headers)
                
                if response.status_code == 201:
                    data = response.json()
                    item_id = data.get("id")
                    if item_id:
                        self.inventory_items.append({
                            "id": item_id,
                            "name": item_data["name"],
                            "category": item_data["category"],
                            "quantity": item_data["total_quantity"]
                        })
                    else:
                        response_time = time.time() - start_time
                        self.log_test(
                            "ФАЗА 1.4: Create Inventory Items", 
                            False, 
                            f"No item ID for {item_data['name']}", 
                            response_time
                        )
                        return False
                else:
                    response_time = time.time() - start_time
                    self.log_test(
                        "ФАЗА 1.4: Create Inventory Items", 
                        False, 
                        f"HTTP {response.status_code} for {item_data['name']}: {response.text}", 
                        response_time
                    )
                    return False
            
            response_time = time.time() - start_time
            self.log_test(
                "ФАЗА 1.4: Create Inventory Items", 
                True, 
                f"Created {len(self.inventory_items)} inventory items", 
                response_time,
                request_data=inventory_data,
                response_data={"created_items": len(self.inventory_items)}
            )
            return True
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("ФАЗА 1.4: Create Inventory Items", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_create_equipment_items(self):
        """ФАЗА 1.5: Create 5 test equipment items"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            equipment_data = [
                {"category": "Освещение", "name": "Прожектор LED 50W", "total_quantity": 10, "visual_marker": "💡"},
                {"category": "Звук", "name": "Микрофон беспроводной", "total_quantity": 6, "visual_marker": "🎤"},
                {"category": "Мебель", "name": "Стул банкетный", "total_quantity": 50, "visual_marker": "🪑"},
                {"category": "Техника", "name": "Проектор мультимедийный", "total_quantity": 3, "visual_marker": "📽️"},
                {"category": "Декор", "name": "Арка свадебная", "total_quantity": 2, "visual_marker": "🌸"}
            ]
            
            for item_data in equipment_data:
                response = requests.post(f"{self.base_url}/equipment", json=item_data, headers=headers)
                
                if response.status_code == 201:
                    data = response.json()
                    item_id = data.get("id")
                    if item_id:
                        self.equipment_items.append({
                            "id": item_id,
                            "name": item_data["name"],
                            "category": item_data["category"],
                            "quantity": item_data["total_quantity"]
                        })
                    else:
                        response_time = time.time() - start_time
                        self.log_test(
                            "ФАЗА 1.5: Create Equipment Items", 
                            False, 
                            f"No item ID for {item_data['name']}", 
                            response_time
                        )
                        return False
                else:
                    response_time = time.time() - start_time
                    self.log_test(
                        "ФАЗА 1.5: Create Equipment Items", 
                        False, 
                        f"HTTP {response.status_code} for {item_data['name']}: {response.text}", 
                        response_time
                    )
                    return False
            
            response_time = time.time() - start_time
            self.log_test(
                "ФАЗА 1.5: Create Equipment Items", 
                True, 
                f"Created {len(self.equipment_items)} equipment items", 
                response_time,
                request_data=equipment_data,
                response_data={"created_items": len(self.equipment_items)}
            )
            return True
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("ФАЗА 1.5: Create Equipment Items", False, f"Exception: {str(e)}", response_time)
            return False
    
    # ============== ФАЗА 2: БАЗОВОЕ ТЕСТИРОВАНИЕ СПИСКОВ ==============
            
    def test_add_preliminary_list(self):
        """ФАЗА 2.1: Add items to preliminary_list of Project A"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Create preliminary list with 2 items
            preliminary_items = [
                self.create_sample_list_item(
                    self.inventory_items[0]["id"], 
                    self.inventory_items[0]["name"], 
                    self.inventory_items[0]["category"], 
                    3, 
                    "inventory"
                ),
                self.create_sample_list_item(
                    self.equipment_items[0]["id"], 
                    self.equipment_items[0]["name"], 
                    self.equipment_items[0]["category"], 
                    2, 
                    "equipment"
                )
            ]
            
            update_data = {
                "preliminary_list": {
                    "items": preliminary_items
                }
            }
            
            response = requests.patch(f"{self.base_url}/projects/{self.project_a_id}", json=update_data, headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                saved_preliminary = data.get("preliminary_list", {})
                saved_items = saved_preliminary.get("items", [])
                
                if len(saved_items) == 2:
                    self.log_test(
                        "ФАЗА 2.1: Add Preliminary List", 
                        True, 
                        f"Added 2 items to preliminary_list of Project A", 
                        response_time,
                        request_data=update_data,
                        response_data={"preliminary_list": saved_preliminary}
                    )
                    return True
                else:
                    self.log_test(
                        "ФАЗА 2.1: Add Preliminary List", 
                        False, 
                        f"Expected 2 items, got {len(saved_items)}", 
                        response_time
                    )
                    return False
            else:
                self.log_test(
                    "ФАЗА 2.1: Add Preliminary List", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("ФАЗА 2.1: Add Preliminary List", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_verify_preliminary_list(self):
        """ФАЗА 2.2: Verify preliminary_list was saved correctly"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.get(f"{self.base_url}/projects/{self.project_a_id}", headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                preliminary_list = data.get("preliminary_list", {})
                items = preliminary_list.get("items", [])
                
                if len(items) == 2:
                    # Verify item structure
                    first_item = items[0]
                    required_fields = ["id", "name", "category", "quantity", "source"]
                    has_all_fields = all(field in first_item for field in required_fields)
                    
                    if has_all_fields:
                        self.log_test(
                            "ФАЗА 2.2: Verify Preliminary List", 
                            True, 
                            f"Preliminary list correctly saved with 2 items, all fields present", 
                            response_time,
                            response_data={"preliminary_list": preliminary_list}
                        )
                        return True
                    else:
                        self.log_test(
                            "ФАЗА 2.2: Verify Preliminary List", 
                            False, 
                            f"Missing required fields in items: {first_item}", 
                            response_time
                        )
                        return False
                else:
                    self.log_test(
                        "ФАЗА 2.2: Verify Preliminary List", 
                        False, 
                        f"Expected 2 items, found {len(items)}", 
                        response_time
                    )
                    return False
            else:
                self.log_test(
                    "ФАЗА 2.2: Verify Preliminary List", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("ФАЗА 2.2: Verify Preliminary List", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_add_final_list(self):
        """ФАЗА 2.3: Add items to final_list while preserving preliminary_list"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Create final list with 2 different items
            final_items = [
                self.create_sample_list_item(
                    self.inventory_items[1]["id"], 
                    self.inventory_items[1]["name"], 
                    self.inventory_items[1]["category"], 
                    5, 
                    "inventory"
                ),
                self.create_sample_list_item(
                    self.equipment_items[1]["id"], 
                    self.equipment_items[1]["name"], 
                    self.equipment_items[1]["category"], 
                    1, 
                    "equipment"
                )
            ]
            
            update_data = {
                "final_list": {
                    "items": final_items
                }
            }
            
            response = requests.patch(f"{self.base_url}/projects/{self.project_a_id}", json=update_data, headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                final_list = data.get("final_list", {})
                preliminary_list = data.get("preliminary_list", {})
                
                final_items_count = len(final_list.get("items", []))
                preliminary_items_count = len(preliminary_list.get("items", []))
                
                if final_items_count == 2 and preliminary_items_count == 2:
                    self.log_test(
                        "ФАЗА 2.3: Add Final List", 
                        True, 
                        f"Added final_list (2 items) while preserving preliminary_list (2 items)", 
                        response_time,
                        request_data=update_data,
                        response_data={"final_list": final_list, "preliminary_preserved": preliminary_items_count == 2}
                    )
                    return True
                else:
                    self.log_test(
                        "ФАЗА 2.3: Add Final List", 
                        False, 
                        f"Final: {final_items_count} items, Preliminary: {preliminary_items_count} items (expected 2 each)", 
                        response_time
                    )
                    return False
            else:
                self.log_test(
                    "ФАЗА 2.3: Add Final List", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("ФАЗА 2.3: Add Final List", False, f"Exception: {str(e)}", response_time)
            return False
            
    def test_add_dismantling_list(self):
        """ФАЗА 2.4: Add dismantling_list while preserving other lists"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Create dismantling list with 1 item
            dismantling_items = [
                self.create_sample_list_item(
                    self.inventory_items[2]["id"], 
                    self.inventory_items[2]["name"], 
                    self.inventory_items[2]["category"], 
                    1, 
                    "inventory"
                )
            ]
            
            update_data = {
                "dismantling_list": {
                    "items": dismantling_items
                }
            }
            
            response = requests.patch(f"{self.base_url}/projects/{self.project_a_id}", json=update_data, headers=headers)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                dismantling_list = data.get("dismantling_list", {})
                final_list = data.get("final_list", {})
                preliminary_list = data.get("preliminary_list", {})
                
                dismantling_count = len(dismantling_list.get("items", []))
                final_count = len(final_list.get("items", []))
                preliminary_count = len(preliminary_list.get("items", []))
                
                if dismantling_count == 1 and final_count == 2 and preliminary_count == 2:
                    self.log_test(
                        "ФАЗА 2.4: Add Dismantling List", 
                        True, 
                        f"All three lists present: preliminary(2), final(2), dismantling(1)", 
                        response_time,
                        request_data=update_data,
                        response_data={
                            "dismantling_list": dismantling_list,
                            "all_lists_preserved": True,
                            "counts": {"preliminary": preliminary_count, "final": final_count, "dismantling": dismantling_count}
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "ФАЗА 2.4: Add Dismantling List", 
                        False, 
                        f"Lists count - Preliminary: {preliminary_count}, Final: {final_count}, Dismantling: {dismantling_count}", 
                        response_time
                    )
                    return False
            else:
                self.log_test(
                    "ФАЗА 2.4: Add Dismantling List", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}", 
                    response_time
                )
                return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test("ФАЗА 2.4: Add Dismantling List", False, f"Exception: {str(e)}", response_time)
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