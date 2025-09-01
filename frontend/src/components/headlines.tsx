"use client";

import { newsCardProps } from "@/lib/utils";
import HeadlinesCarousel from "./headlinesCarousel";
import axios from "axios";
import { useState , useEffect } from "react";

async function newsFetcher({
  url,
}: {
  url: string;
}): Promise<newsCardProps[]> {
  try {
    const response = await axios.get(url);
    const data: newsCardProps[] = response.data || [];
    const seenUrls = new Set<string>();
    return data.filter((item: newsCardProps) => {
      if(seenUrls.has(item.url) || !item.urlToImage) return false;
      seenUrls.add(item.url);
      return true;
    })
  } catch (error) {
    console.log(error);
    return [];
  }
}

export const Headlines = ({
  category,
}: {
  category : string
}) => {

  const [headlines , setHeadlines] = useState<newsCardProps[]>([]);

  useEffect(()=> {
    const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL;
    if(!BASE_URL) return;

    newsFetcher({url:`${BASE_URL}/top-headlines${category}`}).then((data)=> {
      setHeadlines(()=> {
        return data;
      });
    })

  },[category])

  return <HeadlinesCarousel newsInstances={headlines} />;
};
