import { Atom, Briefcase, Cpu, Globe, HeartPlusIcon, Trophy, Tv } from "lucide-react";
import Link from "next/link";

export function AppSidebar({ state }: { state: boolean }) {
  const getSpanClasses = (isExpanded: boolean) => {
    return `
      overflow-hidden transition-all whitespace-nowrap
      ${isExpanded ? "w-full ml-2" : "w-0"}
    `;
  };

  return (
    <div className="flex flex-col h-full pt-5 gap-2 pl-2">
      <Link
        href={"/business"}
        className={"hover:bg-accent p-3 rounded flex items-center"}
      >
        <Briefcase />
        <span className={getSpanClasses(state)}>Business</span>
      </Link>

      <Link
        href={"/general"}
        className={"hover:bg-accent p-3 rounded flex items-center"}
      >
        <Globe />
        <span className={getSpanClasses(state)}>General</span>
      </Link>

      <Link
        href={"/sports"}
        className={"hover:bg-accent p-3 rounded flex items-center"}
      >
        <Trophy />
        <span className={getSpanClasses(state)}>Sports</span>
      </Link>

      <Link
        href={"/entertainment"}
        className={"hover:bg-accent p-3 rounded flex items-center"}
      >
        <Tv />
        <span className={getSpanClasses(state)}>Entertainment</span>
      </Link>
      <Link
        href={"/health"}
        className={"hover:bg-accent p-3 rounded flex items-center"}
      >
        <HeartPlusIcon />
        <span className={getSpanClasses(state)}>Health</span>
      </Link>
      <Link
        href={"/science"}
        className={"hover:bg-accent p-3 rounded flex items-center"}
      >
        <Atom />
        <span className={getSpanClasses(state)}>Science</span>
      </Link>
      <Link
        href={"/technology"}
        className={"hover:bg-accent p-3 rounded flex items-center"}
      >
        <Cpu />
        <span className={getSpanClasses(state)}>Technology</span>
      </Link>
    </div>
  );
}
