const API = "";
let activeHash = "#Ogolny";

function $(id) {
  return document.getElementById(id);
}

function setHash(hash) {
  activeHash = hash;
  location.hash = hash.slice(1);
  document.querySelectorAll(".nav-link").forEach((el) => {
    el.classList.toggle("active", el.dataset.hash === hash);
  });
  document.querySelectorAll(".panel").forEach((el) => {
    el.classList.toggle("active", el.dataset.panel === hash);
  });
  $("active-hash-label").textContent = hash;
  loadPanelData(hash);
}

function appendMessage(text, role) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;
  $("chat-log").appendChild(div);
  $("chat-log").scrollTop = $("chat-log").scrollHeight;
}

async function api(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || res.statusText);
  }
  if (res.status === 204) return null;
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return res.json();
  return res.text();
}

async function sendChat(message) {
  appendMessage(message, "user");
  const data = await api("/workspace/chat", {
    method: "POST",
    body: JSON.stringify({ message, active_hash: activeHash }),
  });
  appendMessage(data.message, "agent");
  if (data.suggested_hash && data.suggested_hash !== activeHash) {
    appendMessage(`Sugestia: otwórz ${data.suggested_hash}`, "agent");
  }
}

async function loadBoard() {
  const tasks = await api("/workspace/board/tasks");
  const container = $("task-list");
  container.innerHTML = "";
  tasks.forEach((task) => {
    const card = document.createElement("article");
    card.className = "task-card";
    card.innerHTML = `
      <header>
        <strong>${task.title}</strong>
        <span class="badge">${task.team}</span>
      </header>
      <p class="muted">${task.intent || ""}</p>
      <select data-id="${task.id}">
        <option value="todo" ${task.status === "todo" ? "selected" : ""}>todo</option>
        <option value="doing" ${task.status === "doing" ? "selected" : ""}>doing</option>
        <option value="blocked" ${task.status === "blocked" ? "selected" : ""}>blocked</option>
        <option value="done" ${task.status === "done" ? "selected" : ""}>done</option>
      </select>`;
    card.querySelector("select").addEventListener("change", async (e) => {
      await api(`/workspace/board/tasks/${task.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: e.target.value }),
      });
    });
    container.appendChild(card);
  });
}

let planItemsCache = [];

async function loadPlanning() {
  const [calendar, items] = await Promise.all([
    api("/workspace/planning/calendar"),
    api("/workspace/planning/items"),
  ]);
  planItemsCache = items.map((i) => ({ title: i.title, source: i.source }));
  $("calendar-list").innerHTML = calendar.events.length
    ? `<p class="muted">Źródło kalendarza: <code>${calendar.source}</code></p>` +
      calendar.events
        .map(
          (e) =>
            `<div class="calendar-item"><time>${e.time}</time><span>${e.title}${
              e.calendar ? ` <span class="muted">(${e.calendar})</span>` : ""
            }</span></div>`
        )
        .join("")
    : `<p class="muted">Brak wydarzeń (źródło: ${calendar.source}).</p>`;
  renderPlanList();
}

function renderPlanList() {
  $("plan-list").innerHTML = planItemsCache.length
    ? planItemsCache
        .map(
          (item, idx) =>
            `<li><span class="muted">${item.source}</span><input data-idx="${idx}" value="${item.title.replace(/"/g, "&quot;")}"></li>`
        )
        .join("")
    : "<li class='muted'>Brak pozycji — wygeneruj plan lub zapytaj AO.</li>";
  $("plan-list").querySelectorAll("input").forEach((input) => {
    input.addEventListener("change", () => {
      const idx = Number(input.dataset.idx);
      planItemsCache[idx].title = input.value;
    });
  });
}

async function savePlanItems() {
  const today = new Date().toISOString().slice(0, 10);
  await api("/workspace/planning/items", {
    method: "PUT",
    body: JSON.stringify({
      plan_date: today,
      items: planItemsCache.map((i) => ({ title: i.title, source: i.source })),
    }),
  });
  await loadPlanning();
}

async function loadWiki(query) {
  const q = query || $("wiki-query").value || "backup";
  const data = await api(`/workspace/wiki/search?q=${encodeURIComponent(q)}`);
  $("wiki-results").innerHTML = data.results.length
    ? data.results
        .map(
          (r) =>
            `<li><strong>${r.source}</strong> <span class="muted">score ${r.score}</span><br>${r.excerpt}…</li>`
        )
        .join("")
    : "<li class='muted'>Brak wyników.</li>";
}

async def loadReview() {
  const pending = await api("/workspace/review/pending");
  $("review-list").innerHTML = pending.length
    ? pending
        .map(
          (p) => `<li>
        <strong>${p.description}</strong>
        <div class="muted">${p.actor_display_name} · ${p.risk_level} · ${p.action_type}</div>
        <div class="review-actions">
          <button class="btn-approve" data-id="${p.request_id}">Approve</button>
          <button class="btn-reject" data-id="${p.request_id}">Reject</button>
        </div>
      </li>`
        )
        .join("")
    : "<li class='muted'>Kolejka pusta.</li>";
  $("review-list").querySelectorAll(".btn-approve").forEach((btn) => {
    btn.addEventListener("click", async () => {
      await api(`/workspace/review/${btn.dataset.id}/approve`, { method: "POST" });
      await loadReview();
      await refreshReviewBadge();
    });
  });
  $("review-list").querySelectorAll(".btn-reject").forEach((btn) => {
    btn.addEventListener("click", async () => {
      await api(`/workspace/review/${btn.dataset.id}/reject`, { method: "POST" });
      await loadReview();
      await refreshReviewBadge();
    });
  });
  await refreshReviewBadge(pending.length);
}

async function refreshReviewBadge(count) {
  let pendingCount = count;
  if (pendingCount === undefined) {
    try {
      const pending = await api("/workspace/review/pending");
      pendingCount = pending.length;
    } catch {
      return;
    }
  }
  const badge = $("review-badge");
  if (!badge) return;
  if (pendingCount > 0) {
    badge.textContent = String(pendingCount);
    badge.hidden = false;
  } else {
    badge.hidden = true;
  }
}

async function loadRetro() {
  const data = await api("/workspace/retro/today");
  $("retro-preview").textContent = data.content || "(brak wpisu na dziś)";
}

function loadPanelData(hash) {
  if (hash === "#Board") loadBoard();
  if (hash === "#Planning") loadPlanning();
  if (hash === "#Wiki") loadWiki();
  if (hash === "#Review") loadReview();
  if (hash === "#Retro") loadRetro();
}

document.querySelectorAll(".nav-link").forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    setHash(link.dataset.hash);
  });
});

