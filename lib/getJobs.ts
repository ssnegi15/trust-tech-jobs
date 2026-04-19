import Papa from "papaparse";

export interface Job {
  ID: string;
  Title: string;
  Company: string;
  Category: string;
  Location: string;
  Link: string;
  Description: string;
  LogoURL: string;
}

export async function getJobs(): Promise<Job[]> {
  const url = process.env.SHEET_URL;

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
      ID: row.ID || row.id || row.Id || Math.random().toString(),
      Title: row.Title || row.title || "Unknown Title",
      Company: row.Company || row.company || "Unknown Company",
      Category: row.Category || row.category || "General",
      Location: row.Location || row.location || "Remote",
      Link: row.Link || row.link || "#",
      Description: row.Description || row.description || "",
      LogoURL: row.LogoURL || row.logourl || "",
    }));

    return normalizedData as Job[];
  } catch (error) {
    console.error("Data Fetch Error:", error);
    return [];
  }
}
