import PageContent from "@/components/content";
import { Suspense } from "react";

function Fallback() {
  return <div>Loading...</div>;
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | undefined }>;
}) {
  const params = await searchParams || "";
  const q = params.q

  console.log(q);

  return (
    <Suspense fallback={<Fallback />}>
      <PageContent category={`/${q}`} />
    </Suspense>
  );
}
