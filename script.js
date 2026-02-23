(function () {
  const form = document.getElementById("predict-form");
  const submitBtn = document.getElementById("submit-btn");
  const resultSection = document.getElementById("result-section");
  const resultLabel = document.getElementById("result-label");
  const resultDetail = document.getElementById("result-detail");
  const errorSection = document.getElementById("error-section");
  const errorMessage = document.getElementById("error-message");

  function hideAllFeedback() {
    resultSection.classList.add("hidden");
    resultSection.classList.remove("visible");
    errorSection.classList.add("hidden");
    errorSection.classList.remove("visible");
  }

  function showResult(label, isAnomaly) {
    hideAllFeedback();
    resultLabel.textContent = label;
    resultLabel.className = "result-label " + (isAnomaly ? "anomaly" : "normal");
    resultDetail.textContent = "Prediction: " + (isAnomaly ? "Anomaly (1)" : "Normal (0)");
    resultSection.classList.remove("hidden");
    resultSection.classList.add("visible");
  }

  function showError(msg) {
    hideAllFeedback();
    errorMessage.textContent = msg;
    errorSection.classList.remove("hidden");
    errorSection.classList.add("visible");
  }

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    const payload = {
      inbound_rate: parseFloat(form.inbound_rate.value),
      outbound_rate: parseFloat(form.outbound_rate.value),
      inbound_util: parseFloat(form.inbound_util.value),
      outbound_util: parseFloat(form.outbound_util.value),
    };

    if ([payload.inbound_rate, payload.outbound_rate, payload.inbound_util, payload.outbound_util].some(Number.isNaN)) {
      showError("Please enter valid numbers for all fields.");
      return;
    }

    submitBtn.disabled = true;
    submitBtn.classList.add("loading");
    hideAllFeedback();

    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (!res.ok) {
        showError(data.error || data.detail || "Request failed.");
        return;
      }

      showResult(data.label, data.prediction === 1);
    } catch (err) {
      showError("Network error: " + (err.message || "Could not reach server."));
    } finally {
      submitBtn.disabled = false;
      submitBtn.classList.remove("loading");
    }
  });
})();
