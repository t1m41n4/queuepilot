const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const TOKEN_KEY = "queuepilot_access_token";

export function saveAccessToken(token: string) {
  if (typeof window !== "undefined") window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearAccessToken() {
  if (typeof window !== "undefined") window.localStorage.removeItem(TOKEN_KEY);
}

export function hasAccessToken() {
  return typeof window !== "undefined" && Boolean(window.localStorage.getItem(TOKEN_KEY));
}

function accessToken() {
  return typeof window === "undefined" ? undefined : window.localStorage.getItem(TOKEN_KEY) ?? undefined;
}

export function userFacingError(reason: unknown): string {
  if (!(reason instanceof ApiError)) return "Something went wrong. Please try again.";
  if (reason.status === 401) {
    clearAccessToken();
    return "Your session has expired. Please sign in again.";
  }
  if (reason.status === 404) return "The requested queue or branch is unavailable.";
  if (reason.status === 409) {
    if (reason.message.toLowerCase().includes("queue is not open")) {
      return "This branch queue is currently paused. Please choose another branch.";
    }
    return "This queue operation is not available right now.";
  }
  if (reason.status === 501) return "This feature is not available yet.";
  if (reason.status >= 500) return "The service is temporarily unavailable. Please try again.";
  return reason.message;
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const token = accessToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {}),
    },
  });

  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = typeof body?.detail === "string" ? body.detail : "The request could not be completed.";
    throw new ApiError(detail, response.status);
  }
  return body as T;
}

export function get<T>(path: string) {
  return apiRequest<T>(path);
}

export function post<T>(path: string, body: unknown) {
  return apiRequest<T>(path, { method: "POST", body: JSON.stringify(body) });
}

export function websocketUrl(path: string): string {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!configured || configured.startsWith("/")) {
    return `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}${path}`;
  }
  const url = new URL(configured);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  return `${url.protocol}//${url.host}${path}`;
}
