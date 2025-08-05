"use server";

import { newsCardProps } from "@/lib/utils";
import HeadlinesCarousel from "./headlinesCarousel";

export const Headlines = async ({
  newsInstances,
}: {
  newsInstances: newsCardProps[];
}) => {
  return <HeadlinesCarousel newsInstances={newsInstances} />;
};
