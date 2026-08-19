// Master App Controller
const API_BASE = "/api";

document.addEventListener("DOMContentLoaded", () => {
  initTabNavigation();
  loadDataQualityMetrics();
  loadOverviewKPIs();
  loadEDAVisualizations();
  loadSQLQuestions();
  loadDashboardColleges();
  loadMLMetrics();
  initFormListeners();
  initKarnatakaListeners();
});

// ── Tab Switcher ──────────────────────────────────────────────
function initTabNavigation() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", (e) => {
      e.preventDefault();
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
      tab.classList.add("active");
      const pane = document.getElementById(tab.getAttribute("data-tab"));
      if (pane) pane.classList.add("active");
    });
  });
}

// ── Data Quality & ETL ───────────────────────────────────────
async function loadDataQualityMetrics() {
  try {
    const res = await fetch(`${API_BASE}/data-quality`);
    const d = await res.json();
    document.getElementById("dq-health-score").innerText = `${d.dataset_health_score}%`;
    document.getElementById("dq-raw-records").innerText = d.raw_records.toLocaleString();
    document.getElementById("dq-duplicates").innerText = d.duplicates_removed.toLocaleString();
    document.getElementById("dq-missing").innerText = d.missing_values_before.toLocaleString();
    document.getElementById("dq-outliers").innerText = d.outliers_detected.toLocaleString();
  } catch (err) { console.error("Data Quality load failed:", err); }
}

// ── Overview KPIs ────────────────────────────────────────────
async function loadOverviewKPIs() {
  try {
    const res = await fetch(`${API_BASE}/overview`);
    const d = await res.json();
    document.getElementById("kpi-total-colleges").innerText = d.total_colleges;
    document.getElementById("kpi-avg-fee").innerText = `INR ${d.avg_tuition_fee_lakhs}L`;
    document.getElementById("kpi-avg-placement").innerText = `${d.avg_placement_lpa} LPA`;
    document.getElementById("kpi-avg-cutoff").innerText = `#${d.avg_cutoff_rank.toLocaleString()}`;
    document.getElementById("kpi-best-roi").innerText = d.best_roi_college;
  } catch (err) { console.error("Overview KPIs load failed:", err); }
}

