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

    def test_get_cidr_output_validation(self):
        """TIGHT TEST: get_cidr - output must be valid CIDR format"""
        current_reason = self.get_current_reason()
        
        print(f"\n--- TIGHT TEST: get-cidr output validation ---")
        response = requests.get(f"http://localhost:8000/get-cidr?subnet_size=26&requiredrange=10&reason={current_reason}")
        self.assertEqual(response.status_code, 200)
        
        output = response.text.strip()
        print(f"get-cidr output: '{output}'")
        
        # TIGHT VALIDATION: Must be valid CIDR format (IP/prefix)
        cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
        self.assertTrue(re.match(cidr_pattern, output), f"Output '{output}' is not in valid CIDR format")
        
        # TIGHT VALIDATION: Must be parseable as IPv4Network
        try:
            network = IPv4Network(output)
            print(f"✅ Valid CIDR: {network}")
        except ValueError as e:
            self.fail(f"Output '{output}' is not a valid IPv4 CIDR: {e}")
        
        # TIGHT VALIDATION: Must be /26 subnet as requested
        self.assertEqual(network.prefixlen, 26, f"Expected /26 subnet, got /{network.prefixlen}")
        
        # TIGHT VALIDATION: Must be in 10.0.0.0/8 range as requested
        self.assertTrue(network.subnet_of(IPv4Network("10.0.0.0/8")), f"CIDR {output} is not in 10.0.0.0/8 range")
        
        # Store for other tests
        self.generated_cidr = output
        print(f"✅ TIGHT TEST PASSED: get-cidr returned valid CIDR: {output}")
        
    def test_delete_cidr_output_validation(self):
        """TIGHT TEST: delete_cidr - output must be 'CIDR {example} deleted successfully'"""
        if not hasattr(self, 'generated_cidr') or self.generated_cidr is None:
            # Generate a CIDR first for testing deletion
            test_reason = self.get_current_reason()
            response = requests.get(f"http://localhost:8000/get-cidr?subnet_size=26&requiredrange=10&reason={test_reason}")
            self.assertEqual(response.status_code, 200)
            self.generated_cidr = response.text.strip()
        
        print(f"\n--- TIGHT TEST: delete-cidr output validation ---")
        delete_response = requests.get(f"http://localhost:8000/delete-cidr-from-list?cidr_deletion={self.generated_cidr}")
        self.assertEqual(delete_response.status_code, 200)
        
        output = delete_response.text.strip()
        print(f"delete-cidr output: '{output}'")
        
        # TIGHT VALIDATION: Must match exact format "CIDR {cidr} deleted successfully"
        expected_pattern = rf'^CIDR {re.escape(self.generated_cidr)} deleted successfully.*$'
        self.assertTrue(re.match(expected_pattern, output), 
                       f"Output '{output}' does not match expected format 'CIDR {self.generated_cidr} deleted successfully'")
        
        print(f"✅ TIGHT TEST PASSED: delete-cidr returned correct format: {output}")
    
    def test_get_subnets_output_validation(self):
        """TIGHT TEST: get_subnets_from_cidr - output must be 4 valid CIDRs with whitespaces"""
        # Use a known CIDR for consistent testing
        test_cidr = "10.0.93.128/26"
        
        print(f"\n--- TIGHT TEST: get-subnets output validation ---")
        response = requests.get(f"http://localhost:8000/get-subnets?subnet_size=28&cidr={test_cidr}")
        self.assertEqual(response.status_code, 200)
        
        output = response.text.strip()
        print(f"get-subnets output: '{output}'")
        
        # TIGHT VALIDATION: Must be space-separated CIDRs
        subnets = output.split()
        
        # TIGHT VALIDATION: Must be exactly 4 subnets (26->28 = 4 subnets)
        self.assertEqual(len(subnets), 4, f"Expected 4 subnets from /26 to /28, got {len(subnets)}")
        
        # TIGHT VALIDATION: Each subnet must be valid CIDR format
        cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
        for i, subnet in enumerate(subnets):
            self.assertTrue(re.match(cidr_pattern, subnet), 
                           f"Subnet {i+1} '{subnet}' is not in valid CIDR format")
            
            # TIGHT VALIDATION: Each must be parseable as IPv4Network
            try:
                network = IPv4Network(subnet)
                print(f"  ✅ Subnet {i+1}: {network}")
            except ValueError as e:
                self.fail(f"Subnet {i+1} '{subnet}' is not a valid IPv4 CIDR: {e}")
            
            # TIGHT VALIDATION: Each must be /28 as requested
            self.assertEqual(network.prefixlen, 28, f"Subnet {i+1} expected /28, got /{network.prefixlen}")
            
            # TIGHT VALIDATION: Each must be subset of original CIDR
            original_network = IPv4Network(test_cidr)
            self.assertTrue(network.subnet_of(original_network), 
                           f"Subnet {i+1} {subnet} is not a subset of {test_cidr}")
        
        # TIGHT VALIDATION: Must contain whitespace separators
        self.assertIn(' ', output, "Output must contain whitespace separators between CIDRs")
        
        # TIGHT VALIDATION: Expected specific subnets for this CIDR
        expected_subnets = ["10.0.93.128/28", "10.0.93.144/28", "10.0.93.160/28", "10.0.93.176/28"]
        self.assertEqual(subnets, expected_subnets, 
                        f"Expected exact subnets {expected_subnets}, got {subnets}")
        
        print(f"✅ TIGHT TEST PASSED: get-subnets returned 4 valid CIDRs with whitespaces: {output}")

    def test_get_next_available_output_validation(self):
        """TIGHT TEST: get_next_available - output must be valid CIDR"""
        current_reason = self.get_current_reason()
        
        print(f"\n--- TIGHT TEST: get-next-cidr-no-push output validation ---")
        response = requests.get(f"http://localhost:8000/get-next-cidr-no-push?subnet_size=26&requiredrange=10&reason={current_reason}")
        self.assertEqual(response.status_code, 200)
        
        output = response.text.strip()
        print(f"get-next-cidr-no-push output: '{output}'")
        
        # TIGHT VALIDATION: Must be valid CIDR format (IP/prefix)
        cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
        self.assertTrue(re.match(cidr_pattern, output), f"Output '{output}' is not in valid CIDR format")
        
        # TIGHT VALIDATION: Must be parseable as IPv4Network
        try:
            network = IPv4Network(output)
            print(f"✅ Valid CIDR: {network}")
        except ValueError as e:
            self.fail(f"Output '{output}' is not a valid IPv4 CIDR: {e}")
        
        # TIGHT VALIDATION: Must be /26 subnet as requested
        self.assertEqual(network.prefixlen, 26, f"Expected /26 subnet, got /{network.prefixlen}")
        
        # TIGHT VALIDATION: Must be in 10.0.0.0/8 range as requested
        self.assertTrue(network.subnet_of(IPv4Network("10.0.0.0/8")), f"CIDR {output} is not in 10.0.0.0/8 range")
        
        # TIGHT VALIDATION: Must be single CIDR (no spaces or extra content)
        self.assertNotIn(' ', output, "Output should be single CIDR without spaces")
        self.assertNotIn('\n', output, "Output should be single line")
        
        print(f"✅ TIGHT TEST PASSED: get-next-cidr-no-push returned valid CIDR: {output}")

    def test_get_occupied_list_output_validation(self):
        """TIGHT TEST: get_occupied_list - output must be valid JSON"""
        print(f"\n--- TIGHT TEST: get-occupied-list output validation ---")
        response = requests.get(f"http://localhost:8000/get-occupied-list")
        self.assertEqual(response.status_code, 200)
        
        output = response.text.strip()
        print(f"get-occupied-list output: '{output[:200]}...' (truncated)")
        
        # TIGHT VALIDATION: Must be valid JSON
        try:
            json_data = json.loads(output)
            print(f"✅ Valid JSON with {len(json_data)} entries")
        except (json.JSONDecodeError, ValueError) as e:
            self.fail(f"Response is not valid JSON: {e}")
        
        # TIGHT VALIDATION: Must be a dictionary
        self.assertIsInstance(json_data, dict, "Response must be a JSON object/dictionary")
        
        # TIGHT VALIDATION: Each value must be a valid CIDR if present
        for key, cidr in json_data.items():
            if cidr:  # Skip empty values
                cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
                self.assertTrue(re.match(cidr_pattern, cidr), 
                               f"CIDR '{cidr}' for key '{key}' is not in valid format")
                
                try:
                    IPv4Network(cidr)
                except ValueError as e:
                    self.fail(f"CIDR '{cidr}' for key '{key}' is not valid: {e}")
        
        print(f"✅ TIGHT TEST PASSED: get-occupied-list returned valid JSON with {len(json_data)} entries")
    
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
