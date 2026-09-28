/**
 * Incident Response Agent - Core Frontend Application & Dashboard Engine
 */

const API_BASE = "";
let trendChartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    checkSystemStatus();
    
    // If on dashboard page, load stats & charts
    if (window.location.pathname === "/dashboard" || window.location.pathname === "/" || window.location.pathname.endsWith("dashboard.html")) {
        loadDashboardData();
    }
});

// Update active sidebar item
function initNavigation() {
    const currentPath = window.location.pathname.toLowerCase();
    const navItems = document.querySelectorAll(".nav-item a");
    
    navItems.forEach(item => {
        const href = (item.getAttribute("href") || "").toLowerCase();
        const baseHref = href.replace("/static/", "").replace("/", "").replace(".html", "");
        const baseCurrent = currentPath.replace("/static/", "").replace("/", "").replace(".html", "");
        
        if (
            href === currentPath ||
            (baseCurrent === "" && baseHref === "dashboard") ||
            (baseCurrent === "index" && baseHref === "dashboard") ||
            (baseCurrent && baseHref && baseCurrent === baseHref)
        ) {
            item.parentElement.classList.add("active");
        } else {
            item.parentElement.classList.remove("active");
        }
    });
}

// Check Backend and Hindsight Connection Status
async function checkSystemStatus() {
    const statusBadge = document.getElementById("hindsight-status-badge");
    const statusText = document.getElementById("hindsight-status-text");
    
    try {
        const res = await fetch(`${API_BASE}/api/status`);
        if (!res.ok) throw new Error("Backend unreachable");
        
        const data = await res.json();
        if (statusBadge && statusText) {
            if (data.hindsight.is_configured) {
                statusText.textContent = "Hindsight Memory: Connected";
                statusBadge.style.color = "var(--accent-emerald)";
            } else {
                statusText.textContent = "Hindsight: Synthetic Demo Bank";
                statusBadge.style.color = "var(--accent-cyan)";
            }
        }
    } catch (err) {
        if (statusBadge && statusText) {
            statusText.textContent = "Backend: Offline";
            statusBadge.style.color = "var(--accent-rose)";
        }
    }
}

