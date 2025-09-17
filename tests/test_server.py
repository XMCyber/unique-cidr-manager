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

    def _get_test_cidr(self):
        """Helper method to generate a CIDR for testing"""
        if not hasattr(self, '_shared_cidr') or not self._shared_cidr:
            current_reason = f"test-{datetime.now().strftime('%H%M%S%f')}"
            response = requests.get(f"http://localhost:8000/get-cidr?subnet_size=26&requiredrange=10&reason={current_reason}")
            if response.status_code == 200:
                self._shared_cidr = response.text.strip()
        return self._shared_cidr

    def test_1_get_cidr_output_validation(self):
        """TEST 1: get_cidr - output must be valid CIDR"""
        print(f"\n🧪 TEST 1: get-cidr API (output = valid CIDR)")
        current_reason = f"get-cidr-test-{datetime.now().strftime('%H%M%S%f')}"

        response = requests.get(f"http://localhost:8000/get-cidr?subnet_size=26&requiredrange=10&reason={current_reason}")
        self.assertEqual(response.status_code, 200)

        output = response.text.strip()
        print(f"   Output: '{output}'")

        # TIGHT VALIDATION: Valid CIDR format
        cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
        self.assertTrue(re.match(cidr_pattern, output), f"Invalid CIDR format: {output}")

        network = IPv4Network(output)
        self.assertEqual(network.prefixlen, 26, f"Expected /26, got /{network.prefixlen}")
        self.assertTrue(network.subnet_of(IPv4Network("10.0.0.0/8")), f"Not in 10.x range: {output}")

        # Store for cleanup
        self._shared_cidr = output
        print(f"   ✅ PASSED: Valid CIDR format")

    def test_2_get_subnets_output_validation(self):
        """TEST 2: get_subnets_from_cidr - output must be 4 valid CIDRs with whitespaces"""
        print(f"\n🧪 TEST 2: get-subnets API (output = 4 valid CIDRs with whitespaces)")

        # Use a known CIDR for consistent testing
        test_cidr = "10.0.93.128/26"

        response = requests.get(f"http://localhost:8000/get-subnets?subnet_size=28&cidr={test_cidr}")
        self.assertEqual(response.status_code, 200)

        output = response.text.strip()
        print(f"   Output: '{output}'")

        # TIGHT VALIDATION: 4 CIDRs with whitespaces
        cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
        subnets = output.split()
        self.assertEqual(len(subnets), 4, f"Expected 4 subnets, got {len(subnets)}")
        self.assertIn(' ', output, "Must contain whitespace separators")

        for i, subnet in enumerate(subnets):
            self.assertTrue(re.match(cidr_pattern, subnet), f"Invalid subnet format: {subnet}")
            subnet_network = IPv4Network(subnet)
            self.assertEqual(subnet_network.prefixlen, 28, f"Subnet {i + 1} not /28: {subnet}")
            self.assertTrue(subnet_network.subnet_of(IPv4Network(test_cidr)), f"Subnet {subnet} not subset of {test_cidr}")

        # Validate expected exact output
        expected_subnets = ["10.0.93.128/28", "10.0.93.144/28", "10.0.93.160/28", "10.0.93.176/28"]
        self.assertEqual(subnets, expected_subnets, f"Expected {expected_subnets}, got {subnets}")

        print(f"   ✅ PASSED: 4 valid CIDRs with whitespaces")

    def test_3_get_next_available_output_validation(self):
        """TEST 3: get_next_available - output must be valid CIDR"""
        print(f"\n🧪 TEST 3: get-next-cidr-no-push API (output = valid CIDR)")

        next_reason = f"next-test-{datetime.now().strftime('%H%M%S%f')}"
        response = requests.get(f"http://localhost:8000/get-next-cidr-no-push?subnet_size=26&requiredrange=10&reason={next_reason}")
        self.assertEqual(response.status_code, 200)

        output = response.text.strip()
        print(f"   Output: '{output}'")

        # TIGHT VALIDATION: Valid CIDR
        cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
        self.assertTrue(re.match(cidr_pattern, output), f"Invalid CIDR format: {output}")

        network = IPv4Network(output)
        self.assertEqual(network.prefixlen, 26, f"Expected /26, got /{network.prefixlen}")
        self.assertNotIn(' ', output, "Should be single CIDR without spaces")
        self.assertNotIn('\n', output, "Should be single line")

        print(f"   ✅ PASSED: Valid CIDR format")

    def test_4_get_occupied_list_output_validation(self):
        """TEST 4: get_occupied_list - output must be valid JSON"""
        print(f"\n🧪 TEST 4: get-occupied-list API (output = valid JSON)")

        response = requests.get("http://localhost:8000/get-occupied-list")
        self.assertEqual(response.status_code, 200)

        output = response.text.strip()
        print(f"   Output: JSON with {len(output)} characters")

        # TIGHT VALIDATION: Valid JSON
        try:
            occupied_data = json.loads(output)
        except (json.JSONDecodeError, ValueError) as e:
            self.fail(f"Invalid JSON response: {e}")

        self.assertIsInstance(occupied_data, dict, "Response must be JSON object/dictionary")

        # Validate each CIDR in occupied list
        cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
        for key, cidr in occupied_data.items():
            if cidr:
                self.assertTrue(re.match(cidr_pattern, cidr), f"Invalid CIDR in occupied list: {cidr}")
                IPv4Network(cidr)  # Validate parseable

        print(f"   ✅ PASSED: Valid JSON with {len(occupied_data)} entries")

    def test_5_delete_cidr_output_validation(self):
        """TEST 5: delete_cidr - output must be 'CIDR {cidr} deleted successfully'"""
        print(f"\n🧪 TEST 5: delete-cidr API (output = 'CIDR {{cidr}} deleted successfully')")

        # Get a CIDR to delete
        test_cidr = self._get_test_cidr()

        response = requests.get(f"http://localhost:8000/delete-cidr-from-list?cidr_deletion={test_cidr}")
        self.assertEqual(response.status_code, 200)

        output = response.text.strip()
        print(f"   Output: '{output}'")

        # TIGHT VALIDATION: Exact format "CIDR {cidr} deleted successfully"
        expected_pattern = rf'^CIDR {re.escape(test_cidr)} deleted successfully.*$'
        self.assertTrue(re.match(expected_pattern, output),
                        f"Delete output doesn't match expected format. Got: {output}")

        print(f"   ✅ PASSED: Correct delete message format")

        # Verify removal
        sleep(1)
        final_response = requests.get("http://localhost:8000/get-occupied-list")
        self.assertEqual(final_response.status_code, 200)
        final_data = json.loads(final_response.text)
        self.assertNotIn(test_cidr, final_data.values(), f"CIDR {test_cidr} should be removed")


if __name__ == '__main__':
    # Run with: python -m pytest tests/test_server.py -v
    # Or: python tests/test_server.py
    unittest.main(verbosity=2)
