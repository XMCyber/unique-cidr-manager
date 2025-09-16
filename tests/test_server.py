import unittest
import requests
from ipaddress import IPv4Network
from time import sleep
from subprocess import Popen, PIPE
from datetime import datetime
import os


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

    def test_get_cidr_and_delete(self):
        """Test generating a CIDR and then deleting it using the GET method (old approach)"""
        current_reason = self.get_current_reason()
        
        # Step 1: Generate a new CIDR
        print(f"\n--- Generating CIDR with reason: {current_reason} ---")
        response = requests.get(f"http://localhost:8000/get-cidr?subnet_size=26&requiredrange=10&reason={current_reason}")
        self.assertEqual(response.status_code, 200)
        
        generated_cidr = response.text.strip()
        print(f"Generated CIDR: {generated_cidr}")
        
        # Store the generated CIDR for use in other tests
        self.generated_cidr = generated_cidr
        
        # Validate it's a proper CIDR
        self.assertTrue(IPv4Network(generated_cidr))
        
        # Step 2: Verify the CIDR is in the occupied list
        print(f"--- Verifying CIDR {generated_cidr} is in occupied list ---")
        occupied_response = requests.get("http://localhost:8000/get-occupied-list")
        self.assertEqual(occupied_response.status_code, 200)
        
        # The response is a JSON string, so we need to parse it
        occupied_data = occupied_response.json()
        # occupied_data is a dictionary where values are CIDR blocks
        cidr_found = generated_cidr in occupied_data.values()
        self.assertTrue(cidr_found, f"Generated CIDR {generated_cidr} should be in occupied list")
        print(f"✓ CIDR found in occupied list")
        
        # Step 3: Delete the CIDR using GET method (old approach)
        print(f"--- Deleting CIDR {generated_cidr} using GET method ---")
        delete_response = requests.get(f"http://localhost:8000/delete-cidr-from-list?cidr_deletion={generated_cidr}")
        self.assertEqual(delete_response.status_code, 200)
        
        delete_result = delete_response.text.strip()
        print(f"Delete response: {delete_result}")
        
        # Step 4: Verify the CIDR is no longer in the occupied list
        print(f"--- Verifying CIDR {generated_cidr} is removed from occupied list ---")
        sleep(1)  # Give it a moment for the deletion to propagate
        
        final_occupied_response = requests.get("http://localhost:8000/get-occupied-list")
        self.assertEqual(final_occupied_response.status_code, 200)
        
        final_occupied_data = final_occupied_response.json()
        # Check if the CIDR is still in the values of the dictionary
        cidr_still_exists = generated_cidr in final_occupied_data.values()
        self.assertFalse(cidr_still_exists, f"CIDR {generated_cidr} should be removed from occupied list")
        print(f"✓ CIDR successfully removed from occupied list")
        
        print(f"--- Test completed successfully ---")
    
    def test_get_subnets(self):
        # Use the CIDR generated in the previous test
        if self.generated_cidr is None:
            self.skipTest("No CIDR available from previous test - run test_get_cidr_and_delete first")
        
        print(f"\n--- Testing subnets for generated CIDR: {self.generated_cidr} ---")
        response = requests.get(f"http://localhost:8000/get-subnets?subnet_size=28&cidr={self.generated_cidr}")
        self.assertEqual(response.status_code, 200)
        print(f"Subnets response: {response.text}")
        self.assertTrue(all(IPv4Network(subnet) for subnet in response.text.split()))

    def test_get_next_cidr_no_push(self):
        current_reason = self.get_current_reason()
        response = requests.get(f"http://localhost:8000/get-next-cidr-no-push?subnet_size=26&requiredrange=10&reason={current_reason}")
        self.assertEqual(response.status_code, 200)
        print(response.text)
        self.assertTrue(IPv4Network(response.text))

    def test_get_occupied_list(self):
        response = requests.get(f"http://localhost:8000/get-occupied-list")
        self.assertEqual(response.status_code, 200)
        try:
            json_data = response.json()
            print
        except ValueError:
            self.fail("Response is not valid JSON")

if __name__ == '__main__':
    unittest.main()
