"use client";

import Image from "next/image";
import useIsMobile from "@/app/hooks/useIsMobile";
import useInView from "@/app/hooks/useInView";

export default function Section3() {
  const isMobile = useIsMobile(768);
  const { ref, isVisible } = useInView<HTMLElement>({
    threshold: [0.2, 0.4],
  });

  return (
    <section
      id="section3"
      ref={ref}
      className={`
        relative w-full
        -mt-px
        min-h-dvh sm:min-h-screen
        ${isVisible ? "section-in-view" : ""}
      `}
    >
      <div className="absolute inset-0 z-0">
        <Image
          src="/bright-side-v2.jpg"
          alt="Golden sunset over a lone tree in a field"
          fill
          priority
          className="object-cover"
        />
      </div>

      <div className="relative z-30 flex items-start md:items-center justify-center px-4 py-12 sm:py-16">
        <div
          className="
            w-full max-w-5xl
            flex flex-col md:flex-row
            items-center md:items-stretch
            justify-center
            gap-6 sm:gap-8
          "
        >
          <div
            className="
              flex-1
              px-6 sm:px-10 py-6 sm:py-8
              rounded-2xl
              bg-white/60 backdrop-blur-xl
              border border-white/40
              shadow-xl
              floating-card glow-card
            "
          >
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-slate-900 drop-shadow-[0_0_14px_rgba(255,255,255,0.7)] mb-3">
              On the bright side
            </h2>

            <h3 className="text-lg sm:text-2xl md:text-3xl text-cyan-700 font-semibold mb-4">
              God continues to bless us. Really, He does.
            </h3>

            <div
              className={`space-y-3 ${
                isMobile ? "text-base" : "text-sm sm:text-base md:text-lg"
              } text-slate-800 leading-relaxed text-left`}
            >
              <p>
                Sometimes, God will bless us through the kindness and generosity
                of His people. You might be here today because of that kindness.
              </p>

              <p>
                But most of all, I want you to know that God is real. And He
                loves you more than you can imagine.
              </p>

              <p>
                He may even use a friend, a stranger, or a small moment like
                this just to get your attention.
              </p>
            </div>
          </div>

          <div
            className="
              w-full md:w-70
              px-6 py-6
              rounded-2xl
              bg-white/75
              border border-white/90
              backdrop-blur-2xl
              shadow-[0_0_45px_rgba(255,255,255,0.6)]
              text-left
            "
          >
            <h3 className="text-2xl sm:text-3xl font-semibold text-slate-900 mb-4">
              So, why are you here?
            </h3>

            <ul
              className={`list-disc pl-4 space-y-2 ${
                isMobile ? "text-lg" : "text-base sm:text-lg"
              } text-slate-800`}
            >
              <li>
                Maybe to be reminded that God is still with you, and it’s going
                to be OK.
              </li>
              <li>
                Maybe to encourage you to keep being faithful right where you
                are.
              </li>
              <li>
                Or maybe God just wants to introduce Himself to you for the very
                first time.
              </li>
            </ul>

            <h4
              className={`mt-6 font-semibold text-cyan-700 text-center ${
                isMobile ? "text-2xl" : "text-xl sm:text-2xl md:text-3xl"
              }`}
            >
              Either way, He wants you to know: He is here, and He loves you.
            </h4>
          </div>
        </div>
      </div>
    </section>
  );
}