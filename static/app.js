const form = document.querySelector("#detector-form");
const messageInput = document.querySelector("#message");
const charCount = document.querySelector("#char-count");
const resultPanel = document.querySelector("#result");
const errorMessage = document.querySelector("#error-message");
const analyzeButton = form.querySelector('button[type="submit"]');

messageInput.addEventListener("input", () => {
  charCount.textContent = `${messageInput.value.length.toLocaleString()} / 5,000`;
});

document.querySelector("#clear-button").addEventListener("click", () => {
  messageInput.value = "";
  charCount.textContent = "0 / 5,000";
  resultPanel.hidden = true;
  errorMessage.hidden = true;
  messageInput.focus();
});

document.querySelectorAll(".example-chip").forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset.message;
    messageInput.dispatchEvent(new Event("input"));
    messageInput.focus();
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  resultPanel.hidden = true;
  errorMessage.hidden = true;
  analyzeButton.disabled = true;
  analyzeButton.classList.add("is-loading");
  analyzeButton.querySelector(".button-label").textContent = "Analyzing…";

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: messageInput.value }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Something went wrong. Please try again.");
    }

    const isSpam = data.prediction === "spam";
    resultPanel.classList.toggle("is-spam", isSpam);
    resultPanel.classList.toggle("is-safe", !isSpam);
    document.querySelector("#result-kicker").textContent = isSpam ? "POTENTIAL SPAM" : "LOOKS LIKE A NORMAL MESSAGE";
    document.querySelector("#result-title").textContent = isSpam ? "Treat with caution" : "Probably safe";
    document.querySelector("#confidence-value").textContent = `${data.confidence}%`;
    document.querySelector("#confidence-bar").style.width = `${data.spam_probability}%`;
    document.querySelector("#spam-probability").textContent = `${data.spam_probability}%`;
    document.querySelector("#result-mark").innerHTML = isSpam
      ? '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 8v4m0 4h.01M10.3 3.9 2.8 17a2 2 0 0 0 1.7 3h15a2 2 0 0 0 1.7-3l-7.5-13.1a2 2 0 0 0-3.4 0Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
      : '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m5 12 4 4L19 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    resultPanel.hidden = false;
  } catch (error) {
    errorMessage.textContent = error.message;
    errorMessage.hidden = false;
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.classList.remove("is-loading");
    analyzeButton.querySelector(".button-label").textContent = "Analyze message";
  }
});
