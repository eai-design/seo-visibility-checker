let rows = [];

const urlInput = document.getElementById("urlInput");
const downloadSites = document.getElementById("downloadSites");
const copyCommand = document.getElementById("copyCommand");
const csvFile = document.getElementById("csvFile");
const loadLatest = document.getElementById("loadLatest");
const statusBox = document.getElementById("status");
const resultBody = document.getElementById("resultBody");
const flagFilter = document.getElementById("flagFilter");
const stats = document.getElementById("stats");

function normalizeLines(text) {
  return text.split(/\r?\n/).map(v => v.trim()).filter(Boolean).join("\n") + "\n";
}

function downloadText(filename, text) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function parseCsv(text) {
  const out = [];
  let row = [];
  let cell = "";
  let quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    const next = text[i + 1];
    if (quoted && ch === '"' && next === '"') {
      cell += '"';
      i++;
    } else if (ch === '"') {
      quoted = !quoted;
    } else if (ch === "," && !quoted) {
      row.push(cell);
      cell = "";
    } else if ((ch === "\n" || ch === "\r") && !quoted) {
      if (ch === "\r" && next === "\n") i++;
      row.push(cell);
      if (row.some(v => v !== "")) out.push(row);
      row = [];
      cell = "";
    } else {
      cell += ch;
    }
  }
  if (cell || row.length) {
    row.push(cell);
    out.push(row);
  }
  const headers = out.shift() || [];
  return out.map(values => Object.fromEntries(headers.map((h, i) => [h.replace(/^\uFEFF/, ""), values[i] || ""])));
}

function escapeHtml(value) {
  return String(value || "").replace(/[&<>"]/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
}

function badge(flag) {
  const cls = flag === "ok" ? "ok" : ["http_error", "fetch_failed", "noindex"].includes(flag) ? "bad" : "warn";
  return `<span class="badge ${cls}">${escapeHtml(flag)}</span>`;
}

function render() {
  const filter = flagFilter.value;
  const visible = filter ? rows.filter(row => (row.flags || "").split(";").includes(filter)) : rows;
  if (!visible.length) {
    resultBody.innerHTML = `<tr><td colspan="6" class="empty">未有符合資料</td></tr>`;
  } else {
    resultBody.innerHTML = visible.map(row => {
      const flags = (row.flags || "").split(";").filter(Boolean).map(badge).join("");
      return `<tr><td><a href="${escapeHtml(row.input_url)}" target="_blank" rel="noreferrer">${escapeHtml(row.input_url)}</a></td><td>${escapeHtml(row.status)}</td><td>${escapeHtml(row.title)}</td><td>${escapeHtml(row.text_length)}</td><td>${escapeHtml(row.meta_robots)}</td><td>${flags}</td></tr>`;
    }).join("");
  }
  const total = rows.length;
  const ok = rows.filter(row => row.flags === "ok").length;
  const suspect = rows.filter(row => row.flags && row.flags !== "ok").length;
  const failed = rows.filter(row => (row.flags || "").includes("fetch_failed") || (row.flags || "").includes("http_error")).length;
  stats.innerHTML = [
    ["Total", total],
    ["OK", ok],
    ["Need Review", suspect],
    ["Failed/Error", failed]
  ].map(([label, value]) => `<div class="card"><span>${label}</span><strong>${value}</strong></div>`).join("");
}

downloadSites.addEventListener("click", () => downloadText("sites.txt", normalizeLines(urlInput.value)));
copyCommand.addEventListener("click", async () => {
  await navigator.clipboard.writeText(document.getElementById("commandBox").textContent.trim());
  statusBox.textContent = "已複製指令";
});
csvFile.addEventListener("change", async event => {
  const file = event.target.files[0];
  if (!file) return;
  rows = parseCsv(await file.text());
  statusBox.textContent = `已載入 ${file.name}，共 ${rows.length} 筆`;
  render();
});
loadLatest.addEventListener("click", async () => {
  try {
    const response = await fetch("reports/latest.csv", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    rows = parseCsv(await response.text());
    statusBox.textContent = `已載入 latest.csv，共 ${rows.length} 筆`;
    render();
  } catch (error) {
    statusBox.textContent = `讀取失敗：${error.message}`;
  }
});
flagFilter.addEventListener("change", render);
render();
