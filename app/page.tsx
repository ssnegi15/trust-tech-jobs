"use client"; // Needs to be a client component for paging state
import { useState, useEffect } from "react";
import Link from "next/link";
import { getJobs, Job } from "@/lib/getJobs";

export default function Home() {
  const [allJobs, setAllJobs] = useState<Job[]>([]);
  const [visibleCount, setVisibleCount] = useState(12); // Show 12 at a time

  useEffect(() => {
    getJobs().then(setAllJobs);
  }, []);

  const displayedJobs = allJobs.slice(0, visibleCount);

  return (
    <main className="max-w-6xl mx-auto py-12 px-4 bg-white text-gray-900">
      <header className="mb-12 text-center">
        <h1 className="text-4xl font-extrabold mb-4">Trust Tech Jobs</h1>
        <p className="text-gray-600">
          Discover {allJobs.length} roles in AI Safety & Ethics
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {displayedJobs.map((job) => (
          <Link
            key={job.ID}
            href={`/jobs/${job.ID}/`} // Added trailing slash to link
            className="block p-6 bg-white border border-gray-200 rounded-xl hover:shadow-lg transition-all"
          >
            <h2 className="text-xl font-bold text-blue-600">{job.Title}</h2>
            <p className="text-gray-700 font-medium">{job.Company}</p>
            <p className="text-gray-500 text-sm mt-2">{job.Location}</p>
          </Link>
        ))}
      </div>

      {visibleCount < allJobs.length && (
        <div className="mt-12 text-center">
          <button
            onClick={() => setVisibleCount((prev) => prev + 12)}
            className="bg-blue-600 text-white px-8 py-3 rounded-full font-bold hover:bg-blue-700 transition"
          >
            Load More Jobs
          </button>
        </div>
      )}
    </main>
  );
}
