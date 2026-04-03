import { Rate } from "@/types/rates";
import { createColumnHelper } from "@tanstack/react-table";

const columnHelper = createColumnHelper<Rate>();

// 1. Define Columns
export const columns = [
  columnHelper.accessor("provider", {
    header: "Provider",
    cell: (info) => <span className="font-semibold">{info.getValue()}</span>,
  }),
  columnHelper.accessor("rate_type", {
    header: "Type",
  }),
  columnHelper.accessor("rate_value", {
    header: "Value (%)",
    cell: (info) => <span className="text-blue-600">{info.getValue()}%</span>,
  }),
  columnHelper.accessor("effective_date", {
    header: "Effective Date",
  }),
  columnHelper.accessor("ingestion_ts", {
    header: "Ingestion Timestamp",
  }),
];
