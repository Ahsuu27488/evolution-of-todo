/**
 * Dapr Client for Chronos Todo Frontend (Phase V)
 *
 * Provides Dapr service invocation for the frontend to call backend services.
 * This enables service discovery, retries, and mTLS without direct dependencies.
 *
 * Usage:
 *   import { daprInvoke } from '@/lib/dapr/client';
 *
 *   const tasks = await daprInvoke('chronos-backend', 'GET', '/api/tasks');
 */

// Dapr sidecar URL (default port for local development)
const DAPR_HTTP_PORT = Number(process.env.NEXT_PUBLIC_DAPR_HTTP_PORT) || 3500;
const DAPR_BASE_URL = `http://localhost:${DAPR_HTTP_PORT}/v1.0`;

// Check if Dapr is enabled
export const isDaprEnabled = (): boolean => {
  return process.env.NEXT_PUBLIC_DAPR_ENABLED === 'true';
};

/**
 * Invoke a backend service method via Dapr service invocation
 *
 * @param appId - Dapr app ID of the target service (e.g., "chronos-backend")
 * @param method - Method name to invoke (e.g., "GET" or the actual method name)
 * @param data - Request body data
 * @param httpVerb - HTTP verb (GET, POST, PUT, DELETE)
 * @returns Response data or throws error
 */
export async function daprInvoke<T = unknown>(
  appId: string,
  method: string,
  data?: unknown,
  httpVerb: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'POST'
): Promise<T> {
  if (!isDaprEnabled()) {
    throw new Error('Dapr is not enabled. Set NEXT_PUBLIC_DAPR_ENABLED=true');
  }

  const url = `${DAPR_BASE_URL}/invoke/${appId}/method/${method}`;

  const options: RequestInit = {
    method: httpVerb,
    headers: {
      'Content-Type': 'application/json',
    },
  };

  // Add body for POST/PUT requests
  if (data && (httpVerb === 'POST' || httpVerb === 'PUT')) {
    options.body = JSON.stringify(data);
  }

  // Add query params for GET requests
  let fullUrl = url;
  if (data && httpVerb === 'GET') {
    const params = new URLSearchParams(data as Record<string, string>);
    const queryString = params.toString();
    if (queryString) {
      fullUrl = `${url}?${queryString}`;
    }
  }

  try {
    const response = await fetch(fullUrl, options);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: response.statusText }));
      throw new Error(`Dapr invocation failed: ${error.message || response.statusText}`);
    }

    return response.json();
  } catch (error) {
    console.error('Dapr service invocation error:', error);
    throw error;
  }
}

/**
 * Wrapper for calling backend API via Dapr
 *
 * This provides the same interface as the existing API client but uses Dapr for transport.
 *
 * @param endpoint - API endpoint (e.g., "/api/tasks")
 * @param options - Fetch options
 * @returns Response data
 */
export async function daprApiCall<T = unknown>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  if (!isDaprEnabled()) {
    throw new Error('Dapr is not enabled');
  }

  // Extract method and body from options
  const method = (options.method || 'POST') as 'GET' | 'POST' | 'PUT' | 'DELETE';
  const body = options.body ? JSON.parse(options.body as string) : undefined;

  // Call backend via Dapr
  return daprInvoke<T>('chronos-backend', endpoint, body, method);
}

/**
 * Publish an event to Dapr Pub/Sub
 *
 * @param topic - Topic name (e.g., "task-events")
 * @param data - Event payload
 * @returns true if published successfully
 */
export async function daprPublishEvent(
  topic: string,
  data: Record<string, unknown>
): Promise<boolean> {
  if (!isDaprEnabled()) {
    return false;
  }

  const url = `${DAPR_BASE_URL}/publish/kafka-pubsub/${topic}`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      console.error('Failed to publish event:', await response.text());
      return false;
    }

    return true;
  } catch (error) {
    console.error('Dapr event publishing error:', error);
    return false;
  }
}

/**
 * Get state from Dapr state store
 *
 * @param key - State key
 * @returns State value or null
 */
export async function daprGetState<T = unknown>(key: string): Promise<T | null> {
  if (!isDaprEnabled()) {
    return null;
  }

  const url = `${DAPR_BASE_URL}/state/statestore/${key}`;

  try {
    const response = await fetch(url);

    if (response.status === 404) {
      return null;
    }

    if (!response.ok) {
      console.error('Failed to get state:', await response.text());
      return null;
    }

    return response.json();
  } catch (error) {
    console.error('Dapr state get error:', error);
    return null;
  }
}

/**
 * Save state to Dapr state store
 *
 * @param key - State key
 * @param value - State value
 * @returns true if saved successfully
 */
export async function daprSaveState(
  key: string,
  value: Record<string, unknown>
): Promise<boolean> {
  if (!isDaprEnabled()) {
    return false;
  }

  const url = `${DAPR_BASE_URL}/state/statestore`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify([
        {
          key,
          value,
        },
      ]),
    });

    if (!response.ok) {
      console.error('Failed to save state:', await response.text());
      return false;
    }

    return true;
  } catch (error) {
    console.error('Dapr state save error:', error);
    return false;
  }
}

/**
 * Dapr service types
 */
export interface DaprService {
  invoke: typeof daprInvoke;
  publishEvent: typeof daprPublishEvent;
  getState: typeof daprGetState;
  saveState: typeof daprSaveState;
}

/**
 * Dapr client instance (singleton)
 */
export const daprClient: DaprService = {
  invoke: daprInvoke,
  publishEvent: daprPublishEvent,
  getState: daprGetState,
  saveState: daprSaveState,
};

export default daprClient;
