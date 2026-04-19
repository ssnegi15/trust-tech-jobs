"use client";

export default function Error({ reset }: { reset: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-center px-4">
      <h2 className="text-2xl font-bold text-gray-800">
        Oops! Something went wrong.
      </h2>
      <p className="text-gray-600 mb-6">
        We couldn't load the jobs right now. This is usually temporary.
      </p>
      <button
        onClick={() => reset()}
        className="bg-black text-white px-6 py-2 rounded-lg font-bold hover:bg-gray-800"
      >
        Try Again
      </button>
    </div>
  );
}
