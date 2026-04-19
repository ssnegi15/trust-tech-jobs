import { getJobs, getJobById } from "@/lib/getJobs";
import { notFound } from "next/navigation";
import Link from "next/link";

export async function generateStaticParams() {
  const jobs = await getJobs();

  if (!jobs || jobs.length === 0) return [];

  return jobs.map((job) => ({
    id: String(job.ID), // MUST be 'id' because the folder is [id]
  }));
}

// Ensure params is handled as a Promise for newer Next.js versions
export default async function JobPage({
  params,
}: {
  params: Promise<{ id: string }> | { id: string };
}) {
  const resolvedParams = await params;
  const id = resolvedParams.id;

  if (!id) {
    console.error("Job Fetch Error: ID is undefined");
    return notFound();
  }

  const job = await getJobById(id);

  if (!job) {
    console.error(`Job Fetch Error: No job found with ID ${id}`);
    return notFound();
  }

  return (
    <div className="min-h-screen bg-slate-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        <Link
          href="/"
          className="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-800 mb-8 transition-colors"
        >
          <svg
            className="w-4 h-4 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back to Job Board
        </Link>

        <article className="bg-white border border-slate-200 rounded-3xl shadow-xl shadow-slate-200/50 overflow-hidden">
          {/* Header Banner */}
          <div className="bg-blue-600 h-3 w-full"></div>

          <div className="p-8 md:p-12">
            <div className="flex flex-wrap gap-3 mb-6">
              <span className="bg-blue-50 text-blue-700 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-widest border border-blue-100">
                {job.Category}
              </span>
              <span className="bg-slate-50 text-slate-600 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-widest border border-slate-100">
                Remote Friendly
              </span>
            </div>

            <h1 className="text-3xl md:text-4xl font-black text-slate-900 mb-4 leading-tight">
              {job.Title}
            </h1>

            <div className="flex flex-col sm:flex-row sm:items-center gap-4 text-slate-600 mb-8 pb-8 border-b border-slate-100">
              <div className="flex items-center font-semibold">
                <span className="text-blue-500 mr-2 font-bold">@</span>
                {job.Company}
              </div>
              <div className="hidden sm:block text-slate-300">|</div>
              <div className="flex items-center">
                <svg
                  className="w-4 h-4 mr-2 text-slate-400"
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
            </div>

            <div className="prose prose-slate max-w-none mb-10">
              <h3 className="text-xl font-bold text-slate-900 mb-4 border-b pb-2">
                Job Description
              </h3>

              {/* Option B: If the scraper is still sending raw HTML tags, use this instead: */}
              <div
                className="text-slate-700 leading-relaxed text-lg"
                dangerouslySetInnerHTML={{ __html: job.Description }}
              />
            </div>

            <div className="bg-slate-50 rounded-2xl p-6 border border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-6">
              <div>
                <p className="text-sm text-slate-500 font-medium">
                  Ready to apply?
                </p>
                <p className="text-slate-900 font-bold">
                  Apply via the official company portal
                </p>
              </div>
              <a
                href={job.Link}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full sm:w-auto text-center bg-blue-600 text-white px-10 py-4 rounded-xl font-bold hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-200 transition-all transform active:scale-95"
              >
                Apply Now
              </a>
            </div>
          </div>
        </article>
      </div>
    </div>
  );
}
