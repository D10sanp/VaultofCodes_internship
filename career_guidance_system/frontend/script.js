// ---------------------------------------------------------------------------
// Wayfind — questionnaire logic
// ---------------------------------------------------------------------------

// Use a same-origin (relative) API base so the frontend works when served
// directly by the backend. If the page is opened from the file system
// (file://), default to the local backend at http://localhost:8000 so
// fetch requests still reach the API during local development.
const API_BASE = (function () {
  try {
    if (window && window.location && window.location.protocol === "file:") {
      return "http://localhost:8000";
    }
  } catch (e) {
    // ignore and fall back to same-origin
  }
  return "";
})();

const state = {
  step: 0,
  skills: [],
  interests: [],
  degree_mode: null,
  counseling_interest: null,
};

const steps = Array.from(document.querySelectorAll(".step"));
const waypointItems = Array.from(document.querySelectorAll("#waypoints li"));
const btnBack = document.getElementById("btn-back");
const btnNext = document.getElementById("btn-next");
const btnSubmit = document.getElementById("btn-submit");
const stepnav = document.querySelector(".stepnav");
const resultsEl = document.getElementById("results");
const loadingEl = document.getElementById("loading");
const quizForm = document.getElementById("quiz");

const LAST_STEP = steps.length - 1;

// ---------------- Conditional question wiring ----------------

document.getElementById("current_education").addEventListener("change", (e) => {
  const collegeFields = document.getElementById("college-fields");
  const needsCollegeInfo = ["Undergraduate", "Postgraduate"].includes(e.target.value);
  collegeFields.hidden = !needsCollegeInfo;
});

function setupTagInput(inputId, tagsContainerId, targetKey) {
  const input = document.getElementById(inputId);
  const container = document.getElementById(tagsContainerId);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      const value = input.value.trim().replace(/,$/, "");
      if (value && !state[targetKey].includes(value)) {
        state[targetKey].push(value);
        renderTags(container, targetKey);
      }
      input.value = "";
    } else if (e.key === "Backspace" && !input.value && state[targetKey].length) {
      state[targetKey].pop();
      renderTags(container, targetKey);
    }
  });
}

function renderTags(container, targetKey) {
  container.innerHTML = "";
  state[targetKey].forEach((tag, idx) => {
    const el = document.createElement("span");
    el.className = "tag";
    el.innerHTML = `${escapeHtml(tag)} <button type="button" aria-label="Remove">×</button>`;
    el.querySelector("button").addEventListener("click", () => {
      state[targetKey].splice(idx, 1);
      renderTags(container, targetKey);
    });
    container.appendChild(el);
  });
}

setupTagInput("skills_input", "skills_tags", "skills");
setupTagInput("interests_input", "interests_tags", "interests");

function setupChoiceGroup(groupId, stateKey, onChange) {
  const group = document.getElementById(groupId);
  group.querySelectorAll(".choice").forEach((btn) => {
    btn.addEventListener("click", () => {
      group.querySelectorAll(".choice").forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
      state[stateKey] = btn.dataset.value;
      if (onChange) onChange(btn.dataset.value);
    });
  });
}

setupChoiceGroup("degree_mode_group", "degree_mode", updateSpecializationVisibility);
setupChoiceGroup("counseling_group", "counseling_interest", updateSpecializationVisibility);

function updateSpecializationVisibility() {
  const field = document.getElementById("specialization-field");
  const wantsHigherEd =
    state.degree_mode && state.degree_mode !== "Not Sure Yet" ||
    (state.counseling_interest && state.counseling_interest.startsWith("Yes"));
  field.hidden = !wantsHigherEd;
}

// ---------------- Step navigation ----------------

