import { RateTableProps } from "@/types/rates";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

export default function RateLineGraph(props: RateTableProps) {
  const { data, loading } = props;

  return (
    <div className="flex-1 w-full h-full">
      {loading ? (
        <div className="h-full flex items-center justify-center">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 w-full max-w-md">
            <div className="flex items-center">
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-800">
                  Loading history data...
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : data.length > 0 ? (
        <ResponsiveContainer
          width="100%"
          height="100%"
          minHeight={300}
          minWidth={300}
        >
          <LineChart
            data={data}
            margin={{ top: 5, right: 20, bottom: 5, left: 0 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              stroke="#f0f0f0"
            />
            <XAxis
              dataKey="effective_date"
              tick={{ fontSize: 12 }}
              tickFormatter={(str) =>
                new Date(str).toLocaleDateString(undefined, {
                  month: "short",
                  day: "numeric",
                })
              }
            />
            <YAxis
              domain={[0, "auto"]}
              tick={{ fontSize: 12 }}
              tickFormatter={(val) => `${val}%`}
            />
            <Line
              type="monotone"
              dataKey="rate_value"
              stroke="#2563eb"
              strokeWidth={3}
              dot={false}
              activeDot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-full flex items-center justify-center">
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 w-full max-w-md">
            <div className="text-center">
              <h3 className="mt-2 text-sm font-medium text-gray-900">No history data found</h3>
              <p className="mt-1 text-sm text-gray-500">
                Try adjusting your date range or selecting different filters.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
