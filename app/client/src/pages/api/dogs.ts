import type { APIRoute } from 'astro';
import { getApiServerUrl } from '../../lib/api';

const API_SERVER_URL = getApiServerUrl();

export const POST: APIRoute = async ({ request }) => {
  // Get the session cookie to forward auth
  const cookie = request.headers.get('cookie') || '';
  
  // Forward JSON body to Flask
  const response = await fetch(`${API_SERVER_URL}/api/dogs`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      ...(cookie ? { cookie } : {}),
    },
    body: await request.text(),
  });

  const body = await response.text();
  const headers = new Headers({ 'content-type': 'application/json' });
  
  // Forward any cookies from Flask
  const setCookie = response.headers.get('set-cookie');
  if (setCookie) {
    headers.set('set-cookie', setCookie);
  }

  return new Response(body, { status: response.status, headers });
};