function showStep(index) {
  steps.forEach((s) => (s.hidden = Number(s.dataset.step) !== index));
  waypointItems.forEach((li) => {
    const n = Number(li.dataset.step);
    li.classList.toggle("active", n === index);
    li.classList.toggle("done", n < index);
  });
  btnBack.disabled = index === 0;
  btnBack.hidden = index === 0;
  btnNext.hidden = index === LAST_STEP;
  btnSubmit.hidden = index !== LAST_STEP;
  if (index === LAST_STEP) renderReview();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function validateStep(index) {
  const section = steps[index];
  const requiredInputs = section.querySelectorAll("[required]");
  for (const input of requiredInputs) {
    if (input.offsetParent === null) continue; // skip hidden fields
    if (!input.value || !input.value.trim()) {
      input.focus();
      input.reportValidity?.();
      return false;
    }
  }
  if (index === 5 && !state.degree_mode) {
    alert("Please choose how you're planning to pursue your next degree.");
    return false;
  }
  if (index === 5 && !state.counseling_interest) {
    alert("Please let us know if you'd like counseling help.");
    return false;
  }
  return true;
}

btnNext.addEventListener("click", () => {
  if (!validateStep(state.step)) return;
  state.step = Math.min(state.step + 1, LAST_STEP);
  showStep(state.step);
});

btnBack.addEventListener("click", () => {
  state.step = Math.max(state.step - 1, 0);
  showStep(state.step);
});

function val(id) {
  const el = document.getElementById(id);
  return el ? el.value.trim() : "";
}

function renderReview() {
  const card = document.getElementById("review-card");
  card.innerHTML = `
    <div><b>Name:</b> ${escapeHtml(val("name"))}</div>
    <div><b>Contact:</b> ${escapeHtml(val("email"))} · ${escapeHtml(val("phone"))}</div>
    <div><b>Education:</b> ${escapeHtml(val("current_education"))}${val("degree_course") ? " — " + escapeHtml(val("degree_course")) : ""}</div>
    <div><b>Skills:</b> ${state.skills.map(escapeHtml).join(", ") || "—"}</div>
    <div><b>Interests:</b> ${state.interests.map(escapeHtml).join(", ") || "—"}</div>
    <div><b>Goal:</b> ${escapeHtml(val("career_goals"))}</div>
    <div><b>Degree plan:</b> ${escapeHtml(state.degree_mode || "—")}</div>
    <div><b>Counseling:</b> ${escapeHtml(state.counseling_interest || "—")}</div>
  `;
}

// ---------------- Submission ----------------

btnSubmit.addEventListener("click", async () => {
  if (!validateStep(0) || !state.degree_mode || !state.counseling_interest) {
    alert("Please complete all required fields before submitting.");
    return;
  }

  const payload = {
    profile: {
      name: val("name"),
      email: val("email"),
      phone: val("phone"),
      current_education: val("current_education"),
      degree_course: val("degree_course") || null,
      college: val("college") || null,
      current_year: val("current_year") || null,
      skills: state.skills,
      interests: state.interests,
      career_goals: val("career_goals"),
      preferred_career_field: val("preferred_career_field") || null,
      current_experience: val("current_experience") || null,
      preferred_location: val("preferred_location") || null,
      budget_preference: val("budget_preference") || null,
      degree_mode: state.degree_mode,
      counseling_interest: state.counseling_interest,
      preferred_specialization: val("preferred_specialization") || null,
    },
  };

  quizForm.hidden = true;
  stepnav.hidden = true;
  loadingEl.hidden = false;

  try {
    const res = await fetch(`${API_BASE}/api/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.detail || `Request failed (${res.status})`);
    }
    const data = await res.json();
    loadingEl.hidden = true;
    renderResults(data);
  } catch (err) {
    loadingEl.hidden = true;
    resultsEl.hidden = false;
    resultsEl.innerHTML = `<div class="error-box">Something went wrong generating your report: ${escapeHtml(err.message)}.
      Make sure the backend server is running (see README.md), then refresh and try again.</div>`;
  }
});

function renderResults(data) {
  const { report, is_lead, lead_type } = data;
  resultsEl.hidden = false;

  const leadBanner = is_lead
    ? `<div class="lead-banner">✺ Based on your answers, one of our counselors can help you further (${escapeHtml(lead_type)}). We've noted your interest — someone may reach out with more information.</div>`
    : `<div class="lead-banner">✺ Here's your personalized career guidance — no counseling follow-up requested.</div>`;

  const careerCards = report.recommended_career_paths
    .map(
      (cp) => `
    <div class="career-card">
      <h3>${escapeHtml(cp.title)}</h3>
      <p>${escapeHtml(cp.why_it_suits)}</p>
      <div class="pill-row">${cp.relevant_roles.map((r) => `<span class="pill">${escapeHtml(r)}</span>`).join("")}</div>
      <div class="pill-row">${cp.skills_required.map((s) => `<span class="pill">${escapeHtml(s)}</span>`).join("")}${cp.skill_gaps.map((g) => `<span class="pill gap">gap: ${escapeHtml(g)}</span>`).join("")}</div>
    </div>`
    )
    .join("");

  const degreeCards = report.recommended_degrees
    .map(
      (d) => `
    <div class="career-card">
      <h3>${escapeHtml(d.career_goal)}</h3>
      <p>${escapeHtml(d.notes || "")}</p>
      <div class="pill-row">${d.suitable_degrees.map((s) => `<span class="pill">${escapeHtml(s)}</span>`).join("")}</div>
    </div>`
    )
    .join("");

  const institutionRows = report.recommended_institutions
    .map(
      (i) => `
    <div class="institution-row">
      <div><b>${escapeHtml(i.name)}</b><br><span style="color:var(--ink-soft); font-size:0.85rem;">${escapeHtml(i.reason)}</span></div>
      <span class="badge">${escapeHtml(i.type)}</span>
    </div>`
    )
    .join("");

  resultsEl.innerHTML = `
    ${leadBanner}

    <div class="result-block">
      <h2>Your career profile</h2>
      <p class="summary-text">${escapeHtml(report.career_profile_summary)}</p>
    </div>

    <div class="result-block">
      <h2>Recommended career paths</h2>
      ${careerCards}
    </div>

    <div class="result-block">
      <h2>Suitable job roles</h2>
      <div class="chip-list">${report.suitable_job_roles.map((r) => `<span class="chip">${escapeHtml(r)}</span>`).join("")}</div>
    </div>

    <div class="result-block">
      <h2>Skills you should learn</h2>
      <div class="chip-list">${report.skills_to_learn.map((s) => `<span class="chip">${escapeHtml(s)}</span>`).join("")}</div>
    </div>

    <div class="result-block">
      <h2>Recommended degree programs</h2>
      ${degreeCards}
    </div>

    <div class="result-block">
      <h2>Recommended universities / colleges</h2>
      ${institutionRows}
    </div>

    <div class="result-block">
      <h2>Your action plan</h2>
      <div class="plan-columns">
        <div class="plan-col">
          <h4>Next 3–6 months</h4>
          <ul>${report.action_plan.short_term.map((a) => `<li>${escapeHtml(a)}</li>`).join("")}</ul>
        </div>
        <div class="plan-col">
          <h4>Next 1–3 years</h4>
          <ul>${report.action_plan.long_term.map((a) => `<li>${escapeHtml(a)}</li>`).join("")}</ul>
        </div>
      </div>
    </div>

    <div class="result-block">
      <h2>Overall recommendation</h2>
      <div class="recommendation-box">${escapeHtml(report.overall_recommendation)}</div>
    </div>
  `;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// init
showStep(0);