// ── Dashboard College Grid ───────────────────────────────────
async function loadDashboardColleges() {
  try {
    const tier = document.getElementById("filter-tier").value;
    const state = document.getElementById("filter-state").value;
    const maxFee = document.getElementById("filter-max-fee").value;
    const minPlacement = document.getElementById("filter-min-placement").value;
    let url = `${API_BASE}/colleges?`;
    if (tier) url += `tier=${encodeURIComponent(tier)}&`;
    if (state) url += `state=${encodeURIComponent(state)}&`;
    if (maxFee) url += `max_fee=${maxFee}&`;
    if (minPlacement) url += `min_placement=${minPlacement}&`;
    const res = await fetch(url);
    const colleges = await res.json();
    const tbody = document.querySelector("#dashboard-colleges-table tbody");
    tbody.innerHTML = "";
    colleges.slice(0, 15).forEach(c => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><span class="tag">#${c.nirf_rank}</span></td>
        <td><strong>${c.college_name}</strong></td>
        <td>${c.city}, ${c.state}</td>
        <td>${c.tier}</td>
        <td>INR ${c.tuition_fee_annual_lakhs}L</td>
        <td>INR ${c.hostel_fee_annual_lakhs}L</td>
        <td><strong style="color:#34d399;">${c.avg_placement_lpa} LPA</strong></td>
        <td>${c.placement_rate_pct}%</td>
        <td>${c.accreditation}</td>`;
      tbody.appendChild(tr);
    });
  } catch (err) { console.error("Dashboard Colleges load failed:", err); }
}

// ── EDA Visualizations ───────────────────────────────────────
async function loadEDAVisualizations() {
  try {
    const res = await fetch(`${API_BASE}/eda/visualizations`);
    const eda = await res.json();
    initCutoffTrendsChart("chart-cutoff-trends", eda.cutoff_trends.data);
    initFeePlacementChart("chart-fee-placement", eda.fee_vs_placement.data);
    initBranchDemandChart("chart-branch-demand", eda.branch_demand.data);
    initLocationChart("chart-location-dist", eda.location_distribution.data);
  } catch (err) { console.error("EDA load failed:", err); }
}

// ── SQL Analytics ────────────────────────────────────────────
async function loadSQLQuestions() {
  try {
    const res = await fetch(`${API_BASE}/sql/questions`);
    const questions = await res.json();
    const container = document.getElementById("sql-questions-list");
    container.innerHTML = "";
    questions.forEach((q, idx) => {
      const item = document.createElement("div");
      item.className = `sql-q-item ${idx === 0 ? "active" : ""}`;
      item.innerText = `${idx + 1}. ${q.question}`;
      item.addEventListener("click", () => {
        document.querySelectorAll(".sql-q-item").forEach(el => el.classList.remove("active"));
        item.classList.add("active");
        runPredefinedSQL(q.id);
      });
      container.appendChild(item);
    });
    if (questions.length > 0) runPredefinedSQL(questions[0].id);
  } catch (err) { console.error("SQL Questions load failed:", err); }
}

async function runPredefinedSQL(questionId) {
  try {
    const res = await fetch(`${API_BASE}/sql/execute-predefined/${questionId}`);
    const result = await res.json();
    document.getElementById("sql-editor").value = result.sql;
    document.getElementById("sql-insight-text").innerText = result.insight;
    renderSQLResultsTable(result.columns, result.data);
  } catch (err) { console.error("Predefined SQL failed:", err); }
}

async function runCustomSQL() {
  const sql = document.getElementById("sql-editor").value;
  try {
    const res = await fetch(`${API_BASE}/sql/execute-custom`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sql_query: sql })
    });
    const result = await res.json();
    if (result.error) { alert(`SQL Error: ${result.error}`); }
    else {
      document.getElementById("sql-insight-text").innerText =
        `Query executed. ${result.row_count} rows returned.`;
      renderSQLResultsTable(result.columns, result.data);
    }
  } catch (err) { console.error("Custom SQL failed:", err); }
}

function renderSQLResultsTable(columns, rows) {
  const container = document.getElementById("sql-results-table-container");
  if (!rows || rows.length === 0) {
    container.innerHTML = "<p class='placeholder-text'>No records returned.</p>";
    return;
  }
  let html = `<table class="data-table"><thead><tr>`;
  columns.forEach(col => html += `<th>${col}</th>`);
  html += `</tr></thead><tbody>`;
  rows.forEach(row => {
    html += `<tr>`;
    columns.forEach(col => html += `<td>${row[col]}</td>`);
    html += `</tr>`;
  });
  html += `</tbody></table>`;
  container.innerHTML = html;
}

// ── ML Metrics ───────────────────────────────────────────────
async function loadMLMetrics() {
  try {
    const res = await fetch(`${API_BASE}/ml/metrics`);
    const meta = await res.json();
    const tbody = document.querySelector("#ml-metrics-table tbody");
    tbody.innerHTML = "";
    Object.entries(meta.metrics_comparison).forEach(([name, m]) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${name}</strong> ${name === meta.best_model_name ? '<span class="tag">Best</span>' : ''}</td>
        <td>${(m.accuracy * 100).toFixed(1)}%</td>
        <td>${(m.precision * 100).toFixed(1)}%</td>
        <td>${(m.recall * 100).toFixed(1)}%</td>
        <td><strong style="color:#6366f1;">${(m.f1_score * 100).toFixed(1)}%</strong></td>
        <td>${(m.roc_auc * 100).toFixed(1)}%</td>`;
      tbody.appendChild(tr);
    });
    initFeatureImportanceChart("chart-feature-importance", meta.feature_importance);
    document.getElementById("ml-metadata-container").innerHTML = `
      <div class="kpi-card"><span class="kpi-label">Model Version</span><span class="kpi-value" style="font-size:1.2rem;">${meta.model_version}</span></div>
      <div class="kpi-card"><span class="kpi-label">Last Trained</span><span class="kpi-value" style="font-size:1.1rem;">${meta.timestamp}</span></div>
      <div class="kpi-card"><span class="kpi-label">Dataset Size</span><span class="kpi-value" style="font-size:1.2rem;">${meta.dataset_size.toLocaleString()} Rows</span></div>`;
  } catch (err) { console.error("ML Metrics load failed:", err); }
}

