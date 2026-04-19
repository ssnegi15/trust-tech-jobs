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
    console.error(
      "CRITICAL: SHEET_URL is not defined in environment variables.",
    );
    return [];
  }

  try {
    // Append a timestamp to the URL to bypass Google's internal cache
    const cacheBuster = url.includes("?")
      ? `&t=${Date.now()}`
      : `?t=${Date.now()}`;
    const response = await fetch(`${url}${cacheBuster}`, {
      cache: "no-store",
      headers: {
        pragma: "no-cache",
        "cache-control": "no-cache",
      },
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const csvData = await response.text();

    // Debug: Log the first bit of data to the GitHub Action console
    console.log("DEBUG: CSV Data received, length:", csvData.length);

    const parsed = Papa.parse(csvData, {
      header: true,
      skipEmptyLines: true,
      transformHeader: (h) => h.trim(), // Removes accidental spaces in headers
    });

    // Normalization: Ensure the keys match your Job interface exactly
    // even if the Google Sheet headers use different casing
    const normalizedData = (parsed.data as any[]).map((row) => ({
      ID: row.ID || row.id || row.Id || "",
      Title: row.Title || row.title || row.job_title || "Unknown Title",
      Company: row.Company || row.company || "Unknown Company",
      Category: row.Category || row.category || "General",
      Location: row.Location || row.location || "Remote",
      Link: row.Link || row.link || row.url || "#",
      Description: row.Description || row.description || "",
      LogoURL: row.LogoURL || row.logourl || row.logo || "",
    }));

    console.log(`DEBUG: Successfully parsed ${normalizedData.length} jobs.`);
    return normalizedData as Job[];
  } catch (error) {
    console.error("Data Fetch Error:", error);
    return [];
  }
}
