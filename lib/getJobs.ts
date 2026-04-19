import Papa from "papaparse";

export interface Job {
  ID: string;
  Title: string;
  Company: string;
  Category: string;
  Location: string;
  Link: string;
  Description: string;
  DateAdded: string; // New field for sorting
  Experience: string; // New field
}

export async function getJobs(): Promise<Job[]> {
  const url = process.env.SHEET_URL || process.env.NEXT_PUBLIC_SHEET_URL;

  if (!url) {
    console.error("SHEET_URL is missing");
    return [];
  }

  try {
    // REMOVED: cache: 'no-store' and the timestamp 't='
    // These are what caused the "NEXT_STATIC_GEN_BAILOUT" error
    const response = await fetch(url);

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const csvData = await response.text();

    const parsed = Papa.parse(csvData, {
      header: true,
      skipEmptyLines: true,
      transformHeader: (h) => h.trim(),
    });

    const normalizedData = (parsed.data as any[]).map((row) => ({
      ID: String(row.ID || row.id || row.Id || "").trim(),
      Title: row.Title || row.title || "Unknown Title",
      Company: row.Company || row.company || "Unknown Company",
      Category: row.Category || row.category || "General",
      Location: row.Location || row.location || "Remote",
      Link: row.Link || row.link || "#",
      Description: row.Description || row.description || "",
      DateAdded: row.DateAdded || "2024-01-01", // Fallback for old rows
      Experience: row.Experience || row[8] || "Not specified",
    }));

    return normalizedData as Job[];
  } catch (error) {
    console.error("Data Fetch Error:", error);
    return [];
  }
}

// Add this to your existing lib/getJobs.ts
export async function getJobById(id: string): Promise<Job | null> {
  const jobs = await getJobs();
  return jobs.find((job) => job.ID === id) || null;
}
