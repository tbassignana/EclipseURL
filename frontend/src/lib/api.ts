const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface ApiOptions extends RequestInit {
  token?: string;
}

async function apiRequest<T>(
  endpoint: string,
  options: ApiOptions = {}
): Promise<T> {
  const { token, ...fetchOptions } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "An error occurred" }));
    throw new Error(error.detail || "An error occurred");
  }

  return response.json();
}

// Auth API
export const authApi = {
  register: (email: string, password: string) =>
    apiRequest<{ id: string; email: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  login: (email: string, password: string) =>
    apiRequest<{ access_token: string; token_type: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  me: (token: string) =>
    apiRequest<{ id: string; email: string; is_admin: boolean }>("/auth/me", {
      token,
    }),
};

// URL API
export const urlApi = {
  shorten: (
    originalUrl: string,
    options: { customAlias?: string; expirationDays?: number },
    token: string
  ) =>
    apiRequest<{
      id: string;
      short_code: string;
      short_url: string;
      original_url: string;
    }>("/urls/shorten", {
      method: "POST",
      body: JSON.stringify({
        original_url: originalUrl,
        custom_alias: options.customAlias,
        expiration_days: options.expirationDays,
      }),
      token,
    }),

  list: (token: string) =>
    apiRequest<
      Array<{
        id: string;
        short_code: string;
        short_url: string;
        original_url: string;
        clicks: number;
        created_at: string;
        expiration?: string;
      }>
    >("/urls", { token }),

  stats: (shortCode: string, token: string) =>
    apiRequest<{
      short_code: string;
      original_url: string;
      total_clicks: number;
      clicks_today: number;
      clicks_this_week: number;
      top_referrers: Array<{ referrer: string; count: number }>;
      clicks_by_country: Array<{ country: string; count: number }>;
      clicks_by_device: Array<{ device: string; count: number }>;
      clicks_over_time: Array<{ date: string; count: number }>;
    }>(`/urls/${shortCode}/stats`, { token }),

  delete: (shortCode: string, token: string) =>
    apiRequest<{ message: string }>(`/urls/${shortCode}`, {
      method: "DELETE",
      token,
    }),

  preview: (url: string) =>
    apiRequest<{
      title?: string;
      description?: string;
      image?: string;
      url: string;
    }>(`/urls/preview?url=${encodeURIComponent(url)}`),
};

// Admin API
export const adminApi = {
  stats: (token: string) =>
    apiRequest<{
      total_urls: number;
      total_clicks: number;
      total_users: number;
      urls_today: number;
      clicks_today: number;
      urls_this_week: number;
      clicks_this_week: number;
    }>("/admin/stats/summary", { token }),

  topUrls: (token: string, limit: number = 10) =>
    apiRequest<{
      urls: Array<{
        id: string;
        short_code: string;
        original_url: string;
        clicks: number;
        user_email: string;
      }>;
      count: number;
    }>(`/admin/top-urls?limit=${limit}`, { token }),

  deleteUrl: (shortCode: string, token: string) =>
    apiRequest<{ message: string }>(`/admin/urls/${shortCode}`, {
      method: "DELETE",
      token,
    }),
};
