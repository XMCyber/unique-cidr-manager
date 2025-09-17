import unittest
import requests
from ipaddress import IPv4Network
from time import sleep
from subprocess import Popen, PIPE
from datetime import datetime
import os
import re
import json


class TestAPI(unittest.TestCase):
    def setUp(self):
        # Get the environment variables and assign them to instance variables
        self.access_token = os.environ.get("ACCESS_TOKEN")
        self.occupied_repo = os.environ.get("OCCUPIED_REPO")
        self.occupied_file = os.environ.get("OCCUPIED_FILE")
        self.committer_email = os.environ.get("COMMITTER_EMAIL")
        self.committer_name = os.environ.get("COMMITTER_NAME")
        # Store the generated CIDR for use in other tests
        self.generated_cidr = None

    @classmethod
    def setUpClass(cls):
        # Start the server before tests
        cls.server_process = Popen(['python', 'server/main.py'])
        sleep(1)  # Wait for the server to start

    @classmethod
    def tearDownClass(cls):
        cls.server_process.terminate()  # Stop the server after tests

    def get_current_reason(self):
        time = datetime.now().strftime("%H:%M:%S")
        return f"test-{time}"

    
    def test_all_apis_integration_workflow(self):
        """COMPREHENSIVE INTEGRATION TEST - All APIs with tight output validation"""
        print(f"\n🚀 COMPREHENSIVE API TEST - All endpoints with tight validation")
        print("=" * 80)
        current_reason = f"integration-test-{datetime.now().strftime('%H%M%S')}"
        
        # TEST 1: get_cidr - output must be valid CIDR
        print("\n1️⃣ TESTING: get-cidr (output = valid CIDR)")
        get_response = requests.get(f"http://localhost:8000/get-cidr?subnet_size=26&requiredrange=10&reason={current_reason}")
        self.assertEqual(get_response.status_code, 200)
        generated_cidr = get_response.text.strip()
        print(f"   Output: '{generated_cidr}'")
        
        # TIGHT VALIDATION: Valid CIDR format
        cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
        self.assertTrue(re.match(cidr_pattern, generated_cidr), f"Invalid CIDR format: {generated_cidr}")
        network = IPv4Network(generated_cidr)
        self.assertEqual(network.prefixlen, 26, f"Expected /26, got /{network.prefixlen}")
        self.assertTrue(network.subnet_of(IPv4Network("10.0.0.0/8")), f"Not in 10.x range: {generated_cidr}")
        print(f"   ✅ PASSED: Valid CIDR format")
        
        # TEST 2: get_subnets_from_cidr - output must be 4 valid CIDRs with whitespaces
        print("\n2️⃣ TESTING: get-subnets (output = 4 valid CIDRs with whitespaces)")
        subnets_response = requests.get(f"http://localhost:8000/get-subnets?subnet_size=28&cidr={generated_cidr}")
        self.assertEqual(subnets_response.status_code, 200)
        subnets_output = subnets_response.text.strip()
        print(f"   Output: '{subnets_output}'")
        
        # TIGHT VALIDATION: 4 CIDRs with whitespaces
        subnets = subnets_output.split()
        self.assertEqual(len(subnets), 4, f"Expected 4 subnets, got {len(subnets)}")
        self.assertIn(' ', subnets_output, "Must contain whitespace separators")
        for i, subnet in enumerate(subnets):
            self.assertTrue(re.match(cidr_pattern, subnet), f"Invalid subnet format: {subnet}")
            subnet_network = IPv4Network(subnet)
            self.assertEqual(subnet_network.prefixlen, 28, f"Subnet {i+1} not /28: {subnet}")
            self.assertTrue(subnet_network.subnet_of(network), f"Subnet {subnet} not subset of {generated_cidr}")
        print(f"   ✅ PASSED: 4 valid CIDRs with whitespaces")
        
        # TEST 3: get_next_available - output must be valid CIDR
        print("\n3️⃣ TESTING: get-next-cidr-no-push (output = valid CIDR)")
        next_reason = f"next-{datetime.now().strftime('%H%M%S')}"
        next_response = requests.get(f"http://localhost:8000/get-next-cidr-no-push?subnet_size=26&requiredrange=10&reason={next_reason}")
        self.assertEqual(next_response.status_code, 200)
        next_cidr = next_response.text.strip()
        print(f"   Output: '{next_cidr}'")
        
        # TIGHT VALIDATION: Valid CIDR
        self.assertTrue(re.match(cidr_pattern, next_cidr), f"Invalid CIDR format: {next_cidr}")
        next_network = IPv4Network(next_cidr)
        self.assertEqual(next_network.prefixlen, 26, f"Expected /26, got /{next_network.prefixlen}")
        self.assertNotIn(' ', next_cidr, "Should be single CIDR without spaces")
        self.assertNotIn('\n', next_cidr, "Should be single line")
        print(f"   ✅ PASSED: Valid CIDR format")
        
        # TEST 4: get_occupied_list - output must be valid JSON
        print("\n4️⃣ TESTING: get-occupied-list (output = valid JSON)")
        occupied_response = requests.get("http://localhost:8000/get-occupied-list")
        self.assertEqual(occupied_response.status_code, 200)
        occupied_output = occupied_response.text.strip()
        print(f"   Output: JSON with {len(occupied_output)} characters")
        
        # TIGHT VALIDATION: Valid JSON
        try:
            occupied_data = json.loads(occupied_output)
        except (json.JSONDecodeError, ValueError) as e:
            self.fail(f"Invalid JSON response: {e}")
        
        self.assertIsInstance(occupied_data, dict, "Response must be JSON object/dictionary")
        self.assertIn(generated_cidr, occupied_data.values(), f"Generated CIDR {generated_cidr} not in occupied list")
        
        # Validate each CIDR in occupied list
        for key, cidr in occupied_data.items():
            if cidr:
                self.assertTrue(re.match(cidr_pattern, cidr), f"Invalid CIDR in occupied list: {cidr}")
                IPv4Network(cidr)  # Validate parseable
        print(f"   ✅ PASSED: Valid JSON with {len(occupied_data)} entries")
        
        # TEST 5: delete_cidr - output must be "CIDR {example} deleted successfully"
        print("\n5️⃣ TESTING: delete-cidr (output = 'CIDR {example} deleted successfully')")
        delete_response = requests.get(f"http://localhost:8000/delete-cidr-from-list?cidr_deletion={generated_cidr}")
        self.assertEqual(delete_response.status_code, 200)
        delete_output = delete_response.text.strip()
        print(f"   Output: '{delete_output}'")
        
        # TIGHT VALIDATION: Exact format "CIDR {cidr} deleted successfully"
        expected_delete_pattern = rf'^CIDR {re.escape(generated_cidr)} deleted successfully.*$'
        self.assertTrue(re.match(expected_delete_pattern, delete_output), 
                       f"Delete output doesn't match expected format. Got: {delete_output}")
        print(f"   ✅ PASSED: Correct delete message format")
        
        # FINAL VERIFICATION: CIDR removed from occupied list
        print("\n6️⃣ FINAL VERIFICATION: CIDR removed from occupied list")
        sleep(1)  # Allow time for propagation
        final_occupied_response = requests.get("http://localhost:8000/get-occupied-list")
        self.assertEqual(final_occupied_response.status_code, 200)
        final_occupied_data = json.loads(final_occupied_response.text)
        self.assertNotIn(generated_cidr, final_occupied_data.values(), 
                        f"CIDR {generated_cidr} should be removed from occupied list")
        print(f"   ✅ PASSED: CIDR successfully removed")
        
        print("\n" + "=" * 80)
        print("🎉 ALL API TESTS PASSED!")
        print("✅ get_cidr = valid CIDR")
        print("✅ get_subnets_from_cidr = 4 valid CIDRs with whitespaces") 
        print("✅ delete_cidr = 'CIDR {example} deleted successfully'")
        print("✅ get_next_available = valid CIDR")
        print("✅ get_occupied_list = valid JSON")
        print("✅ Full integration workflow = SUCCESS")
        print("=" * 80)


if __name__ == '__main__':
    # Run with: python -m pytest tests/test_server.py -v
    # Or: python tests/test_server.py
    unittest.main(verbosity=2)
