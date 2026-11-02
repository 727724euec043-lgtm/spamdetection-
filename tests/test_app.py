import unittest

from app import app


class SpamDetectorTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_homepage_renders_detector(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Message check", response.data)

    def test_spam_message_is_classified(self):
        response = self.client.post(
            "/api/predict",
            json={"message": "Congratulations! Claim your free prize now. Click here!"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["prediction"], "spam")
        self.assertGreaterEqual(response.json["spam_probability"], 50)

    def test_normal_message_is_classified(self):
        response = self.client.post(
            "/api/predict",
            json={"message": "Hey, are we still meeting for lunch today?"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["prediction"], "ham")
        self.assertLess(response.json["spam_probability"], 50)

    def test_empty_message_is_rejected(self):
        response = self.client.post("/api/predict", json={"message": "   "})

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_non_text_message_is_rejected(self):
        response = self.client.post("/api/predict", json={"message": 42})

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_oversized_message_is_rejected(self):
        response = self.client.post(
            "/api/predict",
            json={"message": "x" * 5001},
        )

        self.assertEqual(response.status_code, 413)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
