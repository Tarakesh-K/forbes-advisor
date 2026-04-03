import { Dispatch, SetStateAction } from "react";

export type NavBarProps = {
  navBarOption: NavBarOption;
  setNavBarOption: Dispatch<SetStateAction<NavBarOption>>;
};

export type NavBarOption = "home" | "history";
