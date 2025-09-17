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

    
    def test_integration_full_workflow(self):
        """Integration test - full workflow with tight validation"""
        print(f"\n--- INTEGRATION TEST: Full workflow validation ---")
        current_reason = f"integration-test-{datetime.now().strftime('%H%M%S')}"
        
        # Step 1: Generate CIDR
        print("Step 1: Generate CIDR")
        get_response = requests.get(f"http://localhost:8000/get-cidr?subnet_size=26&requiredrange=10&reason={current_reason}")
        self.assertEqual(get_response.status_code, 200)
        generated_cidr = get_response.text.strip()
        
        # Validate generated CIDR
        self.assertTrue(re.match(r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$', generated_cidr))
        network = IPv4Network(generated_cidr)
        self.assertEqual(network.prefixlen, 26)
        print(f"✅ Generated valid CIDR: {generated_cidr}")
        
        # Step 2: Test subnets from generated CIDR
        print("Step 2: Test subnets generation")
        subnets_response = requests.get(f"http://localhost:8000/get-subnets?subnet_size=28&cidr={generated_cidr}")
        self.assertEqual(subnets_response.status_code, 200)
        subnets_output = subnets_response.text.strip()
        subnets = subnets_output.split()
        self.assertEqual(len(subnets), 4)
        print(f"✅ Generated 4 valid subnets: {subnets_output}")
        
        # Step 3: Verify CIDR is in occupied list
        print("Step 3: Verify in occupied list")
        occupied_response = requests.get("http://localhost:8000/get-occupied-list")
        self.assertEqual(occupied_response.status_code, 200)
        occupied_data = json.loads(occupied_response.text)
        self.assertIn(generated_cidr, occupied_data.values())
        print(f"✅ CIDR found in occupied list")
        
        # Step 4: Delete CIDR
        print("Step 4: Delete CIDR")
        delete_response = requests.get(f"http://localhost:8000/delete-cidr-from-list?cidr_deletion={generated_cidr}")
        self.assertEqual(delete_response.status_code, 200)
        delete_output = delete_response.text.strip()
        expected_delete_pattern = rf'^CIDR {re.escape(generated_cidr)} deleted successfully.*$'
        self.assertTrue(re.match(expected_delete_pattern, delete_output))
        print(f"✅ CIDR deleted with correct message: {delete_output}")
        
        # Step 5: Verify CIDR removed from occupied list
        print("Step 5: Verify removal from occupied list")
        sleep(1)  # Allow time for propagation
        final_occupied_response = requests.get("http://localhost:8000/get-occupied-list")
        self.assertEqual(final_occupied_response.status_code, 200)
        final_occupied_data = json.loads(final_occupied_response.text)
        self.assertNotIn(generated_cidr, final_occupied_data.values())
        print(f"✅ CIDR successfully removed from occupied list")
        
        print(f"🎉 INTEGRATION TEST PASSED: Full workflow completed successfully")


if __name__ == '__main__':
    # Run with: python -m pytest tests/test_server.py -v
    # Or: python tests/test_server.py
    unittest.main(verbosity=2)
