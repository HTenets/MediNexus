"use client";

import { useCallback, useEffect, useState } from "react";
import { createPatient, getMyProfile, type Patient } from "@/lib/api";

interface UsePatientProfileReturn {
  patient: Patient | null;
  loading: boolean;
  /** Set when the profile could not be resolved (network/auth failure). */
  error: string | null;
  reload: () => void;
}

/**
 * Resolve the patient profile belonging to the signed-in user.
 *
 * Pages used to hardcode `patient_demo_001`, which meant every user saw the
 * same seeded demo record and their own data was invisible. This hook reads
 * `GET /patients/me` instead, provisioning a profile on first visit so
 * downstream pages always operate on the caller's own record.
 */
export function usePatientProfile(fallbackName?: string): UsePatientProfileReturn {
  const [patient, setPatient] = useState<Patient | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [nonce, setNonce] = useState(0);

  const reload = useCallback(() => setNonce((n) => n + 1), []);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const profile = await getMyProfile();
        if (!cancelled) setPatient(profile);
      } catch (err) {
        const apiError = err as { code?: number; message?: string };
        // 404 simply means "no profile yet" — provision one from the account.
        if (apiError.code !== 404) {
          if (!cancelled) setError(apiError.message || "加载个人档案失败");
          return;
        }
        try {
          const created = await createPatient({ name: fallbackName || "本人" });
          if (!cancelled) setPatient(created);
        } catch (createErr) {
          if (!cancelled) {
            setError((createErr as { message?: string }).message || "创建个人档案失败");
          }
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [nonce, fallbackName]);

  return { patient, loading, error, reload };
}
