// Chart.js helper render functions

const chartInstances = {};

function initCutoffTrendsChart(canvasId, trendsData) {
  if (chartInstances[canvasId]) chartInstances[canvasId].destroy();

  const years = [2021, 2022, 2023, 2024, 2025];
  const branches = ["CSE", "AI_DS", "ECE", "ME", "CE"];
  const colors = ["#6366f1", "#06b6d4", "#10b981", "#f59e0b", "#f43f5e"];

  const datasets = branches.map((br, idx) => {
    const data = years.map(y => {
      const match = trendsData.find(d => d.year === y && d.branch_code === br);
      return match ? match.avg_closing_rank : null;
    });
    return {
      label: br,
      data: data,
      borderColor: colors[idx],
      backgroundColor: colors[idx],
      tension: 0.3,
      borderWidth: 2
    };
  });

  const ctx = document.getElementById(canvasId).getContext("2d");
  chartInstances[canvasId] = new Chart(ctx, {
    type: "line",
    data: { labels: years, datasets: datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#94a3b8", font: { family: "Plus Jakarta Sans" } } }
      },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
        y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" }, title: { display: true, text: "Closing Rank", color: "#94a3b8" } }
      }
    }
  });
}

function initFeePlacementChart(canvasId, scatterData) {
  if (chartInstances[canvasId]) chartInstances[canvasId].destroy();

  const datasets = [
    { label: "Tier 1", data: [], backgroundColor: "#6366f1" },
    { label: "Tier 2", data: [], backgroundColor: "#06b6d4" },
    { label: "Tier 3", data: [], backgroundColor: "#94a3b8" }
  ];

  scatterData.forEach(item => {
    const point = { x: item.tuition_fee_annual_lakhs, y: item.avg_placement_lpa, label: item.short_name };
    if (item.tier === "Tier 1") datasets[0].data.push(point);
    else if (item.tier === "Tier 2") datasets[1].data.push(point);
    else datasets[2].data.push(point);
  });

  const ctx = document.getElementById(canvasId).getContext("2d");
  chartInstances[canvasId] = new Chart(ctx, {
    type: "scatter",
    data: { datasets: datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#94a3b8" } },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.raw.label}: Fee ${ctx.raw.x}L, Package ${ctx.raw.y} LPA`
          }
        }
      },
      scales: {
        x: { title: { display: true, text: "Annual Tuition Fee (INR Lakhs)", color: "#94a3b8" }, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
        y: { title: { display: true, text: "Average Package (LPA)", color: "#94a3b8" }, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } }
      }
    }
  });
}

function initBranchDemandChart(canvasId, branchData) {
  if (chartInstances[canvasId]) chartInstances[canvasId].destroy();

  const labels = branchData.map(b => b.branch_code);
  const ranks = branchData.map(b => b.avg_closing_rank);

  const ctx = document.getElementById(canvasId).getContext("2d");
  chartInstances[canvasId] = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Avg Closing Rank",
        data: ranks,
        backgroundColor: "rgba(6, 182, 212, 0.7)",
        borderColor: "#06b6d4",
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { display: false } },
        y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } }
      }
    }
  });
}

function initLocationChart(canvasId, locData) {
  if (chartInstances[canvasId]) chartInstances[canvasId].destroy();

  const labels = locData.map(l => l.state);
  const counts = locData.map(l => l.college_count);

  const ctx = document.getElementById(canvasId).getContext("2d");
  chartInstances[canvasId] = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "College Count",
        data: counts,
        backgroundColor: "rgba(99, 102, 241, 0.7)",
        borderColor: "#6366f1",
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: "y",
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
        y: { ticks: { color: "#94a3b8" }, grid: { display: false } }
      }
    }
  });
}

function initFeatureImportanceChart(canvasId, featImpData) {
  if (chartInstances[canvasId]) chartInstances[canvasId].destroy();

  const labels = featImpData.map(f => f.feature);
  const values = featImpData.map(f => f.importance);

  const ctx = document.getElementById(canvasId).getContext("2d");
  chartInstances[canvasId] = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Feature Importance",
        data: values,
        backgroundColor: "rgba(16, 185, 129, 0.7)",
        borderColor: "#10b981",
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: "y",
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
        y: { ticks: { color: "#94a3b8" }, grid: { display: false } }
      }
    }
  });
}
