"use client";

import { useState } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  flexRender,
  SortingState,
} from "@tanstack/react-table";
import { RateComponentProps } from "@/types/rates";
import { columns } from "@/hooks/tableColumns";

export default function RateTable({ initialRates }: RateComponentProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  console.log("col", initialRates);

  // 2. Initialize Table Instance
  const table = useReactTable({
    data: initialRates,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(), // Added for sorting capability
  });

  return (
    <div className="p-4 border rounded-lg bg-white shadow-sm overflow-x-auto">
      <table className="w-full border-collapse">
        <thead className="bg-gray-50 text-gray-700 text-sm uppercase">
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th
                  key={header.id}
                  className="p-3 border-b text-left cursor-pointer hover:bg-gray-100 select-none"
                  onClick={header.column.getToggleSortingHandler()}
                >
                  <div className="flex items-center gap-2">
                    {flexRender(
                      header.column.columnDef.header,
                      header.getContext(),
                    )}
                    {/* Sorting Indicators */}
                    <span>
                      {header.column.getIsSorted() === "asc" ? "🔼" : ""}
                      {header.column.getIsSorted() === "desc" ? "🔽" : ""}
                    </span>
                  </div>
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody className="text-gray-600 text-sm">
          {table.getRowModel().rows.map((row) => (
            <tr
              key={row.id}
              className="hover:bg-gray-50 border-b last:border-0"
            >
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="p-3">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
