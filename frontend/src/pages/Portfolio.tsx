import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getPortfolios, createPortfolio, getHoldings } from "@/api/portfolio";
import Card from "@/components/common/Card";
import { Plus } from "lucide-react";

export default function Portfolio() {
  const queryClient = useQueryClient();
  const [selectedPortfolio, setSelectedPortfolio] = useState<string | null>(
    null,
  );
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");

  const { data: portfolios } = useQuery({
    queryKey: ["portfolios"],
    queryFn: getPortfolios,
  });

  const activePortfolioId = selectedPortfolio ?? portfolios?.[0]?.id;

  const { data: holdings } = useQuery({
    queryKey: ["holdings", activePortfolioId],
    queryFn: () => getHoldings(activePortfolioId!),
    enabled: !!activePortfolioId,
  });

  const createMutation = useMutation({
    mutationFn: () => createPortfolio({ name: newName, currency: "EUR" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolios"] });
      setShowCreate(false);
      setNewName("");
    },
  });

  const totalValue =
    holdings?.reduce((sum, h) => sum + (h.current_value ?? 0), 0) ?? 0;
  const totalGainLoss =
    holdings?.reduce((sum, h) => sum + (h.gain_loss ?? 0), 0) ?? 0;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Portfolio</h1>
          <p className="mt-1 text-sm text-gray-500">
            Track your holdings and performance
          </p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          <Plus className="h-4 w-4" />
          New Portfolio
        </button>
      </div>

      {showCreate && (
        <Card>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              createMutation.mutate();
            }}
            className="flex items-end gap-4"
          >
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700">
                Portfolio Name
              </label>
              <input
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="e.g., De Giro - Value Portfolio"
                required
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              />
            </div>
            <button
              type="submit"
              className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
            >
              Create
            </button>
            <button
              type="button"
              onClick={() => setShowCreate(false)}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
          </form>
        </Card>
      )}

      {/* Portfolio Tabs */}
      {portfolios && portfolios.length > 0 && (
        <div className="flex gap-2 border-b border-gray-200">
          {portfolios.map((p) => (
            <button
              key={p.id}
              onClick={() => setSelectedPortfolio(p.id)}
              className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
                activePortfolioId === p.id
                  ? "border-brand-600 text-brand-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {p.name}
            </button>
          ))}
        </div>
      )}

      {/* Summary Cards */}
      {holdings && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <Card>
            <p className="text-sm text-gray-500">Total Value</p>
            <p className="text-2xl font-bold text-gray-900">
              {totalValue.toLocaleString("nl-NL", {
                style: "currency",
                currency: "EUR",
              })}
            </p>
          </Card>
          <Card>
            <p className="text-sm text-gray-500">Total Gain/Loss</p>
            <p
              className={`text-2xl font-bold ${totalGainLoss >= 0 ? "text-green-600" : "text-red-600"}`}
            >
              {totalGainLoss >= 0 ? "+" : ""}
              {totalGainLoss.toLocaleString("nl-NL", {
                style: "currency",
                currency: "EUR",
              })}
            </p>
          </Card>
          <Card>
            <p className="text-sm text-gray-500">Positions</p>
            <p className="text-2xl font-bold text-gray-900">
              {holdings.length}
            </p>
          </Card>
        </div>
      )}

      {/* Holdings Table */}
      {holdings && holdings.length > 0 && (
        <Card title="Holdings">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="pb-3 text-left font-medium text-gray-500">
                    Stock
                  </th>
                  <th className="pb-3 text-right font-medium text-gray-500">
                    Shares
                  </th>
                  <th className="pb-3 text-right font-medium text-gray-500">
                    Avg Cost
                  </th>
                  <th className="pb-3 text-right font-medium text-gray-500">
                    Current
                  </th>
                  <th className="pb-3 text-right font-medium text-gray-500">
                    Value
                  </th>
                  <th className="pb-3 text-right font-medium text-gray-500">
                    P&L
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {holdings.map((h) => (
                  <tr key={h.id} className="hover:bg-gray-50">
                    <td className="py-3">
                      <span className="font-medium">{h.stock_ticker}</span>
                      <span className="ml-2 text-gray-400">
                        {h.stock_name}
                      </span>
                    </td>
                    <td className="py-3 text-right font-mono">{h.shares}</td>
                    <td className="py-3 text-right font-mono">
                      {h.avg_cost_basis.toFixed(2)}
                    </td>
                    <td className="py-3 text-right font-mono">
                      {h.current_price?.toFixed(2) ?? "-"}
                    </td>
                    <td className="py-3 text-right font-mono">
                      {h.current_value?.toFixed(2) ?? "-"}
                    </td>
                    <td
                      className={`py-3 text-right font-mono ${
                        h.gain_loss_pct != null && h.gain_loss_pct >= 0
                          ? "text-green-600"
                          : "text-red-600"
                      }`}
                    >
                      {h.gain_loss_pct != null
                        ? `${h.gain_loss_pct >= 0 ? "+" : ""}${h.gain_loss_pct.toFixed(1)}%`
                        : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {(!holdings || holdings.length === 0) && activePortfolioId && (
        <Card>
          <p className="text-sm text-gray-500">
            No holdings yet. Add transactions to track your investments.
          </p>
        </Card>
      )}
    </div>
  );
}
