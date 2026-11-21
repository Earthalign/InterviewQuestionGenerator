/**
 * Python Interview Lab — Client Application
 */

const questionList = document.querySelector("#question-list");
const toast = document.querySelector("#toast");
const sourceStatus = document.querySelector("#source-status");
const generateSetButton = document.querySelector("#generate-set-button");
let toastTimeout;
let currentQuestions = [];
let currentCompletedIds = [];
let currentFilter = "all";

const OPTION_LETTERS = ["A", "B", "C", "D"];

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("visible");
  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => toast.classList.remove("visible"), 3200);
}

function getCategoryClass(category) {
  const norm = category.toLowerCase().replace(/[^a-z0-9]/g, "-");
  return `badge-cat-${norm}`;
}

function updateProgress(progress) {
  const countEl = document.querySelector("#progress-count");
  const totalEl = document.querySelector("#progress-total");
  const streakEl = document.querySelector("#streak-count");
  const percentEl = document.querySelector("#progress-percentage");
  const captionEl = document.querySelector("#progress-caption");
  const fillEl = document.querySelector(".progress-fill");
  const trackEl = document.querySelector(".progress-track");

  if (countEl) countEl.textContent = progress.completed;
  if (totalEl) totalEl.textContent = progress.total;
  if (streakEl) streakEl.textContent = progress.streak;

  const percentage = progress.total > 0
    ? Math.round((progress.completed / progress.total) * 100)
    : 0;

  if (percentEl) percentEl.textContent = `${percentage}%`;
  if (trackEl) {
    trackEl.setAttribute("aria-valuemax", progress.total);
    trackEl.setAttribute("aria-valuenow", progress.completed);
  }
  if (fillEl) fillEl.style.width = `${percentage}%`;

  if (captionEl) {
    if (progress.completed === progress.total && progress.total > 0) {
      captionEl.textContent = "🎉 Gratulacje! Cały dzisiejszy zestaw został ukończony.";
    } else if (progress.completed > 0) {
      const remaining = progress.total - progress.completed;
      captionEl.textContent = `Świetne tempo! Do ukończenia zestawu pozostało pytań: ${remaining}.`;
    } else {
      captionEl.textContent = "Zacznij od dowolnego pytania. Wybierz odpowiedź i sprawdź swoją wiedzę.";
    }
  }

  updateFilterCounts();
}

function updateFilterCounts() {
  const countAll = currentQuestions.length;
  const countTheory = currentQuestions.filter(q => q.kind === "theory").length;
  const countPractice = currentQuestions.filter(q => q.kind === "practice").length;
  const countCompleted = currentQuestions.filter(q => currentCompletedIds.includes(q.id)).length;
  const countPending = countAll - countCompleted;

  const setEl = (id, val) => {
    const el = document.querySelector(id);
    if (el) el.textContent = val;
  };

  setEl("#count-all", countAll);
  setEl("#count-theory", countTheory);
  setEl("#count-practice", countPractice);
  setEl("#count-completed", countCompleted);
  setEl("#count-pending", countPending);
}

function applyFilter(filter) {
  currentFilter = filter;
  document.querySelectorAll(".filter-tab").forEach(tab => {
    const isActive = tab.dataset.filter === filter;
    tab.classList.toggle("active", isActive);
    tab.setAttribute("aria-selected", isActive);
  });

  document.querySelectorAll(".question-card").forEach(card => {
    const kind = card.dataset.kind;
    const isCompleted = card.classList.contains("is-complete");

    let isVisible = true;
    if (filter === "theory") isVisible = (kind === "theory");
    else if (filter === "practice") isVisible = (kind === "practice");
    else if (filter === "completed") isVisible = isCompleted;
    else if (filter === "pending") isVisible = !isCompleted;

    card.classList.toggle("is-hidden", !isVisible);
  });
}

