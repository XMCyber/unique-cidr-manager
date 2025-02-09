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

    def test_get_cidr(self):
        current_reason = self.get_current_reason()
        response = requests.get(f"http://localhost:8000/get-cidr?subnet_size=26&requiredrange=10&reason={current_reason}")
        self.assertEqual(response.status_code, 200)
        print(response.text)
        self.assertTrue(IPv4Network(response.text))
    
    def test_get_subnets(self):
        response = requests.get("http://localhost:8000/get-subnets?subnet_size=28&cidr=10.0.1.0/26")
        self.assertEqual(response.status_code, 200)
        print(response.text)
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
