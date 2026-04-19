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
            href={`/jobs/${job.ID}/`}
            className="group relative flex flex-col bg-white border border-slate-200 rounded-3xl p-6 transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/10 hover:border-blue-500/50 hover:-translate-y-1"
          >
            {/* Accent Tag */}
            <div className="flex justify-between items-start mb-6">
              <div className="text-[10px] font-black uppercase tracking-widest text-blue-600 bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-100">
                {job.Category}
              </div>
              <div className="h-2 w-2 rounded-full bg-slate-200 group-hover:bg-blue-500 transition-colors"></div>
            </div>

            <h3 className="text-xl font-bold text-slate-900 group-hover:text-blue-600 mb-2 leading-tight transition-colors">
              {job.Title}
            </h3>

            <p className="text-slate-500 font-medium text-sm mb-6">
              <span className="text-blue-500 font-bold">@</span> {job.Company}
            </p>

            <div className="mt-auto pt-4 border-t border-slate-50 flex items-center justify-between text-xs font-semibold text-slate-400">
              <div className="flex items-center gap-1.5">
                <svg
                  className="w-4 h-4 text-slate-300"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                  />
                </svg>
                {job.Location}
              </div>
              <span className="text-blue-500 group-hover:translate-x-1 transition-transform">
                Details →
              </span>
            </div>
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
