"use client";

import { Button } from "@/components/ui/button";
import { UserCircle, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import Link from "next/link";
import { Dispatch, SetStateAction, useState } from "react";
import { ModeToggle } from "./toggleButton";
import { useRouter } from "next/navigation";

export default function Header({
  isSidebarOpen,
  setSidebarOpen,
}: {
  isSidebarOpen: boolean;
  setSidebarOpen: Dispatch<SetStateAction<boolean>>;
}) {
  const [searchValue, setSearchValue] = useState<string>();
  const router = useRouter();

  return (
    <header className="flex items-center shrink-0 h-16 border-b px-4 md:px-6">
      <Button
        variant="ghost"
        size="icon"
        className="mr-1"
        onClick={() => setSidebarOpen(!isSidebarOpen)}
      >
        {isSidebarOpen ? (
          <PanelLeftClose className="h-5 w-5" />
        ) : (
          <PanelLeftOpen className="h-5 w-5" />
        )}
        <span className="sr-only">Toggle sidebar</span>
      </Button>

      <Link
        href="/"
        className="mr-2 p-2 rounded-md hover:bg-accent hidden sm:block"
      >
        {" "}
        Home Page{" "}
      </Link>
      <Link
        href="/"
        className=" p-2 rounded-md hover:bg-accent hidden sm:block"
      >
        {" "}
        About{" "}
      </Link>
      <div className="flex-1 mx-4">
        <div className="relative">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (searchValue) {
                router.push(`/search?q=${searchValue}`);
              }
            }}
          >
            <input
              className="w-full bg-muted rounded-full pl-4 pr-10 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              type="text"
              placeholder="Search..."
              autoComplete="off"
              onChange={(e) => {
                setSearchValue(() => {
                  return e.target.value;
                });
              }}
            />
          </form>
          <div className="absolute inset-y-0 right-0 flex items-center pr-3">
            <svg
              className="w-4 h-4 text-muted-foreground"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                clipRule="evenodd"
              />
            </svg>
          </div>
        </div>
      </div>
      <ModeToggle />
      <UserCircle className="h-12 w-12 hover:bg-accent p-2 rounded-full" />
    </header>
  );
}
