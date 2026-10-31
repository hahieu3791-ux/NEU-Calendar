// API Configuration
// python -m http.server (local) does not proxy /api, so always talk to FastAPI on port 8000.
// Docker also publishes backend on 8000, so this works for both local and docker-compose.
export const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000/api/v1`;
