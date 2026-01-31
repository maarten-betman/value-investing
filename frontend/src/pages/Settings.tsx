import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import Card from "@/components/common/Card";

interface SchedulerJob {
  id: string;
  name: string;
  next_run_time: string | null;
  trigger: string;
}

export default function Settings() {
  const { data: jobs } = useQuery<SchedulerJob[]>({
    queryKey: ["scheduler-jobs"],
    queryFn: async () => {
      const { data } = await axios.get("/api/scheduler/jobs");
      return data;
    },
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-500">
          Configure data sources, LLM, and scheduler
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card title="Data Provider">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                FMP API Key
              </label>
              <input
                type="password"
                placeholder="Configured via environment variable"
                disabled
                className="mt-1 block w-full rounded-lg border border-gray-300 bg-gray-50 px-3 py-2 text-sm"
              />
              <p className="mt-1 text-xs text-gray-400">
                Set FMP_API_KEY in your .env file
              </p>
            </div>
          </div>
        </Card>

        <Card title="LLM Provider">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Provider
              </label>
              <input
                type="text"
                placeholder="Configured via environment variable"
                disabled
                className="mt-1 block w-full rounded-lg border border-gray-300 bg-gray-50 px-3 py-2 text-sm"
              />
              <p className="mt-1 text-xs text-gray-400">
                Set LLM_PROVIDER and LLM_API_KEY in your .env file
              </p>
            </div>
          </div>
        </Card>

        <Card title="Scheduled Jobs" className="lg:col-span-2">
          {jobs && jobs.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100">
                    <th className="pb-3 text-left font-medium text-gray-500">
                      Job
                    </th>
                    <th className="pb-3 text-left font-medium text-gray-500">
                      Schedule
                    </th>
                    <th className="pb-3 text-left font-medium text-gray-500">
                      Next Run
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {jobs.map((job) => (
                    <tr key={job.id} className="hover:bg-gray-50">
                      <td className="py-3 font-medium">{job.name}</td>
                      <td className="py-3 font-mono text-gray-500">
                        {job.trigger}
                      </td>
                      <td className="py-3 text-gray-500">
                        {job.next_run_time
                          ? new Date(job.next_run_time).toLocaleString()
                          : "Not scheduled"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-gray-500">Loading scheduler jobs...</p>
          )}
        </Card>
      </div>
    </div>
  );
}
