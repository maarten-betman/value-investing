import api from "./client";
import type {
  FinancialStatement,
  PriceHistory,
  Stock,
  StockDetail,
  ValuationSnapshot,
} from "@/types";

export async function getStocks(params?: {
  exchange?: string;
  sector?: string;
  country?: string;
  page?: number;
  per_page?: number;
}): Promise<Stock[]> {
  const { data } = await api.get("/stocks", { params });
  return data;
}

export async function searchStocks(q: string): Promise<Stock[]> {
  const { data } = await api.get("/stocks/search", { params: { q } });
  return data;
}

export async function getStock(stockId: string): Promise<StockDetail> {
  const { data } = await api.get(`/stocks/${stockId}`);
  return data;
}

export async function getStockFinancials(
  stockId: string,
  periodType = "annual",
): Promise<FinancialStatement[]> {
  const { data } = await api.get(`/stocks/${stockId}/financials`, {
    params: { period_type: periodType },
  });
  return data;
}

export async function getStockPrices(
  stockId: string,
  limit = 365,
): Promise<PriceHistory[]> {
  const { data } = await api.get(`/stocks/${stockId}/prices`, {
    params: { limit },
  });
  return data;
}

export async function getStockValuations(
  stockId: string,
  limit = 100,
): Promise<ValuationSnapshot[]> {
  const { data } = await api.get(`/stocks/${stockId}/valuations`, {
    params: { limit },
  });
  return data;
}
