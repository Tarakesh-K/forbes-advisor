"use client";
import { RateComponentProps } from "@/types/rates";
import RateTable from "@/components/rates/table/RateTable";
import NavBar from "@/components/navBar/NavBar";
import { useState } from "react";
import { NavBarOption, NavBarProps } from "@/types/navBar";
import RateHistory from "@/components/rates/history/RateHistory";

export default function RateComponent({ initialRates }: RateComponentProps) {
  const [navBarOption, setNavBarOption] = useState<NavBarOption>("home");

  const navBarProps: NavBarProps = {
    navBarOption,
    setNavBarOption,
  };

  return (
    <div className="grid grid-cols-12 gap-6 sm:h-[90vh] md:h-full">
      <div className="col-span-12 md:col-span-3">
        <NavBar {...navBarProps} />
      </div>
      <div className="col-span-12 md:col-span-9">
        {navBarOption === "home" && <RateTable initialRates={initialRates} />}
        {navBarOption === "history" && (
          <RateHistory initialRates={initialRates} />
        )}
      </div>
    </div>
  );
}
