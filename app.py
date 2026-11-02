from __future__ import annotations

from flask import Flask, jsonify, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

MAX_MESSAGE_LENGTH = 5_000

TRAINING_MESSAGES = [
    ("ham", "Hey, are we still meeting for lunch today?"),
    ("ham", "I'll call you when I get off the train."),
    ("ham", "Can you send me the notes from class?"),
    ("ham", "Thanks for picking up the groceries."),
    ("ham", "Running ten minutes late, save me a seat."),
    ("ham", "Your appointment is confirmed for Tuesday at 3 pm."),
    ("ham", "The movie starts at seven. Want to meet there?"),
    ("ham", "Don't forget to bring your charger tomorrow."),
    ("ham", "Happy birthday! Hope you have a wonderful day."),
    ("ham", "I left the package at your front door."),
    ("ham", "Are you free this weekend?"),
    ("ham", "Please review the document when you have a chance."),
    ("ham", "Dinner is ready whenever you get home."),
    ("ham", "The meeting has moved to room 204."),
    ("ham", "Could you call me back after your appointment?"),
    ("ham", "I sent you the photos from our trip."),
    ("ham", "Your order is ready for collection at the store."),
    ("ham", "Let me know when you arrive safely."),
    ("ham", "We should catch up over coffee sometime."),
    ("ham", "The project deadline is next Friday."),
    ("ham", "Can you help me with the presentation tonight?"),
    ("ham", "I will be home around six this evening."),
    ("ham", "Thanks for letting me know about the change."),
    ("ham", "See you at the library after class."),
    ("ham", "Mom asked if you can visit on Sunday."),
    ("ham", "Your dentist appointment is tomorrow at 10 am."),
    ("ham", "I found your keys on the kitchen table."),
    ("ham", "Let's take the earlier bus if it is not too busy."),
    ("ham", "Please share the address for the restaurant."),
    ("ham", "That sounds good, I will see you then."),
    ("spam", "Congratulations! You have won a free prize. Claim now!"),
    ("spam", "URGENT: Your account is suspended. Verify your details now."),
    ("spam", "You have been selected for a cash reward. Call now to claim."),
    ("spam", "Win a brand new phone today! Click this link to enter."),
    ("spam", "Limited time offer! Get 80% off, shop now."),
    ("spam", "You are our lucky winner! Claim your free gift today."),
    ("spam", "Make money fast from home. No experience required."),
    ("spam", "Your loan is pre-approved. Apply now with no credit check."),
    ("spam", "Claim your free vacation now. Reply YES to qualify."),
    ("spam", "Final notice: pay your unpaid bill immediately."),
    ("spam", "Exclusive deal just for you. Buy now before it expires."),
    ("spam", "You have won a £1,000 gift card. Click to claim."),
    ("spam", "Get cheap medicines online with free delivery."),
    ("spam", "Act now to receive your guaranteed cash bonus."),
    ("spam", "Your package is on hold. Pay the delivery fee here."),
    ("spam", "Congratulations! You qualify for a free iPhone."),
    ("spam", "Earn extra income quickly. Sign up now for a bonus."),
    ("spam", "This is your last chance to claim your reward."),
    ("spam", "Free entry in our weekly prize draw. Text WIN now."),
    ("spam", "Lowest insurance rates guaranteed. Call today for a quote."),
    ("spam", "We noticed unusual activity. Confirm your password now."),
    ("spam", "Get a cash advance today. Instant approval guaranteed."),
    ("spam", "You have been chosen to receive a complimentary gift."),
    ("spam", "Unlock your exclusive discount before this offer ends."),
    ("spam", "Winner! Send your bank details to receive your prize."),
    ("spam", "Get rich fast with this simple investment opportunity."),
    ("spam", "Your subscription is expiring. Renew now to avoid a fee."),
    ("spam", "Claim your reward by clicking the link below."),
    ("spam", "Special promotion! Buy one and get one free today."),
    ("spam", "You are eligible for debt relief. Apply online now."),
]


def build_classifier() -> Pipeline:
    messages = [message for _, message in TRAINING_MESSAGES]
    labels = [label for label, _ in TRAINING_MESSAGES]
    classifier = Pipeline(
        [
            ("vectorizer", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
            ("classifier", MultinomialNB(alpha=0.25)),
        ]
    )
    classifier.fit(messages, labels)
    return classifier


classifier = build_classifier()


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/predict")
def predict():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Send a JSON object with a message field."), 400

    message = payload.get("message")
    if not isinstance(message, str):
        return jsonify(error="Message must be text."), 400

    message = message.strip()
    if not message:
        return jsonify(error="Enter a message to check."), 400
    if len(message) > MAX_MESSAGE_LENGTH:
        return jsonify(error=f"Messages must be {MAX_MESSAGE_LENGTH:,} characters or fewer."), 413

    probabilities = classifier.predict_proba([message])[0]
    spam_index = list(classifier.classes_).index("spam")
    spam_probability = float(probabilities[spam_index])
    prediction = "spam" if spam_probability >= 0.5 else "ham"

    return jsonify(
        prediction=prediction,
        confidence=round(
            (spam_probability if prediction == "spam" else 1 - spam_probability) * 100
        ),
        spam_probability=round(spam_probability * 100),
    )


if __name__ == "__main__":
    app.run(debug=True)
