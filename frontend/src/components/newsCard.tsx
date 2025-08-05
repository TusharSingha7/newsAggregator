import Image from "next/image";
import { newsCardProps } from "@/lib/utils";

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
