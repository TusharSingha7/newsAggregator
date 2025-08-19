"use client";

import { newsCardProps } from "@/lib/utils";
import NewsCard from "./newsCard";
import axios from "axios";
import { useEffect, useState } from "react";

export default function Body({ category = "" }: { category: string }) {
  const [newsInstances, setNewsInstances] = useState<newsCardProps[]>([]);

  useEffect(() => {
    const userId = localStorage.getItem("user--id");
    try {
      const response = axios.get(
        `https://newsaggregator.tushar-server.diy/everything${category}?userId=${userId}`
      );

      response.then((res) => {
        setNewsInstances(() => {
          return res.data;
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
