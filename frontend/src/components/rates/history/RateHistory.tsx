"use client";
import { useState, useEffect } from "react";
import { getRateHistory } from "@/services/rateService";
import { DateRange, RateComponentProps, RateTableProps } from "@/types/rates";
import { Rate } from "@/types/rates";
import RateLineGraph from "@/components/rates/history/RateLineGraph";

export default function RateHistory({ initialRates }: RateComponentProps) {
  const [data, setData] = useState<Rate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const providers = Array.from(new Set(initialRates.map((r) => r.provider)));
  const types = Array.from(new Set(initialRates.map((r) => r.rate_type)));
  const [range, setRange] = useState<string>("0:1000");

  const today = new Date();
  const toDateDefault = today.toISOString().split("T")[0];
  const fromDateDefault = new Date(today);
  fromDateDefault.setDate(fromDateDefault.getDate() - 30);
  const fromDateString = fromDateDefault.toISOString().split("T")[0];

  const [dateRange, setDateRange] = useState<DateRange>({
    fromDate: fromDateString,
    toDate: toDateDefault,
  });
  const [provider, setProvider] = useState(providers[0]);
  const [type, setType] = useState(types[0]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const history = await getRateHistory({
          provider,
          type,
          range,
          from_date: dateRange.fromDate,
          to_date: dateRange.toDate,
        });
        // Sort by date to ensure the line chart flows correctly
        const sortedData = history.sort(
          (a, b) =>
            new Date(a.effective_date).getTime() -
            new Date(b.effective_date).getTime(),
        );
        setData(sortedData);
      } catch (err) {
        console.error("Error fetching rate history:", err);
        setError("Failed to load rate history data. Please try adjusting your filters or check your connection.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // Auto-refresh every 60 seconds
    const interval = setInterval(fetchData, 60000);

    return () => clearInterval(interval); // Cleanup on unmount or dependency change
  }, [dateRange.fromDate, dateRange.toDate, provider, range, type]); // Refetch whenever inputs change

  const rateTableProps: RateTableProps = {
    data,
    loading,
  };

  return (
    <div className="p-6 bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col justify-between h-full w-full gap-6">
      <h2 className="text-xl font-bold  text-gray-800">Rate History Trend</h2>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Error loading rate history
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 1. Select Controls */}
      <div className="flex gap-4 ">
        <div className="flex-1">
          <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">
            Provider
          </label>
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value.toLowerCase())}
            className="w-full p-2 border rounded-md bg-gray-50 focus:ring-2 focus:ring-blue-500 outline-none"
          >
            {providers.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>
        <div className="flex-1">
          <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">
            Rate Type
          </label>
          <select
            value={type}
            onChange={(e) => setType(e.target.value.toLowerCase())}
            className="w-full p-2 border rounded-md bg-gray-50 focus:ring-2 focus:ring-blue-500 outline-none"
          >
            {types.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 2. Chart Display */}
      <RateLineGraph {...rateTableProps} />
    </div>
  );
}
