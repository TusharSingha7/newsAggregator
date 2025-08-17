
import { Headlines } from "./headlines";
import Body from "./body";

export default async function PageContent({
  category = "",
}: {
  category?: string;
}) {

  return (
    <div className="flex flex-col">
      <div className="relative flex items-center">
          <Headlines category={category} />
        </div>
      <Body category={category} />
    </div>
  );
}
