import api from "./client";
import type { ScreeningProfile, ScreeningResult } from "@/types";

export async function getProfiles(): Promise<ScreeningProfile[]> {
  const { data } = await api.get("/screening/profiles");
  return data;
}

export async function createProfile(
  profile: Omit<ScreeningProfile, "id" | "last_run_at" | "created_at">,
): Promise<ScreeningProfile> {
  const { data } = await api.post("/screening/profiles", profile);
  return data;
}

export async function updateProfile(
  profileId: string,
  updates: Partial<ScreeningProfile>,
): Promise<ScreeningProfile> {
  const { data } = await api.put(`/screening/profiles/${profileId}`, updates);
  return data;
}

export async function deleteProfile(profileId: string): Promise<void> {
  await api.delete(`/screening/profiles/${profileId}`);
}

export async function runScreening(
  profileId: string,
): Promise<ScreeningResult[]> {
  const { data } = await api.post(`/screening/profiles/${profileId}/run`);
  return data;
}

export async function getLatestResults(
  limit = 50,
): Promise<ScreeningResult[]> {
  const { data } = await api.get("/screening/results/latest", {
    params: { limit },
  });
  return data;
}
