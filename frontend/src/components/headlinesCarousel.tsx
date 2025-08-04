"use client"

import {newsCardProps} from "@/lib/utils";
import Autoplay from "embla-carousel-autoplay";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
import NewsCard from "./newsCard";

export default function HeadlinesCarousel( { newsInstances }: { newsInstances: newsCardProps[] }) 
{
    return (
    <Carousel
      className="w-full max-w-full relative rounded-2xl" 
      plugins={[Autoplay({ delay: 2000 })]}
    >
      <CarouselContent className="-ml-4 rounded-2xl">
        {newsInstances.map((newsInstance, index) => (
          <CarouselItem key={index} className="pl-4 md:basis-1/3 lg:basis-1/4">
            <NewsCard newsInstance={newsInstance} />
          </CarouselItem>
        ))}
      </CarouselContent>
      <CarouselPrevious className="absolute left-0.5" />
      <CarouselNext className="absolute right-0.5" />
    </Carousel>
  );
}