function updateSourceStatus(data) {
  const generatedByGroq = data.source.startsWith("Groq");
  const fallbackPrefix = "Lokalna pula (awaryjnie): ";
  const legacyFallbackPrefix = "Lokalna pula (awaryjnie: Groq niedostępny)";
  const usingFallback =
    data.source.startsWith(fallbackPrefix) ||
    data.source.startsWith(legacyFallbackPrefix);

  const fallbackReason = usingFallback
    ? data.source.startsWith(fallbackPrefix)
      ? data.source.slice(fallbackPrefix.length)
      : "Groq wcześniej nie odpowiedział."
    : "";

  sourceStatus.dataset.state = usingFallback
    ? "error"
    : data.groq_available
      ? "ready"
      : "local";

  document.querySelector("#source-status-title").textContent = usingFallback
    ? "Groq chwilowo niedostępny"
    : data.groq_available
      ? generatedByGroq
        ? `Źródło: ${data.source}`
        : "Groq AI skonfigurowany"
      : "Lokalna pula pytań";

  document.querySelector("#source-status-description").textContent = usingFallback
    ? `${fallbackReason} Używam lokalnych pytań; możesz ponowić próbę.`
    : data.groq_available
      ? generatedByGroq
        ? "Dzisiejszy zestaw został wygenerowany przez AI."
        : "Możesz wygenerować świeży zestaw pytań."
      : "Ustaw GROQ_API_KEY, aby włączyć generowanie przez Groq AI.";

  generateSetButton.disabled = !data.groq_available;
  generateSetButton.innerHTML = usingFallback
    ? `<span class="btn-icon">↻</span><span>Ponów próbę z Groq</span>`
    : generatedByGroq
      ? `<span class="btn-icon">✨</span><span>Wygeneruj kolejny zestaw</span>`
      : `<span class="btn-icon">✨</span><span>Wygeneruj zestaw</span>`;
}

function renderDashboard(data) {
  currentQuestions = data.questions || [];
  currentCompletedIds = data.progress?.completed_ids || [];

  questionList.replaceChildren(
    ...currentQuestions.map((q, index) =>
      makeQuestionCard(q, index, currentCompletedIds)
    )
  );

  updateProgress(data.progress);
  updateSourceStatus(data);

  if (data.date) {
    const dateObj = new Date(`${data.date}T12:00:00`);
    const dateFormatted = new Intl.DateTimeFormat("pl-PL", {
      weekday: "long",
      day: "numeric",
      month: "long",
      year: "numeric"
    }).format(dateObj);
    document.querySelector("#today-date").textContent = dateFormatted;
  }

  document.querySelector("#content-source").textContent = data.source;
  applyFilter(currentFilter);
}

