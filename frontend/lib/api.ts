const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

interface APIResponse<T> {
  success: boolean;
  data: T | null;
  error?: { code: string; message: string };
}

interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

class APIClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("access_token");
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== "undefined") {
      localStorage.setItem("access_token", token);
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
  }

  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      // Try refresh
      const refreshed = await this.tryRefresh();
      if (refreshed) {
        headers["Authorization"] = `Bearer ${this.token}`;
        const retry = await fetch(`${this.baseUrl}${path}`, {
          ...options,
          headers,
        });
        if (!retry.ok) throw new APIError(retry.status, "Request failed after refresh");
        return retry.json();
      }
      this.clearToken();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      throw new APIError(401, "Session expired");
    }

    if (response.status === 204) {
      return {} as T;
    }

    const data = await response.json();

    if (!response.ok) {
      throw new APIError(
        response.status,
        data?.error?.message || "Request failed",
        data?.error?.code
      );
    }

    return data;
  }

  private async tryRefresh(): Promise<boolean> {
    if (typeof window === "undefined") return false;
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) return false;

    try {
      const res = await fetch(`${this.baseUrl}/api/v1/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      this.setToken(data.data.access_token);
      localStorage.setItem("refresh_token", data.data.refresh_token);
      return true;
    } catch {
      return false;
    }
  }

  // ── Auth ──
  async login(username: string, password: string) {
    const res = await this.request<APIResponse<any>>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    if (res.data) {
      this.setToken(res.data.access_token);
      if (typeof window !== "undefined") {
        localStorage.setItem("refresh_token", res.data.refresh_token);
      }
    }
    return res;
  }

  async register(email: string, username: string, password: string, fullName?: string) {
    return this.request<APIResponse<any>>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, username, password, full_name: fullName }),
    });
  }

  async getMe() {
    return this.request<APIResponse<any>>("/api/v1/auth/me");
  }

  // ── Cameras ──
  async getCameras() {
    return this.request<APIResponse<any[]>>("/api/v1/cameras/");
  }

  async createCamera(data: any) {
    return this.request<APIResponse<any>>("/api/v1/cameras/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async deleteCamera(id: string) {
    return this.request<void>(`/api/v1/cameras/${id}`, { method: "DELETE" });
  }

  // ── Detections ──
  async getDetections(params: Record<string, any> = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== "") {
        query.set(key, String(value));
      }
    });
    return this.request<PaginatedResponse<any>>(`/api/v1/detections/?${query}`);
  }

  async getDetection(id: string) {
    return this.request<APIResponse<any>>(`/api/v1/detections/${id}`);
  }

  async getRecentDetections(limit = 10) {
    return this.request<APIResponse<any[]>>(`/api/v1/detections/recent?limit=${limit}`);
  }

  // ── Analytics ──
  async getAnalyticsOverview() {
    return this.request<APIResponse<any>>("/api/v1/analytics/overview");
  }

  async getVehicleTypes(start?: string, end?: string) {
    const params = new URLSearchParams();
    if (start) params.set("start", start);
    if (end) params.set("end", end);
    return this.request<APIResponse<any[]>>(`/api/v1/analytics/vehicle-types?${params}`);
  }

  async getHourlyTraffic(date?: string) {
    const params = date ? `?date=${date}` : "";
    return this.request<APIResponse<any[]>>(`/api/v1/analytics/hourly-traffic${params}`);
  }

  async getCameraStats() {
    return this.request<APIResponse<any[]>>("/api/v1/analytics/camera-stats");
  }

  async getTopPlates(limit = 10) {
    return this.request<APIResponse<any[]>>(`/api/v1/analytics/top-plates?limit=${limit}`);
  }

  // ── Alerts ──
  async getAlertRules() {
    return this.request<APIResponse<any[]>>("/api/v1/alerts/rules");
  }

  async createAlertRule(data: any) {
    return this.request<APIResponse<any>>("/api/v1/alerts/rules", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getAlertEvents(status?: string) {
    const params = status ? `?status=${status}` : "";
    return this.request<APIResponse<any[]>>(`/api/v1/alerts/events${params}`);
  }

  async acknowledgeAlert(id: string) {
    return this.request<APIResponse<any>>(`/api/v1/alerts/events/${id}/acknowledge`, {
      method: "POST",
    });
  }

  // ── System ──
  async getSystemHealth() {
    return this.request<APIResponse<any>>("/api/v1/system/health");
  }

  async getDetailedHealth() {
    return this.request<APIResponse<any>>("/api/v1/system/health/detailed");
  }

  // ── AI ──
  async aiQuery(message: string) {
    return this.request<APIResponse<any>>("/api/v1/ai/query", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
  }
}

class APIError extends Error {
  status: number;
  code?: string;

  constructor(status: number, message: string, code?: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

export const api = new APIClient(API_BASE);
export const WS_URL = WS_BASE;
export type { APIResponse, PaginatedResponse, APIError };
