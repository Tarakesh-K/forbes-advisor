import { NavBarProps } from "@/types/navBar";

export default function NavBar(props: NavBarProps) {
  const { navBarOption, setNavBarOption } = props;

  return (
    <div className="bg-gradient-to-b from-gray-400 to-white p-2 md:p-4 rounded-md h-max md:h-[90vh]">
      <p>
        Current Tab:{" "}
        <span className="font-bold">
          {navBarOption.charAt(0).toUpperCase() + navBarOption.slice(1)}
        </span>
      </p>

      <nav className="mt-4 flex md:flex-col gap-3 items-start">
        <button
          onClick={() => setNavBarOption("home")}
          className={`flex items-center px-4 py-2 rounded-lg transition-all duration-300 text-sm font-medium w-full
      ${
        navBarOption === "home"
          ? "bg-blue-600 text-white shadow-md shadow-blue-200"
          : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
      }`}
        >
          Home
        </button>

        <button
          onClick={() => setNavBarOption("history")}
          className={`flex items-center px-4 py-2 rounded-lg transition-all duration-300 text-sm font-medium w-full
      ${
        navBarOption === "history"
          ? "bg-blue-600 text-white shadow-md shadow-blue-200"
          : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
      }`}
        >
          History
        </button>
      </nav>
    </div>
  );
}
