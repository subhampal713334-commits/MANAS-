const form = document.querySelector("#assessment-form");
const errorBox = document.querySelector("#form-error");
const submitButton = form.querySelector("button[type='submit']");
const welcomeState = document.querySelector("#welcome-state");
const scoreState = document.querySelector("#score-state");
const scoreValue = document.querySelector("#score-value");
const rangeTitle = document.querySelector("#range-title");
const rangeCopy = document.querySelector("#range-copy");
const scoreFill = document.querySelector("#score-fill");
const suggestionList = document.querySelector("#suggestion-list");
const resetButton = document.querySelector("#reset-button");
const formResetButton = document.querySelector("#form-reset-button");

const wellbeingGuidance = {
  lower: {
    title: "Lower score range",
    copy: "Below 5.1 · A dataset-relative statistical range.",
    suggestions: [
      "Consider setting aside a short, screen-free pause during the day.",
      "Try a small routine that supports rest, movement, or time outdoors.",
      "If you would like support, consider talking with someone you trust.",
    ],
  },
  middle: {
    title: "Middle score range",
    copy: "5.1 to 7.1 · A dataset-relative statistical range.",
    suggestions: [
      "Notice which parts of your current routine feel most sustainable.",
      "Protect regular breaks between focused work and screen time.",
      "Keep making room for sleep, movement, and activities away from screens.",
    ],
  },
  upper: {
    title: "Upper score range",
    copy: "Above 7.1 · A dataset-relative statistical range.",
    suggestions: [
      "Continue the routines that help you feel balanced and focused.",
      "Make time for meaningful offline activities and regular connection.",
      "Review your digital habits from time to time as your schedule changes.",
    ],
  },
};

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function clearError() {
  errorBox.textContent = "";
  errorBox.hidden = true;
}

function collectFormData() {
  const data = Object.fromEntries(new FormData(form).entries());
  const numericFields = [
    "Age",
    "Avg_Daily_Usage_Hours",
    "Daily_Unlocks",
    "Study_Hours",
    "Physical_Activity_Hours",
    "Sleep_Hours_Per_Night",
  ];

  numericFields.forEach((field) => {
    data[field] = Number(data[field]);
  });
  return data;
}

function displayGuidance(score) {
  const range = score < 5.1 ? wellbeingGuidance.lower
    : score <= 7.1 ? wellbeingGuidance.middle
    : wellbeingGuidance.upper;

  rangeTitle.textContent = range.title;
  rangeCopy.textContent = range.copy;
  scoreFill.style.width = `${Math.max(0, Math.min(100, (score / 10) * 100))}%`;
  suggestionList.replaceChildren(
    ...range.suggestions.map((suggestion) => {
      const item = document.createElement("li");
      item.textContent = suggestion;
      return item;
    }),
  );
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearError();

  if (!form.checkValidity()) {
    showError("Please complete every field with a valid value.");
    form.reportValidity();
    return;
  }

  submitButton.disabled = true;
  submitButton.textContent = "Calculating...";

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(collectFormData()),
    });
    const result = await response.json();

    if (!response.ok) {
      const detail = Array.isArray(result.detail)
        ? "Please check the values entered and try again."
        : result.detail || "The prediction could not be calculated.";
      throw new Error(detail);
    }

    const score = Number(result.Mental_Health_Score);
    scoreValue.textContent = score.toFixed(2);
    displayGuidance(score);
    welcomeState.hidden = true;
    scoreState.hidden = false;
  } catch (error) {
    showError(error.message || "Unable to reach the prediction service.");
  } finally {
    submitButton.disabled = false;
    submitButton.innerHTML = 'Calculate score <span aria-hidden="true">→</span>';
  }
});

resetButton.addEventListener("click", () => {
  form.reset();
  clearError();
  scoreState.hidden = true;
  welcomeState.hidden = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
});

formResetButton.addEventListener("click", () => {
  form.reset();
  clearError();
});
