

import { newsCardProps } from "@/lib/utils";
import HeadlinesCarousel from "./headlinesCarousel";
import axios from "axios";

async function newsFetcher({
  url,
}: {
  url: string;
}): Promise<newsCardProps[]> {
  try {
    const response = await axios.get(url);
    const data: newsCardProps[] = response.data || [];
    return data;
  } catch (error) {
    console.log(error);
    return [];
  }
}

export const Headlines = async ({
  category,
}: {
  category : string
}) => {
  const headlinesResponse: newsCardProps[] = await newsFetcher({url:`https://newsaggregator.tushar-server.diy/top-headlines${category}`});
  const headlineInstances: newsCardProps[] = headlinesResponse
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
        embedding : newsInstance.embedding || []
      };
    });
  return <HeadlinesCarousel newsInstances={headlineInstances} />;
};
