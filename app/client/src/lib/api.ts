export function getApiServerUrl() {
  return (process.env.API_SERVER_URL || 'http://localhost:5100').trim().replace(/\/+$/, '');
}