$("chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = $("chat-input");
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  try {
    await sendChat(text);
  } catch (err) {
    appendMessage(`Błąd: ${err.message}`, "agent");
  }
});

$("wiki-form").addEventListener("submit", (e) => {
  e.preventDefault();
  loadWiki($("wiki-query").value);
});

$("retro-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  await api("/workspace/retro", {
    method: "POST",
    body: JSON.stringify({
      went_well: fd.get("went_well"),
      improve: fd.get("improve"),
      tomorrow: fd.get("tomorrow"),
    }),
  });
  loadRetro();
});

$("add-task-btn").addEventListener("click", async () => {
  const title = $("new-title").value.trim();
  if (!title) return;
  await api("/workspace/board/tasks", {
    method: "POST",
    body: JSON.stringify({ team: $("new-team").value, title }),
  });
  $("new-title").value = "";
  loadBoard();
});

$("generate-plan-btn").addEventListener("click", async () => {
  await api("/workspace/planning/generate", { method: "POST" });
  await loadPlanning();
});

$("save-plan-btn").addEventListener("click", () => savePlanItems());

$("add-plan-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = $("new-plan-item").value.trim();
  if (!title) return;
  planItemsCache.push({ title, source: "ceo" });
  $("new-plan-item").value = "";
  renderPlanList();
});

window.addEventListener("hashchange", () => {
  const hash = location.hash ? `#${location.hash.slice(1)}` : "#Ogolny";
  setHash(hash);
});

(async function init() {
  const hash = location.hash ? `#${location.hash.slice(1)}` : "#Ogolny";
  setHash(hash);
  appendMessage("Dzień dobry! Jestem Agentem Osobistym. Zapytaj o plan, backup albo tablicę.", "agent");
  try {
    const health = await api("/workspace/health");
    appendMessage(`Indeks Knowledge: ${health.documents_indexed} dokumentów.`, "agent");
    if (health.review_pending_count > 0) {
      appendMessage(
        `W kolejce #Review czeka ${health.review_pending_count} akcji do zatwierdzenia — zapytaj „co wymaga uwagi?”.`,
        "agent"
      );
    }
    await refreshReviewBadge(health.review_pending_count);
  } catch {
    appendMessage("Workspace API niedostępne — uruchom scripts/octa-mvp-up.sh", "agent");
  }
})();
