import { useQuery } from "@tanstack/react-query";
import { getLatestResults } from "@/api/screening";
import { getWatchlist } from "@/api/watchlist";
import Card from "@/components/common/Card";
import Badge from "@/components/common/Badge";
import { Link } from "react-router-dom";

const recommendationColors = {
  strong_buy: "green" as const,
  buy: "blue" as const,
  hold: "yellow" as const,
  avoid: "red" as const,
};

export default function Dashboard() {
  const { data: screeningResults } = useQuery({
    queryKey: ["screening-results-latest"],
    queryFn: () => getLatestResults(10),
  });

  const { data: watchlistItems } = useQuery({
    queryKey: ["watchlist"],
    queryFn: getWatchlist,
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Your value investing overview
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Top Opportunities */}
        <Card title="Top Opportunities" className="lg:col-span-2">
          {screeningResults && screeningResults.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100">
                    <th className="pb-3 text-left font-medium text-gray-500">
                      Stock
                    </th>
                    <th className="pb-3 text-right font-medium text-gray-500">
                      Composite Score
                    </th>
                    <th className="pb-3 text-right font-medium text-gray-500">
                      Margin of Safety
                    </th>
                    <th className="pb-3 text-right font-medium text-gray-500">
                      Recommendation
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {screeningResults.map((result) => (
                    <tr key={result.id} className="hover:bg-gray-50">
                      <td className="py-3">
                        <Link
                          to={`/stocks/${result.stock_id}`}
                          className="font-medium text-gray-900 hover:text-brand-600"
                        >
                          {result.stock_ticker}
                        </Link>
                        <span className="ml-2 text-gray-500">
                          {result.stock_name}
                        </span>
                      </td>
                      <td className="py-3 text-right font-mono">
                        {result.composite_score?.toFixed(1) ?? "-"}
                      </td>
                      <td className="py-3 text-right font-mono">
                        {result.margin_of_safety_pct != null
                          ? `${result.margin_of_safety_pct.toFixed(1)}%`
                          : "-"}
                      </td>
                      <td className="py-3 text-right">
                        {result.recommendation && (
                          <Badge
                            variant={
                              recommendationColors[
                                result.recommendation as keyof typeof recommendationColors
                              ] ?? "gray"
                            }
                          >
                            {result.recommendation.replace("_", " ")}
                          </Badge>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-gray-500">
              No screening results yet. Create a screening profile and run it to
              see opportunities.
            </p>
          )}
        </Card>

        {/* Watchlist Alerts */}
        <Card title="Watchlist">
          {watchlistItems && watchlistItems.length > 0 ? (
            <ul className="space-y-3">
              {watchlistItems.slice(0, 8).map((item) => (
                <li
                  key={item.id}
                  className="flex items-center justify-between"
                >
                  <div>
                    <Link
                      to={`/stocks/${item.stock_id}`}
                      className="font-medium text-gray-900 hover:text-brand-600"
                    >
                      {item.stock_ticker}
                    </Link>
                    <span className="ml-2 text-xs text-gray-500">
                      {item.stock_name}
                    </span>
                  </div>
                  <div className="text-right">
                    {item.current_price != null && (
                      <span className="font-mono text-sm">
                        {item.current_price.toFixed(2)}
                      </span>
                    )}
                    {item.current_mos_pct != null && (
                      <span
                        className={`ml-2 text-xs font-medium ${
                          item.current_mos_pct > 0
                            ? "text-green-600"
                            : "text-red-600"
                        }`}
                      >
                        {item.current_mos_pct > 0 ? "+" : ""}
                        {item.current_mos_pct.toFixed(1)}% MoS
                      </span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">
              No items in your watchlist yet.
            </p>
          )}
        </Card>

        {/* Quick Stats */}
        <Card title="Quick Stats">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {screeningResults?.length ?? 0}
              </p>
              <p className="text-xs text-gray-500">Screening Results</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {watchlistItems?.length ?? 0}
              </p>
              <p className="text-xs text-gray-500">Watchlist Items</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">
                {screeningResults?.filter(
                  (r) =>
                    r.recommendation === "strong_buy" ||
                    r.recommendation === "buy",
                ).length ?? 0}
              </p>
              <p className="text-xs text-gray-500">Buy Signals</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-brand-600">
                {screeningResults
                  ?.reduce(
                    (max, r) =>
                      r.composite_score && r.composite_score > max
                        ? r.composite_score
                        : max,
                    0,
                  )
                  ?.toFixed(1) ?? "-"}
              </p>
              <p className="text-xs text-gray-500">Top Score</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
