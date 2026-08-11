import { getToken, refreshAccessToken, logout } from "./auth";
import { BASE_PATH } from "./config";

const API_BASE = `${BASE_PATH}/api/v1`;

/**
 * Handle a definitive 401 (token invalid and refresh failed): clear stale
 * credentials and send the user to login instead of leaving them stuck on an
 * error screen. This commonly happens when the backend JWT secret changed
 * (e.g. after a redeploy) so previously issued tokens no longer validate.
 */
function handleAuthFailure(): void {
  if (typeof window === "undefined") return;
  logout();
  if (!window.location.pathname.startsWith(`${BASE_PATH}/login`)) {
    window.location.href = `${BASE_PATH}/login`;
  }
}

export interface ApiError {
  code: number;
  message: string;
  detail?: string;
}

export interface PatientCreate {
  name: string;
  gender?: string;
  dob?: string | Date;
  phone?: string;
  id_number?: string;
  address?: string;
  allergies?: string[];
  medical_history?: string[];
}

export interface PatientUpdate {
  name?: string;
  gender?: string;
  dob?: string | Date;
  phone?: string;
  id_number?: string;
  address?: string;
  allergies?: string[];
  medical_history?: string[];
}

export interface Patient {
  id: string;
  name: string;
  gender?: string;
  dob?: string;
  age?: number;
  phone?: string;
  allergies: string[];
  medical_history: string[];
  created_at: string;
  last_visit?: string;
  status: string;
}

export interface PatientListResponse {
  total: number;
  items: Patient[];
}

export interface MedicalRecord {
  id: string;
  patient_id: string;
  date: string;
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
  diagnosis: string;
  department: string;
  doctor: string;
}

export interface ConsultationHistoryResponse {
  session_id: string;
  records: MedicalRecord[];
  total: number;
}

export interface ConsultationHistoryItem {
  timestamp: string;
  agent: string;
  soap?: {
    subjective?: string;
    objective?: string;
    assessment?: string;
    plan?: string;
  };
  [key: string]: unknown;
}

export interface ConsultationStatus {
  session_id: string;
  patient_id: string;
  status: string;
  current_agent: string;
  history: ConsultationHistoryItem[];
}

export interface ConsultationStartResponse {
  session_id: string;
  patient_id: string;
  status: string;
  current_agent: string;
  created_at: string;
}

export interface HealthCheckResponse {
  status: string;
  mode: string;
  version: string;
}

function getAuthHeaders(): HeadersInit {
  const token = getToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  try {
    let response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        ...getAuthHeaders(),
        ...options.headers,
      },
    });

    // Auto-refresh on 401: try refreshing the token once, then retry.
    // If refresh also fails, the session is dead — clear it and redirect.
    if (response.status === 401) {
      const newToken = await refreshAccessToken();
      if (newToken) {
        response = await fetch(`${API_BASE}${path}`, {
          ...options,
          headers: {
            ...getAuthHeaders(),
            ...options.headers,
          },
        });
      } else {
        handleAuthFailure();
      }
    }

    if (!response.ok) {
      let errorBody: Partial<ApiError> = {};
      try {
        errorBody = await response.json();
      } catch {
        // ignore JSON parsing error
      }
      throw {
        code: response.status,
        message:
          (errorBody.detail as string | undefined) ||
          errorBody.message ||
          `HTTP error ${response.status}`,
        detail: errorBody.detail as string | undefined,
      } as ApiError;
    }

    const contentType = response.headers.get("content-type");
    if (contentType?.includes("application/json")) {
      return response.json() as Promise<T>;
    }
    return response.text() as unknown as Promise<T>;
  } catch (error) {
    if ("code" in (error as ApiError)) {
      throw error;
    }
    throw {
      code: 0,
      message: "网络错误",
      detail: error instanceof Error ? error.message : undefined,
    } as ApiError;
  }
}

export async function fetchApi(path: string, options?: RequestInit) {
  return request(path, options);
}

export async function getConsultation(sessionId: string): Promise<ConsultationStatus> {
  return request(`/consult/${sessionId}`);
}

export async function startConsultation(patientId?: string): Promise<ConsultationStartResponse> {
  return request("/consult", {
    method: "POST",
    body: JSON.stringify({ patient_id: patientId }),
  });
}

export async function listPatients(
  search?: string,
  page?: number,
  pageSize?: number
): Promise<PatientListResponse> {
  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (page) params.set("page", page.toString());
  if (pageSize) params.set("page_size", pageSize.toString());
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/patients${query}`);
}

export async function getPatient(patientId: string): Promise<Patient> {
  return request(`/patients/${patientId}`);
}

export async function createPatient(data: PatientCreate): Promise<Patient> {
  return request("/patients", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updatePatient(patientId: string, data: PatientUpdate): Promise<Patient> {
  return request(`/patients/${patientId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deletePatient(patientId: string): Promise<{ message: string }> {
  return request(`/patients/${patientId}`, {
    method: "DELETE",
  });
}

export async function listRecords(patientId: string): Promise<ConsultationHistoryResponse> {
  return request(`/records/patient/${patientId}`);
}

export async function getRecord(recordId: string): Promise<MedicalRecord> {
  return request(`/records/${recordId}`);
}

export async function createRecord(patientId: string, data: Partial<MedicalRecord>): Promise<MedicalRecord> {
  return request(`/records/patient/${patientId}`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function healthCheck(): Promise<HealthCheckResponse> {
  return request("/health");
}