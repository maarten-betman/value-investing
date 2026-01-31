import api from "./client";
import type { WatchlistItem } from "@/types";

export async function getWatchlist(): Promise<WatchlistItem[]> {
  const { data } = await api.get("/watchlist");
  return data;
}

export async function addToWatchlist(item: {
  stock_id: string;
  target_price?: number;
  target_mos_pct?: number;
  notes?: string;
}): Promise<WatchlistItem> {
  const { data } = await api.post("/watchlist", item);
  return data;
}

export async function updateWatchlistItem(
  itemId: string,
  updates: Partial<WatchlistItem>,
): Promise<WatchlistItem> {
  const { data } = await api.put(`/watchlist/${itemId}`, updates);
  return data;
}

export async function removeFromWatchlist(itemId: string): Promise<void> {
  await api.delete(`/watchlist/${itemId}`);
}
