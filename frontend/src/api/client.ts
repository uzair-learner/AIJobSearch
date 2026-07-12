const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api";

function buildApiErrorMessage(error: unknown): string {
  if (error instanceof TypeError) {
    return "Unable to reach the API. Check whether the backend server is running or whether the browser blocked the request.";
  }
  return error instanceof Error ? error.message : "Unexpected API error.";
}

export async function apiGet<T>(path: string): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`);
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }
    return response.json() as Promise<T>;
  } catch (error) {
    throw new Error(buildApiErrorMessage(error));
  }
}

export async function apiPost<T>(path: string, body: unknown, headers?: HeadersInit): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(headers ?? {}),
      },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
      const detail = payload?.detail;
      if (response.status === 400 && detail) throw new Error(detail);
      if (response.status === 404) throw new Error("API endpoint not found.");
      if (response.status >= 500) throw new Error(detail ?? "The backend encountered an internal error.");
      throw new Error(detail ?? `Request failed with status ${response.status}`);
    }
    return response.json() as Promise<T>;
  } catch (error) {
    throw new Error(buildApiErrorMessage(error));
  }
}

export async function apiPostForm<T>(path: string, formData: FormData, headers?: HeadersInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers,
    body: formData,
  });
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(payload?.detail ?? `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}