// ── Form Listeners ───────────────────────────────────────────
function initFormListeners() {

  // ETL re-run button
  document.getElementById("btn-trigger-etl").addEventListener("click", async () => {
    alert("Re-executing ETL Data Cleaning Pipeline...");
    const res = await fetch(`${API_BASE}/data-quality/trigger-etl`, { method: "POST" });
    const data = await res.json();
    loadDataQualityMetrics();
    alert(`ETL Completed! Dataset Health Score: ${data.dataset_health_score}%`);
  });

  // Custom SQL button
  document.getElementById("btn-run-custom-sql").addEventListener("click", runCustomSQL);

  // Dashboard Filters
  document.getElementById("btn-apply-filters").addEventListener("click", loadDashboardColleges);

  // ── Predictor Form ─────────────────────────────────────────
  document.getElementById("form-predict").addEventListener("submit", async (e) => {
    e.preventDefault();
    const submitBtn = e.currentTarget.querySelector("button[type='submit']");
    const req = {
      entrance_rank: parseInt(document.getElementById("pred-rank").value),
      closing_rank: parseInt(document.getElementById("pred-closing").value),
      annual_budget: parseFloat(document.getElementById("pred-budget").value),
      tuition_fee: parseFloat(document.getElementById("pred-fee").value),
      avg_placement_lpa: parseFloat(document.getElementById("pred-placement").value),
      tier: document.getElementById("pred-tier").value,
      model_choice: document.getElementById("pred-model").value
    };
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Calculating\u2026';
    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req)
      });
      const result = await res.json();
      if (!res.ok) throw new Error(result.detail || "Prediction failed.");
      const pct = (result.admission_probability * 100).toFixed(1);
      document.getElementById("prob-percentage").innerText = `${pct}%`;
      document.getElementById("prob-classification").innerText =
        pct >= 60 ? "High Admission Probability"
        : pct >= 40 ? "Moderate Chance (Target Spot Round)" : "Low Chance";
      document.getElementById("res-rank-gap").innerText =
        result.rank_gap > 0 ? `+${result.rank_gap}` : result.rank_gap;
      document.getElementById("res-rank-fit").innerText = `${result.rank_fit}x`;
      document.getElementById("res-fee-aff").innerText = `${result.fee_affordability_ratio}x`;
      document.getElementById("res-model-used").innerText = result.model_used;
      document.getElementById("prob-circle-display").style.background =
        `conic-gradient(#6366f1 ${pct}%, rgba(255,255,255,0.1) ${pct}%)`;
    } catch (err) {
      document.getElementById("prob-classification").innerText = `Unable to calculate: ${err.message}`;
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="fa-solid fa-calculator"></i> Predict Admission Probability';
    }
  });

  // ── Recommendation Form ────────────────────────────────────
  const formRec = document.getElementById("form-recommend");
  if (formRec) {
    formRec.addEventListener("submit", async (e) => {
      e.preventDefault();
      const req = {
        entrance_rank: parseInt(document.getElementById("rec-rank").value),
        category: document.getElementById("rec-category").value,
        preferred_branch: document.getElementById("rec-branch").value,
        max_annual_budget: 999.0
      };
      const container = document.getElementById("recs-results-container");
      container.innerHTML = "<p class='placeholder-text'><i class='fa-solid fa-spinner fa-spin'></i> Finding best matches\u2026</p>";
      try {
        const res = await fetch(`${API_BASE}/recommend`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify(req)
        });
        const recs = await res.json();
        if (!res.ok) throw new Error(recs.detail || "Recommendations failed.");
        container.innerHTML = "";
        recs.forEach(r => {
          const card = document.createElement("div");
          card.className = "rec-card";
          card.innerHTML = `
            <div class="rec-header">
              <div>
                <div class="rec-title">${r.college_name}</div>
                <div class="rec-sub">${r.city}, ${r.state} | ${r.tier} | Branch: ${r.branch_code}</div>
              </div>
              <div class="rec-badge">${r.overall_match_score}% Match</div>
            </div>
            <div class="score-bars">
              <div class="bar-row"><span class="bar-label">Admission Prob</span><div class="bar-track"><div class="bar-fill" style="width:${r.score_breakdown.admission_probability}%;"></div></div><span>${r.score_breakdown.admission_probability}%</span></div>
              <div class="bar-row"><span class="bar-label">Rank Fit</span><div class="bar-track"><div class="bar-fill" style="width:${r.score_breakdown.rank_fit}%;"></div></div><span>${r.score_breakdown.rank_fit}%</span></div>
              <div class="bar-row"><span class="bar-label">Placement Score</span><div class="bar-track"><div class="bar-fill" style="width:${r.score_breakdown.placement_score}%;"></div></div><span>${r.score_breakdown.placement_score}%</span></div>
            </div>
            <div class="decision-tags">
              ${r.decision_factors.map(f => '<span class="tag"><i class="fa-solid fa-check"></i> ' + f + '</span>').join("")}
            </div>`;
          container.appendChild(card);
        });
        if (recs.length === 0) container.innerHTML = "<p class='placeholder-text'>No matches found.</p>";
      } catch (err) {
        container.innerHTML = `<div class="insight-alert">Unable to load recommendations: ${err.message}</div>`;
      }
    });
    formRec.dispatchEvent(new Event("submit"));
  }

  // ── RAG / LLM Chat ────────────────────────────────────────
  const formChat = document.getElementById("form-chat");
  if (formChat) {
    formChat.addEventListener("submit", async (e) => {
      e.preventDefault();
      const inputEl = document.getElementById("chat-input");
      const prompt = inputEl.value.trim();
      if (!prompt) return;
      appendChatMessage("user", prompt);
      inputEl.value = "";
      const submitBtn = formChat.querySelector("button[type='submit']");
      submitBtn.disabled = true;
      const pending = appendChatMessage("bot", "Thinking\u2026");
      try {
        const res = await fetch(`${API_BASE}/llm/assistant`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt })
        });
        const ans = await res.json();
        if (!res.ok) throw new Error(ans.detail || "Assistant could not answer.");
        pending.remove();
        appendChatMessage("bot", ans.response);
        if (ans.sources && ans.sources.length > 0) renderRAGSources(ans.sources);
      } catch (err) {
        pending.querySelector(".msg-text").innerText = `Unable to answer: ${err.message}`;
      } finally { submitBtn.disabled = false; }
    });

    // Quick-query pill buttons
    document.querySelectorAll(".quick-pill").forEach(btn => {
      btn.addEventListener("click", () => {
        document.getElementById("chat-input").value = btn.getAttribute("data-prompt");
        formChat.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
      });
    });
  }
} // end initFormListeners


