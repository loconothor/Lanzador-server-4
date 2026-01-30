let currentServer = null;

async function loadServers() {
    const servers = await window.pywebview.api.get_servers();

    document.getElementById("totalServers").textContent = servers.length;
    document.getElementById("onlineServers").textContent =
        servers.filter(s => s.status === "online").length;
    document.getElementById("offlineServers").textContent =
        servers.filter(s => s.status === "offline").length;

    const container = document.getElementById("servers");
    container.innerHTML = "";

    servers.forEach(s => {
        const card = document.createElement("div");
        card.className = `server-card ${s.status}`;

        card.innerHTML = `
            <h3>${s.name}</h3>
            <p>Estado: <strong>${s.status}</strong></p>

            <div class="server-actions">
                <button onclick="startServer('${s.id}')">▶ Iniciar</button>
                <button onclick="stopServer('${s.id}')">⏹ Detener</button>
                <button onclick="openConsole('${s.id}')">🖥 Consola</button>
            </div>
        `;

        container.appendChild(card);
    });
}

async function startServer(id) {
    await window.pywebview.api.start_server(id);
    loadServers();
}

async function stopServer(id) {
    await window.pywebview.api.stop_server(id);
    loadServers();
}

function openConsole(id) {
    currentServer = id;
    document.getElementById("console").textContent = "";
}

function classifyLog(line) {
    const upper = line.toUpperCase();

    if (upper.includes("ERROR") || upper.includes("SEVERE") || upper.includes("FATAL")) {
        return "error";
    }
    if (upper.includes("WARN")) {
        return "warn";
    }
    if (upper.includes("DONE") || upper.includes("STARTED")) {
        return "success";
    }
    if (upper.startsWith(">")) {
        return "command";
    }
    if (
        upper.includes("LOADING") ||
        upper.includes("STOPPING") ||
        upper.includes("SAVING")
    ) {
        return "system";
    }

    return "info";
}

function classifyLog(line) {
    const upper = line.toUpperCase();

    if (upper.includes("ERROR") || upper.includes("SEVERE") || upper.includes("FATAL")) {
        return "error";
    }
    if (upper.includes("WARN")) return "warn";
    if (upper.includes("DONE") || upper.includes("STARTED")) return "success";
    if (upper.startsWith(">")) return "command";
    if (upper.includes("LOADING") || upper.includes("STOPPING") || upper.includes("SAVING")) return "system";

    return "info";
}

async function updateConsole() {
    if (!currentServer) return;

    const logs = await window.pywebview.api.get_logs(currentServer);
    const consoleEl = document.getElementById("console");

    logs.forEach(line => {
        // Evitar duplicados
        if (consoleEl.textContent.includes(line)) return;

        const span = document.createElement("span");
        const type = classifyLog(line);

        span.className = `log ${type}`;
        span.textContent = line;

        consoleEl.appendChild(span);
    });

    filterLogs(); // Aplica filtros automáticamente
    consoleEl.scrollTop = consoleEl.scrollHeight; // Auto-scroll
}

// 🔘 FILTROS
function filterLogs() {
    const checkboxes = document.querySelectorAll(".log-filters input");
    const visibleTypes = Array.from(checkboxes).filter(cb => cb.checked).map(cb => cb.value);

    const logElements = document.querySelectorAll("#console .log");
    logElements.forEach(el => {
        el.style.display = visibleTypes.includes(el.classList[1]) ? "block" : "none";
    });
}

// 🧹 LIMPIAR CONSOLA
function clearConsole() {
    document.getElementById("console").innerHTML = "";
}

// 🔄 ACTUALIZACIÓN CONTINUA
setInterval(updateConsole, 300);
window.onload = loadServers;


function filterLogs() {
    const checkboxes = document.querySelectorAll(".log-filters input");
    const visibleTypes = Array.from(checkboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.value);

    const logElements = document.querySelectorAll("#console .log");

    logElements.forEach(el => {
        if (visibleTypes.includes(el.classList[1])) {
            el.style.display = "block";
        } else {
            el.style.display = "none";
        }
    });
}