// Format ISO date to readable string
function formatTimestamp(isoStr) {
    if (!isoStr) return "N/A";
    const d = new Date(isoStr);
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

// Severity Badge HTML helper
function getSeverityBadge(sev) {
    const s = (sev || "LOW").toUpperCase();
    if (s === "HIGH") return `<span class="badge badge-high">High</span>`;
    if (s === "MEDIUM") return `<span class="badge badge-med">Medium</span>`;
    return `<span class="badge badge-low">Low</span>`;
}

// Status Badge HTML helper
function getStatusBadge(stat) {
    const s = (stat || "OPEN").toUpperCase();
    if (s === "RESOLVED") return `<span class="badge badge-resolved">Resolved</span>`;
    if (s === "INVESTIGATING") return `<span class="badge badge-investigating">Investigating</span>`;
    return `<span class="badge badge-open">Open</span>`;
}

// Load Dashboard Analytics & Incidents Table
async function loadDashboardData() {
    try {
        const res = await fetch(`${API_BASE}/api/dashboard/stats`);
        if (!res.ok) throw new Error("Failed to fetch dashboard metrics");
        const data = await res.json();

        // 1. Update 6 Metric Cards
        const elTotal = document.getElementById("stat-total");
        const elOpen = document.getElementById("stat-open");
        const elResolved = document.getElementById("stat-resolved");
        const elHigh = document.getElementById("stat-high");
        const elMedium = document.getElementById("stat-medium");
        const elLow = document.getElementById("stat-low");

        if (elTotal) elTotal.textContent = data.total_incidents;
        if (elOpen) elOpen.textContent = data.open_incidents;
        if (elResolved) elResolved.textContent = data.resolved_incidents;
        if (elHigh) elHigh.textContent = data.high_severity;
        if (elMedium) elMedium.textContent = data.medium_severity;
        if (elLow) elLow.textContent = data.low_severity;

        // 2. Render Categories Breakdown
        renderCategories(data.categories, data.total_incidents);

        // 3. Render Incident Trend Chart
        renderTrendChart(data.trend_data);

        // 4. Render Recent Incidents Table
        renderRecentIncidents(data.recent_incidents);

    } catch (err) {
        console.error("Error loading dashboard data:", err);
    }
}

// Render Categories with Progress Bars
function renderCategories(categories, total) {
    const container = document.getElementById("category-distribution-container");
    if (!container) return;

    if (!categories || Object.keys(categories).length === 0) {
        container.innerHTML = `<div style="color:var(--text-muted); font-size:0.85rem;">No incidents recorded yet.</div>`;
        return;
    }

    let html = "";
    for (const [catName, count] of Object.entries(categories)) {
        const percent = total > 0 ? Math.round((count / total) * 100) : 0;
        html += `
            <div class="category-item">
                <div class="category-header">
                    <span class="category-name">${catName}</span>
                    <span class="category-count">${count} (${percent}%)</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: ${percent}%;"></div>
                </div>
            </div>
        `;
    }
    container.innerHTML = html;
}

// Render Modern Cyber Trend Chart with Chart.js
function renderTrendChart(trendData) {
    const canvas = document.getElementById("incidentTrendChart");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (trendChartInstance) {
        trendChartInstance.destroy();
    }

    // Create subtle cyan gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 240);
    gradient.addColorStop(0, "rgba(6, 182, 212, 0.4)");
    gradient.addColorStop(1, "rgba(6, 182, 212, 0.0)");

    trendChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: trendData.labels || ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            datasets: [{
                label: "Incident Ingestion Rate",
                data: trendData.values || [2, 4, 3, 5, 8, 4, 8],
                borderColor: "#06b6d4",
                borderWidth: 2.5,
                backgroundColor: gradient,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: "#06b6d4",
                pointBorderColor: "#fff",
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "#111827",
                    titleColor: "#f9fafb",
                    bodyColor: "#06b6d4",
                    borderColor: "rgba(6, 182, 212, 0.3)",
                    borderWidth: 1,
                    padding: 10
                }
            },
            scales: {
                x: {
                    grid: { color: "rgba(255, 255, 255, 0.05)" },
                    ticks: { color: "#9ca3af", font: { size: 11 } }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: "rgba(255, 255, 255, 0.05)" },
                    ticks: { color: "#9ca3af", stepSize: 2, font: { size: 11 } }
                }
            }
        }
    });
}

// Render Recent Incidents in Table
function renderRecentIncidents(incidents) {
    const tbody = document.getElementById("recent-incidents-table-body");
    if (!tbody) return;

    if (!incidents || incidents.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align:center; color:var(--text-muted); padding:2rem;">
                    No recent incidents logged. Click "+ New Incident" to submit one.
                </td>
            </tr>
        `;
        return;
    }

    let rows = "";
    incidents.forEach(inc => {
        rows += `
            <tr>
                <td class="incident-id">${inc.id}</td>
                <td class="incident-title-cell" title="${inc.title}">
                    <div style="font-weight:600;">${inc.title}</div>
                    <div style="font-size:0.75rem; color:var(--text-muted);">${inc.description.substring(0, 60)}...</div>
                </td>
                <td><span style="font-size:0.8rem; color:var(--text-secondary);">${inc.type}</span></td>
                <td>${getSeverityBadge(inc.severity)}</td>
                <td>${getStatusBadge(inc.status)}</td>
                <td><code style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-secondary);">${inc.affected_system || "N/A"}</code></td>
                <td style="font-size:0.78rem; color:var(--text-muted);">${formatTimestamp(inc.timestamp || inc.created_at)}</td>
                <td>
                    <a href="/static/analysis.html?id=${inc.id}" class="btn btn-outline btn-sm">Triage & AI →</a>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = rows;
}
