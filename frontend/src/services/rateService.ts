import { RATE_ENDPOINTS } from "@/repos/ratesRepo";
import { Rate, RateHistory } from "@/types/rates";

export async function getLatestRates(): Promise<Rate[]> {
  try {
    const res = await fetch(RATE_ENDPOINTS.LATEST, { cache: "no-store" });
    if (!res.ok) throw new Error(`Failed to fetch rates: ${res.status}`);
    return res.json();
  } catch (error) {
    console.error("Error fetching latest rates:", error);
    throw error;
  }
}

export async function getRateHistory(
  rateHistory: RateHistory,
): Promise<Rate[]> {
  try {
    const {provider, type, range, from_date, to_date} = rateHistory;
    const params = new URLSearchParams({ provider, type, range, from_date, to_date });
    const res = await fetch(`${RATE_ENDPOINTS.HISTORY}?${params}`, {
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`Failed to fetch history: ${res.status}`);
    return res.json();
  } catch (error) {
    console.error("Error fetching rate history:", error);
    throw error;
  }
}

export async function getRateHistoryByLists(
  providers: string[] | string,
  types: string[] | string,
  range = "0:30",
): Promise<Rate[]> {
  try {
    const providerList = Array.isArray(providers)
      ? providers
      : providers
          .split(",")
          .map((i) => i.trim())
          .filter(Boolean);
    const typeList = Array.isArray(types)
      ? types
      : types
          .split(",")
          .map((i) => i.trim())
          .filter(Boolean);

    const params = new URLSearchParams({ range });
    if (providerList.length > 0) params.set("provider", providerList.join(","));
    if (typeList.length > 0) params.set("type", typeList.join(","));

    const res = await fetch(`${RATE_ENDPOINTS.HISTORY}?${params}`, {
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`Failed to fetch history: ${res.status}`);
    return res.json();
  } catch (error) {
    console.error("Error fetching rate history by lists:", error);
    throw error;
  }
}
