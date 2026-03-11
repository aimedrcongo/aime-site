const API_BASE_URL = "https://api.aime-rdc.org";

const statusElement = document.getElementById("api-status");
const pingButton = document.getElementById("ping-api-btn");

async function pingApi() {
  if (!statusElement) return;
  statusElement.textContent = "Test de connexion en cours...";

  const targets = [
    `${API_BASE_URL}/`,
    `${API_BASE_URL}/admin/`,
  ];

  for (const target of targets) {
    try {
      const response = await fetch(target, { method: "GET", mode: "cors" });
      statusElement.textContent = `API joignable (${response.status}) via ${target}`;
      return;
    } catch (error) {
      // Continue to next endpoint if this one fails.
    }
  }

  statusElement.textContent = `Impossible de joindre ${API_BASE_URL}. Verifie DNS, CORS et SSL.`;
}

if (pingButton) {
  pingButton.addEventListener("click", pingApi);
}
