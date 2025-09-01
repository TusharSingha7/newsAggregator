"use client";

import { newsCardProps } from "@/lib/utils";
import NewsCard from "./newsCard";
import axios from "axios";
import { useEffect, useState } from "react";

export default function Body({ category = "" }: { category: string }) {
  const [newsInstances, setNewsInstances] = useState<newsCardProps[]>([]);
  useEffect(() => {
    const userId = localStorage.getItem("user--id");
    const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL;

    try {
      const response = axios.get(
        `${BASE_URL}/everything${category}?userId=${userId}`
      );

      response.then((res) => {
        const seen = new Set<string>();
        setNewsInstances(() => {
          return res.data.filter((item : newsCardProps) => {
            if(seen.has(item.url) || !item.urlToImage) return false;
            seen.add(item.url);
            return true;
          })
        });
      });
    } catch (error) {
      console.log(error);
    }
  }, [category]);
  return (
    <div className="grid grid-cols-[repeat(auto-fit,minmax(400px,1fr))] h-full overflow-y-auto">
      {newsInstances.map((newsInstance, index) => {
        if (!newsInstance.urlToImage) {
          return;
        }
        return <NewsCard key={index} newsInstance={newsInstance} />;
      })}
    </div>
  );
}