function makeQuestionCard(question, index, completedIds) {
  const isCompleted = completedIds.includes(question.id);
  const details = document.createElement("details");
  details.className = `question-card ${isCompleted ? "is-complete" : ""}`;
  details.dataset.id = question.id;
  details.dataset.kind = question.kind;

  // SUMMARY
  const summary = document.createElement("summary");
  summary.className = "question-summary";

  const numberBadge = document.createElement("div");
  numberBadge.className = "question-number question-number-badge";
  numberBadge.textContent = isCompleted ? "✓" : String(index + 1).padStart(2, "0");

  const headerText = document.createElement("div");
  headerText.className = "question-header-text question-main";

  const title = document.createElement("h3");
  title.className = "question-title";
  title.textContent = question.title;

  const promptPreview = document.createElement("p");
  promptPreview.className = "question-prompt-preview question-prompt";
  promptPreview.textContent = question.prompt.split("\n")[0];

  headerText.append(title, promptPreview);

  const badges = document.createElement("div");
  badges.className = "question-badges question-tags";

  const catBadge = document.createElement("span");
  catBadge.className = `badge ${getCategoryClass(question.category)} tag tag-category`;
  catBadge.textContent = question.category;

  const kindBadge = document.createElement("span");
  kindBadge.className = `badge badge-kind-${question.kind} tag tag-kind ${question.kind}`;
  kindBadge.textContent = question.kind === "theory" ? "TEORIA" : "PRAKTYKA";

  badges.append(catBadge, kindBadge);

  const chevron = document.createElement("span");
  chevron.className = "accordion-chevron chevron";
  chevron.setAttribute("aria-hidden", "true");
  chevron.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"></polyline></svg>`;

  summary.append(numberBadge, headerText, badges, chevron);

  // BODY
  const body = document.createElement("div");
  body.className = "question-content question-body";

  const fullPrompt = document.createElement("div");
  fullPrompt.className = "question-full-prompt";
  fullPrompt.textContent = question.prompt;
  body.append(fullPrompt);

  const form = document.createElement("form");
  form.className = "answer-form";

  const optionsGroup = document.createElement("fieldset");
  optionsGroup.className = "answer-options-group answer-options";
  optionsGroup.setAttribute("aria-label", "Wybierz odpowiedź");

  question.options.forEach((optText, optIdx) => {
    const label = document.createElement("label");
    label.className = "answer-option-card answer-option";

    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = `answer-${question.id}`;
    radio.value = optText;
    radio.required = true;

    const letterBadge = document.createElement("span");
    letterBadge.className = "option-letter-badge";
    letterBadge.textContent = OPTION_LETTERS[optIdx] || "•";

    const textLabel = document.createElement("span");
    textLabel.className = "option-text-label";
    textLabel.textContent = optText;

    label.append(radio, letterBadge, textLabel);
    optionsGroup.append(label);
  });

  form.append(optionsGroup);

  const submitBtn = document.createElement("button");
  submitBtn.className = "btn-submit-answer submit-button";
  submitBtn.type = "submit";
  submitBtn.textContent = "Sprawdź odpowiedź";
  form.append(submitBtn);

  const feedbackBox = document.createElement("div");
  feedbackBox.className = "feedback-box feedback";
  feedbackBox.hidden = true;
  body.append(form, feedbackBox);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const checked = form.querySelector('input[type="radio"]:checked');
    if (!checked) {
      form.reportValidity();
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Weryfikacja…";

    try {
      const response = await fetch("/api/attempts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question_id: question.id, answer: checked.value }),
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || "Błąd podczas sprawdzania odpowiedzi.");
      }

      feedbackBox.hidden = false;
      feedbackBox.className = `feedback-box feedback ${result.completed ? "success" : "retry"}`;

      const titleEl = document.createElement("strong");
      titleEl.className = "feedback-title";
      titleEl.textContent = result.feedback;

      const solutionEl = document.createElement("p");
      solutionEl.className = "feedback-solution";
      solutionEl.textContent = result.solution;

      feedbackBox.replaceChildren(titleEl, solutionEl);

      if (result.completed) {
        details.classList.add("is-complete");
        numberBadge.textContent = "✓";
        if (!currentCompletedIds.includes(question.id)) {
          currentCompletedIds.push(question.id);
        }
        showToast("✓ Poprawna odpowiedź!");
      }

      const streakVal = Number(document.querySelector("#streak-count")?.textContent) || 0;
      updateProgress({
        completed: result.completed_count,
        total: result.total_count,
        percentage: Math.round((result.completed_count / result.total_count) * 100),
        streak: streakVal,
      });
    } catch (err) {
      showToast(err.message || "Wystąpił błąd.");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Sprawdź odpowiedź";
    }
  });

  details.append(summary, body);
  return details;
}

async function generateNewSet() {
  const completed = Number(document.querySelector("#progress-count")?.textContent) || 0;
  if (
    completed > 0 &&
    !window.confirm("Nowy zestaw wyzeruje dzisiejszy postęp. Kontynuować?")
  ) {
    return;
  }

  generateSetButton.disabled = true;
  generateSetButton.innerHTML = `<span class="btn-icon">⏳</span><span>Generowanie pytań…</span>`;
  sourceStatus.dataset.state = "generating";
  document.querySelector("#source-status-title").textContent = "Przygotowuję zestaw z Groq AI";
  document.querySelector("#source-status-description").textContent = "Generowanie 20 pytań technicznych po polsku…";

  try {
    const response = await fetch("/api/today/generate", { method: "POST" });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Nie udało się wygenerować pytań.");
    }
    renderDashboard(data);
    showToast("Pomyślnie wygenerowano nowy zestaw pytań.");
  } catch (err) {
    sourceStatus.dataset.state = "error";
    document.querySelector("#source-status-title").textContent = "Nie udało się wygenerować zestawu";
    document.querySelector("#source-status-description").textContent = err.message || "Błąd generowania pytań.";
    showToast(err.message || "Błąd generowania.");
    generateSetButton.disabled = false;
    generateSetButton.innerHTML = `<span class="btn-icon">↻</span><span>Ponów próbę</span>`;
  }
}

// SETUP EVENT LISTENERS
document.addEventListener("DOMContentLoaded", () => {
  generateSetButton.addEventListener("click", generateNewSet);

  document.querySelectorAll(".filter-tab").forEach(tab => {
    tab.addEventListener("click", () => applyFilter(tab.dataset.filter));
  });

  // Load Initial Data
  fetch("/api/today")
    .then(res => res.json())
    .then(data => renderDashboard(data))
    .catch(err => {
      showToast("Nie udało się pobrać zestawu na dziś.");
      questionList.innerHTML = `<div class="loading-state"><span>Nie udało się pobrać pytań. Odśwież stronę.</span></div>`;
    });
});
