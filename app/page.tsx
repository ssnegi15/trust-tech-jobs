import { getJobs } from "@/lib/getJobs";

export default async function Home() {
  const jobs = await getJobs();

  return (
    <main className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <header className="mb-12 text-center">
          <h1 className="text-4xl font-extrabold text-gray-900 mb-2">
            Trust Tech Jobs
          </h1>
          <p className="text-lg text-gray-600">AI • Privacy • ESG</p>
        </header>

        <div className="grid gap-6">
          {jobs.map((job) => (
            <div
              key={job.ID}
              className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition"
            >
              <div className="flex justify-between items-start">
                <div>
                  <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800 mb-2">
                    {job.Category}
                  </span>
                  <h2 className="text-xl font-bold text-gray-800">
                    {job.Title}
                  </h2>
                  <p className="text-gray-500 font-medium">
                    {job.Company} • {job.Location}
                  </p>
                </div>
                <a
                  href={job.Link}
                  target="_blank"
                  className="bg-black text-white px-5 py-2 rounded-lg font-bold hover:bg-gray-800 transition"
                >
                  Apply
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
