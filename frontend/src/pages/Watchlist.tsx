import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getWatchlist, removeFromWatchlist } from "@/api/watchlist";
import Card from "@/components/common/Card";
import { Trash2 } from "lucide-react";
import { Link } from "react-router-dom";

export default function Watchlist() {
  const queryClient = useQueryClient();

  const { data: items } = useQuery({
    queryKey: ["watchlist"],
    queryFn: getWatchlist,
  });

  const removeMutation = useMutation({
    mutationFn: removeFromWatchlist,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["watchlist"] });
    },
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Watchlist</h1>
        <p className="mt-1 text-sm text-gray-500">
          Stocks you are monitoring for potential investment
        </p>
      </div>

      {items && items.length > 0 ? (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="pb-3 text-left font-medium text-gray-500">
                    Stock
                  </th>
                  <th className="pb-3 text-right font-medium text-gray-500">
                    Current Price
                  </th>
                  <th className="pb-3 text-right font-medium text-gray-500">
                    Target Price
                  </th>
                  <th className="pb-3 text-right font-medium text-gray-500">
                    Current MoS
                  </th>
                  <th className="pb-3 text-right font-medium text-gray-500">
                    Target MoS
                  </th>
                  <th className="pb-3 text-left font-medium text-gray-500">
                    Notes
                  </th>
                  <th className="pb-3 text-right font-medium text-gray-500">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {items.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="py-3">
                      <Link
                        to={`/stocks/${item.stock_id}`}
                        className="font-medium text-gray-900 hover:text-brand-600"
                      >
                        {item.stock_ticker}
                      </Link>
                      <span className="ml-2 text-gray-400">
                        {item.stock_name}
                      </span>
                    </td>
                    <td className="py-3 text-right font-mono">
                      {item.current_price?.toFixed(2) ?? "-"}
                    </td>
                    <td className="py-3 text-right font-mono">
                      {item.target_price?.toFixed(2) ?? "-"}
                    </td>
                    <td
                      className={`py-3 text-right font-mono ${
                        item.current_mos_pct != null && item.current_mos_pct > 0
                          ? "text-green-600"
                          : "text-red-600"
                      }`}
                    >
                      {item.current_mos_pct != null
                        ? `${item.current_mos_pct.toFixed(1)}%`
                        : "-"}
                    </td>
                    <td className="py-3 text-right font-mono">
                      {item.target_mos_pct != null
                        ? `${item.target_mos_pct.toFixed(1)}%`
                        : "-"}
                    </td>
                    <td className="py-3 text-gray-500 max-w-[200px] truncate">
                      {item.notes ?? "-"}
                    </td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => removeMutation.mutate(item.id)}
                        className="text-gray-400 hover:text-red-600"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : (
        <Card>
          <p className="text-sm text-gray-500">
            Your watchlist is empty. Add stocks from the screener or stock
            detail pages.
          </p>
        </Card>
      )}
    </div>
  );
}
