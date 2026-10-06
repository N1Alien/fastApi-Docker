const configuredApiUrl = import.meta.env.VITE_API_URL?.trim();
const defaultApiUrl = import.meta.env.DEV
  ? 'http://localhost:10000'
  : 'https://fastapi-docker-i29z.onrender.com';

export const API_BASE_URL = (configuredApiUrl || defaultApiUrl).replace(/\/+$/, '');

export function apiUrl(path) {
  return `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;
}
