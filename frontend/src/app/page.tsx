"use client";
import useSWR from "swr";
import RateComponent from "@/components/rates/RateComponent";
import { getLatestRates } from "@/services/rateService";
import { Rate } from "@/types/rates";

const fetcher = async () => {
  const data = await getLatestRates();
  return data;
};

export default function Home() {
  const { data: rates = [], error, isLoading } = useSWR<Rate[]>("latest-rates", fetcher, {
    refreshInterval: 5000,
    dedupingInterval: 3000,
    revalidateOnFocus: true,
  });

  if (error) {
    return (
      <div className="max-w-[1440px] w-full mx-auto p-2 md:p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-red-800">
                Failed to load latest rates
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <p>Unable to fetch the latest interest rates. Please check your internet connection and try again.</p>
              </div>
              <div className="mt-4">
                <button
                  onClick={() => window.location.reload()}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  <svg className="-ml-1 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Retry
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-[1440px] w-full mx-auto p-2 md:p-8">
      {isLoading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-2 md:p-6 md:mb-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="animate-spin h-6 w-6 text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-blue-800">
                Loading latest rates
              </h3>
              <div className="mt-1 text-sm text-blue-700">
                <p>Fetching the most recent interest rate data...</p>
              </div>
            </div>
          </div>
        </div>
      )}
      <RateComponent initialRates={rates} />
    </div>
  );
}
