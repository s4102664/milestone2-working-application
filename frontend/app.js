// --- bootstrap ---
console.log("app.js loaded");

// ✅ Utility: toast notification
function showToast(msg, type = "info") {
  const t = document.getElementById("toast");
  if (!t) return;
  t.textContent = msg;
  t.className = `toast toast--${type}`;
  t.hidden = false;
  t.style.opacity = "1";
  setTimeout(() => { t.style.transition = "opacity 0.6s"; t.style.opacity = "0"; }, 1800);
  setTimeout(() => { t.hidden = true; t.style.transition = ""; }, 2400);
}

// 🔹 Tabs navigation (Personas)
function initTabs(){
  document.querySelectorAll(".tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((b) => b.classList.remove("is-active"));
      document.querySelectorAll(".panel").forEach((p) => p.classList.remove("is-active"));
      btn.classList.add("is-active");
      document.getElementById(`tab-${btn.dataset.tab}`).classList.add("is-active");
      document.getElementById("crumb").textContent = btn.textContent.replace(/\s*\(.*\)/, "");
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  });
}

// 🩺 Health check (Nielsen #1: visibility of system status)
async function checkHealth() {
  const statusEl = document.getElementById("status");
  if (!statusEl) return;
  try {
    const res = await fetch(`${window.API_BASE}/health`, { mode: "cors" });
    console.log("health status:", res.status);
    const js = await res.json();
    statusEl.textContent = js.ok ? "✅ API is running" : "⚠️ API issue";
    statusEl.style.color = js.ok ? "#00b300" : "#e67e22";
  } catch (e) {
    console.warn("health error:", e);
    statusEl.textContent = "❌ API unreachable";
    statusEl.style.color = "#e74c3c";
  }
}

// 🌍 Level 3A — Compare (Maria)
function initCompare(){
  const form = document.getElementById("form-compare");
  const box  = document.getElementById("compare-result");
  if(!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const country = (fd.get("country") || "AUS").trim();
    const year    = (fd.get("year") || "2024").toString().trim();
    try {
      const res = await fetch(`${window.API_BASE}/coverage/compare?country=${encodeURIComponent(country)}&year=${encodeURIComponent(year)}`, { mode: "cors" });
      const js = await res.json();
      box.innerHTML = "";
      if (js.error) {
        box.innerHTML = `<div class="card error"><h3>Error</h3><p>${js.error}</p></div>`;
        showToast("Invalid year or missing data", "error");
        return;
      }
      box.innerHTML = `
        <div class="card"><h3>Country</h3><p>${js.country}</p></div>
        <div class="card"><h3>Year</h3><p>${js.year}</p></div>
        <div class="card"><h3>Local</h3><p>${js.local}%</p></div>
        <div class="card"><h3>Global Avg</h3><p>${js.global_avg}%</p></div>`;
      showToast("Comparison loaded", "success");
    } catch (err) {
      console.error(err);
      showToast("Failed to load comparison", "error");
    }
  });

  document.getElementById("reset-compare").addEventListener("click", () => {
    form.reset();
    box.innerHTML = "";
  });
}

// 📊 Level 2 — Filter & Sort (Dr. Ahmed)
function renderRows(rows) {
  const tb = document.querySelector("#results-table tbody");
  tb.innerHTML = (rows || []).map(
    (r) => `<tr><td>${r.country}</td><td>${r.vaccine}</td><td>${r.year}</td><td>${r.coverage}</td></tr>`
  ).join("");
}

function initQuery(){
  const form = document.getElementById("form-query");
  if(!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const params = new URLSearchParams({
      country: (fd.get("country") || "").trim(),
      vaccine: (fd.get("vaccine") || "").trim(),
      year: (fd.get("year") || "").toString().trim(),
      sort: fd.get("sort") || "coverage_desc",
    }).toString();

    try {
      const res = await fetch(`${window.API_BASE}/coverage/query?${params}`, { mode: "cors" });
      const js = await res.json();
      renderRows(js.rows || []);
      document.getElementById("results-meta").textContent = `${js.count || 0} rows`;
      showToast("Data refreshed", "success");
    } catch (err) {
      console.error(err);
      showToast("Failed to load data", "error");
    }
  });

  document.getElementById("reset-query").addEventListener("click", () => {
    document.querySelector("#results-table tbody").innerHTML = "";
    document.getElementById("results-meta").textContent = "";
    form.reset();
  });

  // export CSV (client-side)
  document.getElementById("export-csv").addEventListener("click", () => {
    const rows = [...document.querySelectorAll("#results-table tbody tr")].map((tr) =>
      [...tr.children].map((td) => td.textContent)
    );
    if (!rows.length) return showToast("No data to export", "error");
    const head = ["Country", "Vaccine", "Year", "Coverage"];
    const csv = [head, ...rows].map(r => r.map(v => `"${String(v).replace(/"/g,'""')}"`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "coverage_export.csv";
    a.click();
    showToast("CSV exported", "success");
  });
}

// 📈 Level 3B — Trends (Liam)
function initTrends(){
  const form = document.getElementById("form-trends");
  const box  = document.getElementById("trends-result");
  if(!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const vaccine   = (fd.get("vaccine") || "MMR").trim();
    const countries = (fd.get("countries") || "AUS,NZL,GBR").trim();

    try {
      const res = await fetch(`${window.API_BASE}/trends?vaccine=${encodeURIComponent(vaccine)}&countries=${encodeURIComponent(countries)}`, { mode: "cors" });
      const js = await res.json();
      const cards = (js.points || []).map(
        (p) => `<div class="card"><h3>${p.country}</h3><p>Year: ${p.year}</p><p>Coverage: ${p.coverage}%</p></div>`
      ).join("") || `<div class="card"><p>No trend data</p></div>`;
      box.innerHTML = cards;
      showToast("Trends loaded", "success");
    } catch (err) {
      console.error(err);
      showToast("Failed to load trends", "error");
    }
  });

  document.getElementById("reset-trends").addEventListener("click", () => {
    form.reset();
    box.innerHTML = "";
  });
}

// --- init after DOM is ready & scripts loaded ---
window.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initCompare();
  initQuery();
  initTrends();
  checkHealth(); 
});