// ── appendChatMessage ────────────────────────────────────────
function appendChatMessage(sender, text) {
  const container = document.getElementById("chat-history-box");
  const div = document.createElement("div");
  div.className = `chat-msg ${sender}`;

  let fmt = text
    .replace(/^### (.*$)/gim, '<h4 style="margin-top:12px;margin-bottom:8px;color:#38bdf8;">$1</h4>')
    .replace(/^#### (.*$)/gim, '<h5 style="margin-top:10px;margin-bottom:6px;color:#a5b4fc;">$1</h5>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>');

  const lines = fmt.split('\n');
  let inTable = false, tableHtml = '', finalLines = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith('|') && line.endsWith('|')) {
      if (line.includes(':---') || line.includes('---')) continue;
      const cells = line.split('|').map(c => c.trim()).filter((c, idx, arr) => idx > 0 && idx < arr.length - 1);
      if (!inTable) {
        inTable = true;
        tableHtml = '<div class="table-responsive"><table class="data-table" style="margin:10px 0;"><thead><tr>';
        cells.forEach(c => tableHtml += `<th>${c}</th>`);
        tableHtml += '</tr></thead><tbody>';
      } else {
        tableHtml += '<tr>';
        cells.forEach(c => tableHtml += `<td>${c}</td>`);
        tableHtml += '</tr>';
      }
    } else {
      if (inTable) { inTable = false; tableHtml += '</tbody></table></div>'; finalLines.push(tableHtml); tableHtml = ''; }
      finalLines.push(line);
    }
  }
  if (inTable) { tableHtml += '</tbody></table></div>'; finalLines.push(tableHtml); }

  div.innerHTML = `
    <div class="msg-author">${sender === "user" ? "You" : "EduAnalytics AI Assistant"}</div>
    <div class="msg-text">${finalLines.join('<br>')}</div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}


// ── renderRAGSources ─────────────────────────────────────────
function renderRAGSources(sources) {
  const container = document.getElementById("rag-sources-container");
  let html = '<h4 class="margin-bottom-sm"><i class="fa-solid fa-file-contract text-accent"></i> Verified Document Citations</h4>';
  sources.forEach(s => {
    html += `
      <div class="highlight-item margin-bottom-sm">
        <i class="fa-solid fa-file-lines highlight-icon"></i>
        <div>
          <strong>${s.document_name}</strong><br>
          <span style="font-size:0.75rem;color:#94a3b8;">Section ${s.section} | Verified: ${s.verification_date} | Cosine: ${s.relevance_score}</span>
        </div>
      </div>`;
  });
  container.innerHTML = html;
}


// ── Karnataka Listeners ──────────────────────────────────────
function initKarnatakaListeners() {
  const formSch = document.getElementById("form-karnataka-scholarship");
  if (formSch) {
    formSch.addEventListener("submit", async (e) => {
      e.preventDefault();
      const req = {
        category: document.getElementById("kar-category").value,
        annual_income: parseFloat(document.getElementById("kar-income").value),
        is_kannada_medium: document.getElementById("kar-kannada-med").checked,
        is_rural: document.getElementById("kar-kannada-med").checked,
        kcet_rank: parseInt(document.getElementById("kar-rank").value),
        tuition_fee: parseFloat(document.getElementById("kar-fee").value)
      };
      const res = await fetch(`${API_BASE}/karnataka/scholarship-check`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req)
      });
      const data = await res.json();
      const container = document.getElementById("kar-scholarship-results");
      let html = `
        <div class="insight-alert" style="background:rgba(16,185,129,0.12);border-color:rgba(16,185,129,0.4);color:#6ee7b7;margin-bottom:16px;">
          <strong><i class="fa-solid fa-building-columns"></i> Official Govt Sourced Eligibility (${data.candidate_category})</strong><br>
          <span>Total Fee Waiver: <strong>INR ${data.total_estimated_annual_benefit.toLocaleString()}/yr</strong> | Net Payable: <strong>INR ${data.net_effective_fee.toLocaleString()}</strong></span>
        </div>`;
      data.schemes.forEach(s => {
        html += `
          <div class="highlight-item margin-bottom-sm">
            <i class="fa-solid fa-graduation-cap highlight-icon"></i>
            <div>
              <strong>${s.name}</strong> (${s.authority})<br>
              <span class="text-accent">${s.benefit}</span><br>
              <span style="font-size:0.78rem;color:#94a3b8;">
                Portal: <a href="${s.portal}" target="_blank" style="color:#38bdf8;text-decoration:underline;"><i class="fa-solid fa-arrow-up-right-from-square"></i> Visit</a> |
                Docs: ${s.documents_required.join(", ")}
              </span>
            </div>
          </div>`;
      });
      container.innerHTML = html;
    });
    formSch.dispatchEvent(new Event("submit"));
  }

  const formGuide = document.getElementById("form-karnataka-guide");
  if (formGuide) {
    const runSearch = async () => {
      const sqEl = document.getElementById("kar-search-query");
      const branchEl = document.getElementById("kar-branch");
      const req = {
        search_query: sqEl ? sqEl.value.trim() : null,
        preferred_branch: branchEl ? branchEl.value : "CSE",
        entrance_exam: document.getElementById("kar-exam").value,
        rank: parseInt(document.getElementById("kar-exam-rank").value),
        category: document.getElementById("kar-exam-cat").value,
        max_budget: 999.0
      };
      const res = await fetch(`${API_BASE}/karnataka/college-guide`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req)
      });
      const colleges = await res.json();
      const container = document.getElementById("kar-colleges-results");
      container.innerHTML = "";
      if (colleges.length === 0) {
        container.innerHTML = "<div class='insight-alert'><i class='fa-solid fa-circle-exclamation'></i> No colleges matched. Try a KEA Code (E001, E003\u2026) or college name.</div>";
        return;
      }
      colleges.forEach(c => {
        const div = document.createElement("div");
        div.className = "highlight-item margin-bottom-sm";
        div.innerHTML = `
          <div class="kpi-value" style="font-size:1.1rem;color:#38bdf8;">#${c.kcet_code}</div>
          <div style="flex:1;">
            <strong>${c.college_name}</strong> (${c.location}) \u2014 <span class="tag">NIRF #${c.nirf_rank}</span><br>
            <span>Branch: <strong style="color:#a5b4fc;">${c.selected_branch_name}</strong> | Avg Pkg: <strong style="color:#34d399;">${c.avg_placement_lpa} LPA</strong> (High ${c.highest_placement_lpa} LPA)</span><br>
            <div style="margin-top:6px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;">
              <span class="tag" style="background:rgba(56,189,248,0.18);color:#38bdf8;border:1px solid rgba(56,189,248,0.4);">${c.selected_branch} Cutoff: #${c.category_cutoff_rank}</span>
              <span class="tag">${c.admission_status}</span>
              <a href="${c.website_url}" target="_blank" style="color:#38bdf8;font-size:0.8rem;font-weight:600;text-decoration:underline;"><i class="fa-solid fa-globe"></i> Website</a>
              <a href="${c.govt_portal_url}" target="_blank" style="color:#a5b4fc;font-size:0.8rem;font-weight:600;text-decoration:underline;"><i class="fa-solid fa-shield-halved"></i> KEA</a>
              <span style="font-size:0.75rem;color:#94a3b8;"><i class="fa-solid fa-phone"></i> ${c.contact_phone}</span>
            </div>
          </div>`;
        container.appendChild(div);
      });
    };
    formGuide.addEventListener("submit", (e) => { e.preventDefault(); runSearch(); });
    const sqInput = document.getElementById("kar-search-query");
    if (sqInput) sqInput.addEventListener("input", runSearch);
    const branchSelect = document.getElementById("kar-branch");
    if (branchSelect) branchSelect.addEventListener("change", runSearch);
    runSearch();
  }
}
