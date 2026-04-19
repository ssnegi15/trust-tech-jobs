import { getJobs } from "@/lib/getJobs";
import Link from "next/link";

export default async function Home() {
  const jobs = await getJobs();

  return (
    <main className="max-w-6xl mx-auto py-12 px-4">
      <header className="mb-12 text-center">
        <h1 className="text-4xl font-extrabold text-gray-900 mb-4">
          Trust Tech Jobs
        </h1>
        <p className="text-lg text-gray-600">
          The latest roles in AI Safety, Ethics, and Policy.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {jobs.map((job) => (
          <Link
            key={job.ID}
            href={`/jobs/${job.ID}`}
            className="group block p-6 bg-white border rounded-xl shadow-sm hover:shadow-md hover:border-blue-300 transition-all"
          >
            <div className="mb-4">
              <span className="inline-block px-3 py-1 text-xs font-semibold text-blue-700 bg-blue-50 rounded-full">
                {job.Category}
              </span>
            </div>
            <h2 className="text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
              {job.Title}
            </h2>
            <p className="text-gray-600 mt-1">{job.Company}</p>
            <div className="mt-4 flex items-center text-sm text-gray-500">
              <svg
                className="w-4 h-4 mr-1"
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
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              {job.Location}
            </div>
          </Link>
        ))}
      </div>
    </main>
  );
}
