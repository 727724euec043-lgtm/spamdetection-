# Signal — Spam detector

A small Flask website that uses a scikit-learn TF-IDF and Naive Bayes text classifier to estimate whether a message looks like spam.

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Start the website:

   ```powershell
   python app.py
   ```

4. Open http://127.0.0.1:5000.

The classifier is trained from a small, illustrative sample corpus included in `app.py`. It is intended as a working demo, not a production spam filter or a security decision. For better real-world accuracy, train and evaluate it on a representative, appropriately licensed SMS dataset.

## Run tests

```powershell
python -m unittest discover -s tests
```
