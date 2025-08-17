import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export type newsCardProps = {
  source : {
    id : string,
    name : string
  },
  author : string,
  title : string,
  description : string,
  url : string,
  urlToImage : string,
  publishedAt : Date,
  content : string,
  embedding? : number[]
}
