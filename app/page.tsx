"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { getJobs, Job } from "@/lib/getJobs";

export default function Home() {
  const [allJobs, setAllJobs] = useState<Job[]>([]);
  const [activeFilter, setActiveFilter] = useState("All");
  const [visibleCount, setVisibleCount] = useState(12);

  useEffect(() => {
    getJobs().then((data) => {
      // Sort by DateAdded (Newest first)
      const sorted = [...data].sort((a, b) => {
        const dateA = new Date(a.DateAdded || 0).getTime();
        const dateB = new Date(b.DateAdded || 0).getTime();
        return dateB - dateA;
      });
      setAllJobs(sorted);
    });
  }, []);

  // Filter Logic
  const filteredJobs = allJobs.filter((job) => {
    const title = job.Title.toLowerCase();
    if (activeFilter === "All") return true;
    if (activeFilter === "AI")
      return (
        title.includes("ai") ||
        title.includes("safety") ||
        title.includes("ethics")
      );
    if (activeFilter === ".NET")
      return title.includes(".net") || title.includes("c#");
    if (activeFilter === "React") return title.includes("react");
    return true;
  });

  const displayedJobs = filteredJobs.slice(0, visibleCount);

  return (
    <main className="max-w-6xl mx-auto py-12 px-4 bg-white text-gray-900 min-h-screen">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-black mb-4 tracking-tight">
          Trust Tech Jobs
        </h1>
        <p className="text-slate-500 font-medium">
          Showing {filteredJobs.length} specialized roles
        </p>
      </header>

      {/* Filter Bar */}
      <div className="flex justify-center gap-2 mb-12 sticky top-4 z-10">
        <div className="bg-white/80 backdrop-blur-md border border-slate-200 p-1.5 rounded-2xl shadow-xl shadow-slate-200/50 flex gap-1">
          {["All", "AI", ".NET", "React"].map((filter) => (
            <button
              key={filter}
              onClick={() => {
                setActiveFilter(filter);
                setVisibleCount(12); // Reset paging on filter change
              }}
              className={`px-5 py-2 rounded-xl text-sm font-bold transition-all ${
                activeFilter === filter
                  ? "bg-blue-600 text-white shadow-md shadow-blue-200"
                  : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
              }`}
            >
              {filter}
            </button>
          ))}
        </div>
      </div>

      {/* Jobs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {displayedJobs.map((job) => (
          <Link
            key={job.ID}
            href={`/jobs/${job.ID}/`}
            className="group relative flex flex-col bg-white border border-slate-200 rounded-3xl p-6 transition-all duration-300 hover:shadow-2xl hover:border-blue-500/50 hover:-translate-y-1"
          >
            {/* Header: Experience & Location */}
            <div className="flex justify-between items-start mb-4">
              <span className="flex items-center gap-1.5 px-3 py-1 bg-slate-900 text-white text-[10px] font-bold rounded-full">
                <svg
                  className="w-3 h-3"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
                {job.Experience || "Entry Level"}
              </span>
              <span className="text-[10px] font-bold text-slate-400">
                {job.DateAdded
                  ? new Date(job.DateAdded).toLocaleDateString()
                  : "New"}
              </span>
            </div>

            <h3 className="text-xl font-bold text-slate-900 group-hover:text-blue-600 mb-1 leading-tight">
              {job.Title}
            </h3>
            <p className="text-blue-600 font-bold text-sm mb-4">
              @{job.Company}
            </p>

            {/* Tech Tags Section */}
            <div className="flex flex-wrap gap-2 mb-6">
              {job.Category.split(",").map((tag) => (
                <span
                  key={tag}
                  className="bg-blue-50 text-blue-700 text-[10px] font-bold px-2 py-0.5 rounded border border-blue-100"
                >
                  {tag.trim()}
                </span>
              ))}
            </div>

            {/* Footer: NCR specific highlighting */}
            <div className="mt-auto pt-4 border-t border-slate-50 flex items-center justify-between text-xs font-semibold text-slate-400">
              <div className="flex items-center gap-1.5">
                <span
                  className={
                    job.Location.toLowerCase().includes("noida") ||
                    job.Location.toLowerCase().includes("gurgaon")
                      ? "text-emerald-600 font-bold"
                      : ""
                  }
                >
                  {job.Location}
                </span>
              </div>
              <span className="text-blue-500 group-hover:translate-x-1 transition-transform">
                View Role →
              </span>
            </div>
          </Link>
        ))}
      </div>

      {/* Empty State */}
      {filteredJobs.length === 0 && (
        <div className="text-center py-20">
          <p className="text-slate-400 font-medium italic">
            No {activeFilter} roles found at the moment.
          </p>
        </div>
      )}

      {/* Pagination */}
      {visibleCount < filteredJobs.length && (
        <div className="mt-12 text-center">
          <button
            onClick={() => setVisibleCount((prev) => prev + 12)}
            className="bg-slate-900 text-white px-10 py-4 rounded-2xl font-bold hover:bg-blue-600 hover:shadow-xl hover:shadow-blue-200 transition-all active:scale-95"
          >
            Show More Opportunities
          </button>
        </div>
      )}
    </main>
  );
}
