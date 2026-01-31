import api from "./client";
import type { Holding, Portfolio, Transaction } from "@/types";

export async function getPortfolios(): Promise<Portfolio[]> {
  const { data } = await api.get("/portfolios");
  return data;
}

export async function createPortfolio(portfolio: {
  name: string;
  description?: string;
  currency?: string;
}): Promise<Portfolio> {
  const { data } = await api.post("/portfolios", portfolio);
  return data;
}

export async function getHoldings(portfolioId: string): Promise<Holding[]> {
  const { data } = await api.get(`/portfolios/${portfolioId}/holdings`);
  return data;
}

export async function createTransaction(
  portfolioId: string,
  transaction: Omit<Transaction, "id" | "portfolio_id" | "stock_ticker">,
): Promise<Transaction> {
  const { data } = await api.post(
    `/portfolios/${portfolioId}/transactions`,
    transaction,
  );
  return data;
}

export async function getTransactions(
  portfolioId: string,
): Promise<Transaction[]> {
  const { data } = await api.get(`/portfolios/${portfolioId}/transactions`);
  return data;
}
