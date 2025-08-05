import PageContent from "@/components/content";
import { Suspense } from "react";

function Fallback() {
  return <div>Loading...</div>;
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: { [key: string]: string | undefined };
}) {
  const q = searchParams.q || "";

  console.log(q);

  return (
    <Suspense fallback={<Fallback />}>
      <PageContent category={q} />
    </Suspense>
  );
}
