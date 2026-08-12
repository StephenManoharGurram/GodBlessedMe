"use client";

import useIsMobile from "@/app/hooks/useIsMobile";

export default function Section4() {
  const isMobile = useIsMobile(768);

  return (
    <section
      id="section4"
      className="
        relative w-full
        -mt-px
        min-h-dvh sm:min-h-screen
        bg-linear-to-b from-[#3a2a1d] via-[#d8c3a5] to-[#f7f0e6]
        text-[#3a2a1d]
        flex items-center
      "
    >
      <div className="max-w-5xl mx-auto px-4 py-24 sm:py-28 md:py-32 text-center">
        <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold">
          So, now what?
        </h2>

        <div className="mt-4 h-0.5 w-24 mx-auto rounded-full bg-[#d9b678] shadow-[0_0_16px_rgba(217,182,120,0.6)]" />

        <p
          className={`mt-8 leading-relaxed max-w-4xl mx-auto text-[#4b3b2a] ${
            isMobile ? "text-lg" : "text-base sm:text-lg md:text-xl"
          }`}
        >
          Can you look for ways to turn up the volume of God&apos;s kindness
          in a world that really needs more of it — more goodness, more joy,
          more hope.
        </p>

        <p
          className={`mt-4 mb-8 leading-relaxed max-w-4xl mx-auto text-[#4b3b2a] ${
            isMobile ? "text-lg" : "text-base sm:text-lg md:text-xl"
          }`}
        >
          And if you&apos;ve experienced His kindness recently, would you take
          a moment to share that story with someone?
        </p>

        <h2
          className={`mt-4 leading-relaxed max-w-4xl mx-auto text-[#4b3b2a] font-bold ${
            isMobile ? "text-2xl" : "text-base sm:text-2xl md:text-3xl"
          }`}
        >
          That&apos;s It. And may God continue to bless you on your journey.
        </h2>

        <p
          className={`mt-20 leading-relaxed max-w-4xl mx-auto text-[#4b3b2a] ${
            isMobile ? "text-xs" : "text-sm md:text-base"
          }`}
        >
          If you need a church home and a faith community to grow in your
          understanding of God, please look for a Bible-teaching, local church
          you can be part of. If you&apos;re not sure where to start,{" "}
          <a
            href="https://lcc.org"
            target="_blank"
            rel="noreferrer"
            className="text-[#b08452] hover:text-[#d0a97a] underline underline-offset-2"
          >
            Legacy Christian Church
          </a>{" "}
          is one great option to explore.
        </p>

        <p
          className={`mt-6 leading-relaxed max-w-4xl mx-auto text-[#4b3b2a] ${
            isMobile ? "text-xs" : "text-sm md:text-base"
          }`}
        >
          Wherever you end up, just let the pastor know that you&apos;ve been
          blessed by God and want to get to know Him better.
        </p>
      </div>
    </section>
  );
}