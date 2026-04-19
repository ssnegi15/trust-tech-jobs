import { getJobs, getJobById } from "@/lib/getJobs";
import { notFound } from "next/navigation";
import Link from "next/link";

export async function generateStaticParams() {
  const jobs = await getJobs();
  return jobs.map((job) => ({
    id: job.ID,
  }));
}

export default async function JobPage({ params }: { params: { id: string } }) {
  const job = await getJobById(params.id);

  if (!job) {
    notFound();
  }

  return (
    <div className="max-w-3xl mx-auto py-12 px-4">
      <Link
        href="/"
        className="text-blue-600 hover:underline mb-8 inline-block"
      >
        ← Back to all jobs
      </Link>

      <div className="bg-white border rounded-xl p-8 shadow-sm">
        <h1 className="text-3xl font-bold mb-2">{job.Title}</h1>
        <p className="text-xl text-gray-600 mb-6">
          {job.Company} • {job.Location}
        </p>

        <div className="prose max-w-none mb-8">
          <h3 className="text-lg font-semibold">Description</h3>
          <p className="text-gray-700 whitespace-pre-wrap ">
            {job.Description}
          </p>
        </div>

        <a
          href={job.Link}
          target="_blank"
          className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-blue-700 transition"
        >
          Apply for this position
        </a>
      </div>
    </div>
  );
}
