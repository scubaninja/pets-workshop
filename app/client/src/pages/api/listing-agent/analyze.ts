import type { APIRoute } from 'astro';
import { getApiServerUrl } from '../../../lib/api';

const API_SERVER_URL = getApiServerUrl();

export const POST: APIRoute = async ({ request }) => {
  console.log('[Astro API] /api/listing-agent/analyze called');
  console.log('[Astro API] API_SERVER_URL:', API_SERVER_URL);
  
  // Get the session cookie to forward auth
  const cookie = request.headers.get('cookie') || '';
  console.log('[Astro API] Cookie present:', !!cookie);
  
  // Get the form data (image + notes)
  const formData = await request.formData();
  console.log('[Astro API] FormData keys:', [...formData.keys()]);
  console.log('[Astro API] Notes value:', formData.get('notes'));
  
  // Forward to Flask backend
  console.log('[Astro API] Forwarding to Flask...');
  const response = await fetch(`${API_SERVER_URL}/api/listing-agent/analyze`, {
    method: 'POST',
    headers: cookie ? { cookie } : {},
    body: formData,
  });
  
  console.log('[Astro API] Flask response status:', response.status);

  const body = await response.text();
  console.log('[Astro API] Response body length:', body.length);
  
  const headers = new Headers({ 'content-type': 'application/json' });
  
  // Forward any cookies from Flask
  const setCookie = response.headers.get('set-cookie');
  if (setCookie) {
    headers.set('set-cookie', setCookie);
  }

  return new Response(body, { status: response.status, headers });
};
