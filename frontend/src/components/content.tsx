"use server";

import { newsCardProps } from "@/lib/utils";
import NewsCard from "./newsCard";
import { Headlines } from "./headlines";
import axios from "axios";

export default async function PageContent({ category }: { category: string }) {
  const response = await axios.get("http://127.0.0.1:8000/home");

  const newsInstances: newsCardProps[] = response.data
    .filter((newsInstance: newsCardProps) => {
      if (!newsInstance.urlToImage) {
        return false;
      }
      return true;
    })
    .map((newsInstance: newsCardProps) => {
      return {
        source: {
          id: newsInstance.source.id,
          name: newsInstance.source.name,
        },
        author: newsInstance.author,
        title: newsInstance.title,
        description: newsInstance.description,
        url: newsInstance.url,
        urlToImage: newsInstance.urlToImage,
        publishedAt: newsInstance.publishedAt,
        content: newsInstance.content,
      };
    });

  return (
    <div className="grid grid-cols-[repeat(auto-fit,minmax(400px,1fr))] h-full overflow-y-auto">
      <div className="col-span-full relative flex items-center">
        <Headlines newsInstances={newsInstances} />
      </div>
      {newsInstances.map((newsInstance, index) => {
        if (!newsInstance.urlToImage) {
          return;
        }
        return <NewsCard key={index} newsInstance={newsInstance} />;
      })}
    </div>
  );
}
