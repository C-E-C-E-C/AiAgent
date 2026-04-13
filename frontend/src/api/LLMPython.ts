const PY_API_BASE = 'http://localhost:8000';

export async function getHealth() {
  const response = await fetch(`${PY_API_BASE}/api/health`);
  return response.json();
}

export async function planTrip(payload) {
  const response = await fetch(`${PY_API_BASE}/api/trips/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return response.json();
}

export async function chatStream(payload) {
  const response = await fetch(`${PY_API_BASE}/api/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return response;
}