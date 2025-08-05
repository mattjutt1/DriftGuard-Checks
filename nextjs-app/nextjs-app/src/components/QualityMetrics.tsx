"use client";

interface QualityMetricsProps {
  healthResult: unknown;
}

export default function QualityMetrics({ healthResult }: QualityMetricsProps) {
  if (!healthResult) return null;
  
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const result = healthResult as any;

  return (
    <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold mb-4 flex items-center">
        <span className="mr-2">System Health Status</span>
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium ${
            result.healthy
              ? "bg-green-100 text-green-800"
              : "bg-red-100 text-red-800"
          }`}
        >
          {result.healthy ? "Healthy" : "Issues Detected"}
        </span>
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="font-semibold text-gray-800 mb-2">
            Service Status
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Running:</span>
              <span
                className={
                  result.service?.running
                    ? "text-green-600"
                    : "text-red-600"
                }
              >
                {result.service?.running ? "✅ Yes" : "❌ No"}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Response Time:</span>
              <span
                className={
                  result.service?.responseTime > 2000
                    ? "text-yellow-600"
                    : "text-green-600"
                }
              >
                {result.service?.responseTime}ms
              </span>
            </div>
          </div>
        </div>

        <div>
          <h3 className="font-semibold text-gray-800 mb-2">
            Model Status
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Available:</span>
              <span
                className={
                  result.model?.available
                    ? "text-green-600"
                    : "text-red-600"
                }
              >
                {result.model?.available ? "✅ Yes" : "❌ No"}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Model:</span>
              <span className="text-gray-600">
                {result.model?.name}
              </span>
            </div>
            {result.model?.size && (
              <div className="flex justify-between">
                <span>Size:</span>
                <span className="text-gray-600">
                  {result.model.size}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {result.recommendations &&
        result.recommendations.length > 0 && (
          <div className="mt-4">
            <h3 className="font-semibold text-gray-800 mb-2">
              Recommendations
            </h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
              {result.recommendations.map(
                (rec: string, idx: number) => (
                  <li key={idx}>{rec}</li>
                ),
              )}
            </ul>
          </div>
        )}

      {result.error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-700 text-sm">{result.error}</p>
        </div>
      )}
    </div>
  );
}