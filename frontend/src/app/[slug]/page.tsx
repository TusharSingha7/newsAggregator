import PageContent from "@/components/content";

export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  return <PageContent category={`/${slug}`} />;
}
