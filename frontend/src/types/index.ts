export interface User {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Stock {
  id: string;
  ticker: string;
  name: string;
  exchange: string;
  sector: string | null;
  industry: string | null;
  currency: string;
  country: string | null;
  market_cap: number | null;
  is_active: boolean;
  last_data_refresh: string | null;
}

export interface ValuationSnapshot {
  calculated_at: string;
  market_price: number | null;
  graham_number: number | null;
  graham_formula_value: number | null;
  ncav_per_share: number | null;
  dcf_value: number | null;
  pe_ratio: number | null;
  pb_ratio: number | null;
  current_ratio: number | null;
  debt_to_equity: number | null;
  dividend_yield: number | null;
  margin_of_safety_pct: number | null;
  earnings_stability: number | null;
  composite_score: number | null;
}

export interface StockDetail extends Stock {
  latest_valuation: ValuationSnapshot | null;
}

export interface PriceHistory {
  date: string;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  adj_close: number | null;
  volume: number | null;
}

export interface FinancialStatement {
  period_type: string;
  period_end: string;
  revenue: number | null;
  net_income: number | null;
  eps: number | null;
  book_value_per_share: number | null;
  total_assets: number | null;
  total_liabilities: number | null;
  current_assets: number | null;
  current_liabilities: number | null;
  total_debt: number | null;
  total_equity: number | null;
  dividends_per_share: number | null;
  free_cash_flow: number | null;
  operating_cash_flow: number | null;
}

export interface ScreeningProfile {
  id: string;
  name: string;
  description: string | null;
  exchanges: string[];
  sectors: string[];
  countries: string[];
  included_tickers: string[];
  excluded_tickers: string[];
  criteria: Record<string, unknown>;
  is_active: boolean;
  schedule: string | null;
  last_run_at: string | null;
  created_at: string;
}

export interface ScreeningResult {
  id: string;
  stock_id: string;
  stock_ticker: string | null;
  stock_name: string | null;
  run_at: string;
  passed_criteria: Record<string, unknown> | null;
  failed_criteria: Record<string, unknown> | null;
  composite_score: number | null;
  margin_of_safety_pct: number | null;
  recommendation: string | null;
}

export interface Portfolio {
  id: string;
  name: string;
  description: string | null;
  currency: string;
  created_at: string;
}

export interface Holding {
  id: string;
  portfolio_id: string;
  stock_id: string;
  stock_ticker: string | null;
  stock_name: string | null;
  shares: number;
  avg_cost_basis: number;
  first_purchased: string | null;
  notes: string | null;
  current_price: number | null;
  current_value: number | null;
  gain_loss: number | null;
  gain_loss_pct: number | null;
}

export interface Transaction {
  id: string;
  portfolio_id: string;
  stock_id: string;
  stock_ticker: string | null;
  type: "buy" | "sell" | "dividend";
  shares: number;
  price_per_share: number;
  fees: number;
  executed_at: string;
  notes: string | null;
}

export interface WatchlistItem {
  id: string;
  stock_id: string;
  stock_ticker: string | null;
  stock_name: string | null;
  target_price: number | null;
  target_mos_pct: number | null;
  current_price: number | null;
  current_mos_pct: number | null;
  notes: string | null;
  added_at: string;
}

export interface NewsArticle {
  id: string;
  stock_id: string | null;
  sector: string | null;
  title: string;
  url: string;
  source: string | null;
  published_at: string | null;
  summary: string | null;
  sentiment: "positive" | "neutral" | "negative" | null;
  sentiment_score: number | null;
  analysis: string | null;
}
