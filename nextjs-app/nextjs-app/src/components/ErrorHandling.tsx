"use client";

interface ErrorHandlingProps {
  testResult: unknown;
}

export default function ErrorHandling({ testResult }: ErrorHandlingProps) {
  if (!testResult) return null;
  
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const result = testResult as any;

  return (
    <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold mb-4 flex items-center">
        <span className="mr-2">Integration Test Results</span>
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium ${
            result.success
              ? "bg-green-100 text-green-800"
              : "bg-red-100 text-red-800"
          }`}
        >
          {result.success ? "Passed" : "Failed"}
        </span>
      </h2>

      {result.success ? (
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">
              Test Prompt
            </h3>
            <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
              {result.testResults?.originalPrompt}
            </p>
          </div>

          <div>
            <h3 className="font-semibold text-gray-800 mb-2">
              Optimized Result
            </h3>
            <p className="text-sm text-gray-800 bg-blue-50 p-3 rounded">
              {result.testResults?.optimizedPrompt}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="font-semibold text-gray-800 mb-2">
                Metrics
              </h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>Quality Score:</span>
                  <span className="font-medium">
                    {result.testResults?.qualityScore}/10
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Processing Time:</span>
                  <span className="font-medium">
                    {result.testResults?.processingTime}ms
                  </span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-800 mb-2">
                Expert Identity
              </h3>
              <p className="text-sm text-gray-600">
                {result.testResults?.expertIdentity}
              </p>
            </div>
          </div>

          {result.testResults?.reasoning && (
            <div>
              <h3 className="font-semibold text-gray-800 mb-2">
                PromptWizard Analysis
              </h3>
              <p className="text-sm text-gray-600">
                {result.testResults.reasoning}
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-700 text-sm">{result.error}</p>
        </div>
      )}
    </div>
  );
}