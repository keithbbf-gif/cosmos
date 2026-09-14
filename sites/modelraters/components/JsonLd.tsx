import { websiteOrganizationGraph } from "@/lib/json-ld";

export function JsonLd() {
  const data = websiteOrganizationGraph();
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}
