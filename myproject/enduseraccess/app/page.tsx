import Section1 from "@/app/components/home/Section1";
import Section2 from "@/app/components/home/Section2";
import Section3 from "@/app/components/home/Section3";
import Section4 from "@/app/components/home/Section4";

export default function HomePage() {
  
  return (
    <div className="relative w-full overflow-hidden">
      {/* === SECTION 1 === */}
      <Section1 />

      {/* === SECTION 2 — DARK → SUBTLE WARM TRANSITION === */}
      <Section2 />

      {/* === SECTION 3 — NEW IMAGE === */}
      <Section3 />

      {/* === SECTION 4 — Single beige full-page section === */}
      <Section4 />
    </div>
  );
}
