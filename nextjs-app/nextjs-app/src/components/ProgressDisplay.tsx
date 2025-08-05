"use client";

interface ProgressDisplayProps {
  recentSessions: unknown[] | undefined;
}

export default function ProgressDisplay({ recentSessions }: ProgressDisplayProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold mb-4">
        Recent Optimizations
      </h2>

      {recentSessions === undefined ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading sessions...</p>
        </div>
      ) : recentSessions.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No optimizations yet.</p>
          <p className="text-sm">
            Start by optimizing your first prompt!
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
          {recentSessions.map((session: any) => (
            <div
              key={session._id}
              className="border border-gray-200 rounded-lg p-4"
            >
              <div className="flex justify-between items-start mb-2">
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${
                    session.prompt?.optimizationStatus === "completed"
                      ? "bg-green-100 text-green-800"
                      : session.prompt?.optimizationStatus ===
                          "processing"
                        ? "bg-yellow-100 text-yellow-800"
                        : session.prompt?.optimizationStatus === "failed"
                          ? "bg-red-100 text-red-800"
                          : "bg-gray-100 text-gray-800"
                  }`}
                >
                  {session.prompt?.optimizationStatus || "pending"}
                </span>
                {session.qualityScore && (
                  <span className="text-sm font-medium text-blue-600">
                    Score: {session.qualityScore.toFixed(1)}
                  </span>
                )}
              </div>

              <p className="text-sm text-gray-600 mb-2">
                Original:{" "}
                {session.prompt?.originalPrompt.substring(0, 100)}
                {(session.prompt?.originalPrompt.length || 0) > 100 &&
                  "..."}
              </p>

              {session.prompt?.optimizedPrompt && (
                <p className="text-sm text-gray-800">
                  Optimized:{" "}
                  {session.prompt.optimizedPrompt.substring(0, 100)}
                  {session.prompt.optimizedPrompt.length > 100 && "..."}
                </p>
              )}

              <div className="mt-2 text-xs text-gray-500">
                {new Date(session.createdAt).toLocaleDateString()} at{" "}
                {new Date(session.createdAt).toLocaleTimeString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}