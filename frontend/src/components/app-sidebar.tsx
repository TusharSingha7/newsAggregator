import { BookOpen, Gavel, Trophy, Tv } from "lucide-react";
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
        href={"/politics"}
        className={"hover:bg-accent p-3 rounded flex items-center"}
      >
        <Gavel />
        <span className={getSpanClasses(state)}>Politics</span>
      </Link>

      <Link
        href={"/education"}
        className={"hover:bg-accent p-3 rounded flex items-center"}
      >
        <BookOpen />
        <span className={getSpanClasses(state)}>Educational</span>
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
    </div>
  );
}
