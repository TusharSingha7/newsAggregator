"use client"
import Image from "next/image";
import { newsCardProps } from "@/lib/utils";
import axios from "axios";

export default function NewsCard({
  newsInstance,
}: {
  newsInstance: newsCardProps;
}) {
  return (
    <div className="p-1">
      {/* 1. The card is a flex column and has a defined height */}
      <div className="flex flex-col h-96 overflow-hidden rounded-lg border border-slate-500">
        {/* 2. The link (image parent) is set to grow and fill space */}
        <a
          href={newsInstance.url}
          target="_blank"
          rel="noopener noreferrer"
          className="relative flex-grow" // Use flex-grow to fill available space
          onClick={async ()=>{
            //send a request to backend
            console.log(newsInstance.embedding)
            if(!newsInstance.embedding || !localStorage.getItem('user--id')) return;
            try{
                const response = await axios.post('http://localhost:8000/store',{
                userId: localStorage.getItem('user--id'),
                embedding : newsInstance.embedding
                });
                if(response) console.log("posted" , newsInstance.embedding)
            }
            catch(e) {
              console.log("error posting" , e)
            }
            
          }}
        >
          <Image
            src={newsInstance.urlToImage!} // We can use ! because we filtered nulls
            alt={newsInstance.title}
            fill
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            className="object-cover"
          />
        </a>
        <div className="p-4">
          <h2 className="font-bold text-lg truncate">{newsInstance.title}</h2>
          <p className="text-sm text-gray-500 line-clamp-2">
            {newsInstance.description}
          </p>
        </div>
      </div>
    </div>
  );
}
