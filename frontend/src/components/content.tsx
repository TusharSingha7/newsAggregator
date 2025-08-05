
import { newsCardProps } from "@/lib/utils";
import NewsCard from "./newsCard";
import { Headlines } from "./headlines";
import axios from "axios";

async function newsFetcher({endpoint} : {endpoint : string}) : Promise<newsCardProps[]> {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/${endpoint}`);
    const data : newsCardProps[] = response.data;
    return data;
  }
  catch(error) {
    console.log(error);
    return [];
  }
}

export default async function PageContent({ category }: { category: string }) {
  let endpoint = 'home';
  if(category) endpoint = category;

  const response : newsCardProps[] = await newsFetcher({endpoint});

  const newsInstances: newsCardProps[] = response
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
