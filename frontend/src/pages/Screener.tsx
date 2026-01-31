import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getProfiles,
  createProfile,
  runScreening,
  getLatestResults,
} from "@/api/screening";
import Card from "@/components/common/Card";
import Badge from "@/components/common/Badge";
import { Plus, Play } from "lucide-react";

export default function Screener() {
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newExchanges] = useState(["EURONEXT"]);

  const { data: profiles } = useQuery({
    queryKey: ["screening-profiles"],
    queryFn: getProfiles,
  });

  const { data: results } = useQuery({
    queryKey: ["screening-results-latest"],
    queryFn: () => getLatestResults(50),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createProfile({
        name: newName,
        exchanges: newExchanges,
        sectors: [],
        countries: [],
        included_tickers: [],
        excluded_tickers: [],
        criteria: {},
        is_active: true,
        schedule: "0 19 * * 1-5",
        description: null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["screening-profiles"] });
      setShowCreate(false);
      setNewName("");
    },
  });

  const runMutation = useMutation({
    mutationFn: runScreening,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["screening-results-latest"],
      });
      queryClient.invalidateQueries({ queryKey: ["screening-profiles"] });
    },
  });

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Screener</h1>
          <p className="mt-1 text-sm text-gray-500">
            Configure and run value investing screens
          </p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          <Plus className="h-4 w-4" />
          New Profile
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
                Profile Name
              </label>
              <input
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="e.g., Dutch Value Stocks"
                required
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              />
            </div>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
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

      {/* Profiles */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {profiles?.map((profile) => (
          <Card key={profile.id}>
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-gray-900">{profile.name}</h3>
                <p className="mt-1 text-xs text-gray-500">
                  {profile.exchanges?.join(", ")}
                  {profile.sectors?.length
                    ? ` | ${profile.sectors.join(", ")}`
                    : ""}
                </p>
              </div>
              <Badge variant={profile.is_active ? "green" : "gray"}>
                {profile.is_active ? "Active" : "Paused"}
              </Badge>
            </div>
            <div className="mt-4 flex items-center justify-between">
              <span className="text-xs text-gray-400">
                {profile.last_run_at
                  ? `Last run: ${new Date(profile.last_run_at).toLocaleDateString()}`
                  : "Never run"}
              </span>
              <button
                onClick={() => runMutation.mutate(profile.id)}
                disabled={runMutation.isPending}
                className="flex items-center gap-1 rounded-lg bg-brand-50 px-3 py-1.5 text-xs font-medium text-brand-700 hover:bg-brand-100 disabled:opacity-50"
              >
                <Play className="h-3 w-3" />
                Run
              </button>
            </div>
          </Card>
        ))}
      </div>

      {/* Results */}
      {results && results.length > 0 && (
        <Card title="Latest Results">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="pb-3 text-left font-medium text-gray-500">
                    Stock
                  </th>
                  <th className="pb-3 text-right font-medium text-gray-500">
                    Score
                  </th>
                  <th className="pb-3 text-right font-medium text-gray-500">
                    MoS
                  </th>
                  <th className="pb-3 text-right font-medium text-gray-500">
                    Signal
                  </th>
                  <th className="pb-3 text-right font-medium text-gray-500">
                    Passed
                  </th>
                  <th className="pb-3 text-right font-medium text-gray-500">
                    Failed
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {results.map((r) => (
                  <tr key={r.id} className="hover:bg-gray-50">
                    <td className="py-3">
                      <span className="font-medium">{r.stock_ticker}</span>
                      <span className="ml-2 text-gray-400">
                        {r.stock_name}
                      </span>
                    </td>
                    <td className="py-3 text-right font-mono">
                      {r.composite_score?.toFixed(1) ?? "-"}
                    </td>
                    <td className="py-3 text-right font-mono">
                      {r.margin_of_safety_pct != null
                        ? `${r.margin_of_safety_pct.toFixed(1)}%`
                        : "-"}
                    </td>
                    <td className="py-3 text-right">
                      {r.recommendation && (
                        <Badge
                          variant={
                            r.recommendation === "strong_buy" ||
                            r.recommendation === "buy"
                              ? "green"
                              : r.recommendation === "hold"
                                ? "yellow"
                                : "red"
                          }
                        >
                          {r.recommendation.replace("_", " ")}
                        </Badge>
                      )}
                    </td>
                    <td className="py-3 text-right text-green-600 font-mono">
                      {r.passed_criteria
                        ? Object.keys(r.passed_criteria).length
                        : 0}
                    </td>
                    <td className="py-3 text-right text-red-600 font-mono">
                      {r.failed_criteria
                        ? Object.keys(r.failed_criteria).length
                        : 0}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
