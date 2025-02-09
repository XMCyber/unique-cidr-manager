import unittest
import requests
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
        self.commiter_email = os.environ.get("COMMITER_EMAIL")
        self.commiter_name = os.environ.get("COMMITER_NAME")

    @classmethod
    def setUpClass(cls):
        # Start the server before tests
        cls.server_process = Popen(['python', 'server/main.py'])
        sleep(2)  # Wait for the server to start

    @classmethod
    def tearDownClass(cls):
        cls.server_process.terminate()  # Stop the server after tests

    def get_current_reason(self):
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"test-{time}"

    def test_get_cidr(self):
        current_reason = self.get_current_reason()
        response = requests.get(f"http://localhost:8000/get-cidr?subnet_size=24&requiredrange=192&reason={current_reason}")
        self.assertEqual(response.status_code, 200)

    def test_get_next_cidr_no_push(self):
        current_reason = self.get_current_reason()
        response = requests.get(f"http://localhost:8000/get-next-cidr-no-push?subnet_size=24&requiredrange=192&reason={current_reason}")
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
