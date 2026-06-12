import unittest
from fastapi.testclient import TestClient
from main import app

class TestMyFeatures(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])

    def test_convert_endpoint(self):
        payload = {"amt": 1000, "base": "RUB", "target": "USD"}
        response = self.client.post("/convert", data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])

    def test_multi_page(self):
        response = self.client.get("/multi?amt=1000&base=RUB")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])

    def test_buy_page(self):
        response = self.client.get("/buy?amt=1000&base=RUB")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])

    def test_buy_confirm_endpoint(self):
        payload = {
            "user_name": "Иван Тестовый",
            "user_phone": "+7 (999) 000-11-22",
            "amt": 500.0,
            "base": "RUB",
            "target": "EUR"
        }
        response = self.client.post("/buy/confirm", data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])

    def test_history_page(self):
        response = self.client.get("/history?currency=USD")
        self.assertEqual(response.status_code, 200)

    def test_chart_page(self):
        response = self.client.get("/chart?currency=USD")
        self.assertEqual(response.status_code, 200)

    def test_convert_gbp(self):
        response = self.client.post(
            "/convert",
            data={"amt": 1000, "base": "RUB", "target": "GBP"}
        )
        self.assertEqual(response.status_code, 200)

    def test_convert_jpy(self):
        response = self.client.post(
            "/convert",
            data={"amt": 1000, "base": "RUB", "target": "JPY"}
        )
        self.assertEqual(response.status_code, 200)

    def test_convert_aed(self):
        response = self.client.post(
            "/convert",
            data={"amt": 1000, "base": "RUB", "target": "AED"}
        )
        self.assertEqual(response.status_code, 200)

    def test_convert_byn(self):
        response = self.client.post(
            "/convert",
            data={"amt": 1000, "base": "RUB", "target": "BYN"}
        )
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()