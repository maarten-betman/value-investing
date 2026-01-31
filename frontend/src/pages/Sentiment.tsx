import Card from "@/components/common/Card";

export default function Sentiment() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Sentiment</h1>
        <p className="mt-1 text-sm text-gray-500">
          LLM-powered news analysis and sector sentiment
        </p>
      </div>

      <Card>
        <div className="py-12 text-center">
          <p className="text-gray-500">
            Sentiment analysis will be available after configuring an LLM
            provider in Settings.
          </p>
          <p className="mt-2 text-sm text-gray-400">
            This feature scans sector news and provides automated sentiment
            scoring using AI.
          </p>
        </div>
      </Card>
    </div>
  );
}
