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
    throw new Error(
      "SHEET_URL is not defined. Add it to your environment variables.",
    );
  }

  try {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) throw new Error("Failed to fetch from Google Sheets");

    const csvData = await response.text();
    const parsed = Papa.parse(csvData, { header: true, skipEmptyLines: true });

    return parsed.data as Job[];
  } catch (error) {
    console.error("Data Fetch Error:", error);
    return []; // Return empty list so the site doesn't crash
  }
}
