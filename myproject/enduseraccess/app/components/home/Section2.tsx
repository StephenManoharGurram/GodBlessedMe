"use client";

import {RefObject , useRef, useState ,useEffect} from "react";
import useIsMobile from "@/app/hooks/useIsMobile";

type Section2Props = {
  sectionRef: RefObject<HTMLElement | null>;
  sectionVisible: boolean;
  isMobile: boolean;
  pos: { x: number; y: number };
};

export default function Section2(){
  const sectionRef = useRef<HTMLElement | null>(null);
  const [sectionVisible, setSectionVisible] = useState(false);
  const isMobile = useIsMobile(768);
  const pos = { x: 50, y: 50 };
  useEffect(() => {
    const el = sectionRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        const inView = entry.isIntersecting && entry.intersectionRatio > 0.25;
        setSectionVisible(inView);
      },
      { threshold: [0.2, 0.4] }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return <section
      id="section2"
      ref={sectionRef}
      className="
        relative w-full
        -mt-px
        py-20 sm:py-24 md:py-28
        px-4 sm:px-6 md:px-10
        bg-linear-to-b
        from-[#0b3d2e]
        via-[#1a2420]
        to-[#3a2a1d]
      "
    >
      <div
        className="absolute inset-0 pointer-events-none transition-all duration-200"
        style={{
          background: `radial-gradient(circle at ${pos.x}% ${pos.y}%, rgba(255,244,219,0.18), transparent 70%)`,
        }}
      />

      <div className="relative max-w-4xl mx-auto text-center space-y-14">
        <div className="space-y-3 fade-item">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white drop-shadow-[0_0_18px_rgba(0,0,0,0.85)]">
            Let&apos;s face it, life can wear on us
          </h2>
          <div className="h-1 w-24 mx-auto rounded-full bg-amber-300/80 shadow-[0_0_16px_rgba(252,211,77,0.8)]" />
        </div>

        <div
          className="
            bg-white/12 border border-white/25
            rounded-3xl backdrop-blur-xl
            px-6 sm:px-8 md:px-14
            py-10 sm:py-12 md:py-14
            shadow-[0_24px_80px_rgba(0,0,0,0.7)]
            max-w-3xl mx-auto
            fade-item
          "
        >
          <div className="grid grid-cols-3 sm:flex sm:justify-center gap-6 sm:gap-10 md:gap-14 mb-10">
            <div className="flex justify-center">
              <div
                className={`
                  w-16 h-16 sm:w-20 sm:h-20 rounded-full
                  bg-linear-to-br from-amber-300 to-yellow-400
                  flex items-center justify-center text-slate-900
                  shadow-xl cursor-pointer
                  transition-transform duration-300 ease-out
                  hover:-translate-y-2 hover:scale-110 active:scale-95
                  ${sectionVisible ? "icon-slide icon-slide-1" : ""}
                `}
              >
                <svg
                  viewBox="0 0 24 24"
                  className="w-8 h-8 sm:w-10 sm:h-10"
                  aria-hidden="true"
                >
                  <path
                    d="M12 3a9 9 0 0 0-9 9h2a7 7 0 1 1 14 0h2a9 9 0 0 0-9-9zm-.9 10.2 1.8-6 1.7.5-1.8 6a1 1 0 0 1-1.9-.5z"
                    fill="currentColor"
                  />
                </svg>
              </div>
            </div>

            <div className="flex justify-center">
              <div
                className={`
                  w-16 h-16 sm:w-20 sm:h-20 rounded-full
                  bg-linear-to-br from-amber-300 to-orange-400
                  flex items-center justify-center text-slate-900
                  shadow-xl cursor-pointer
                  transition-transform duration-300 ease-out
                  hover:-translate-y-2 hover:scale-110 active:scale-95
                  ${sectionVisible ? "icon-slide icon-slide-2" : ""}
                `}
              >
                <svg
                  viewBox="0 0 24 24"
                  className="w-8 h-8 sm:w-10 sm:h-10"
                  aria-hidden="true"
                >
                  <path
                    d="M9 3h6a2 2 0 0 1 2 2v2h3v4H4V7h3V5a2 2 0 0 1 2-2zm6 4V5h-6v2h6zm-11 6h16v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-7z"
                    fill="currentColor"
                  />
                </svg>
              </div>
            </div>

            <div className="flex justify-center">
              <div
                className={`
                  w-16 h-16 sm:w-20 sm:h-20 rounded-full
                  bg-linear-to-br from-amber-200 to-rose-300
                  flex items-center justify-center text-slate-900
                  shadow-xl cursor-pointer
                  transition-transform duration-300 ease-out
                  hover:-translate-y-2 hover:scale-110 active:scale-95
                  ${sectionVisible ? "icon-slide icon-slide-3" : ""}
                `}
              >
                <svg
                  viewBox="0 0 24 24"
                  className="w-8 h-8 sm:w-10 sm:h-10"
                  aria-hidden="true"
                >
                  <path
                    d="M4 5h16v11H4V5zm6 13h8v2H6v-2h4z"
                    fill="currentColor"
                  />
                </svg>
              </div>
            </div>
          </div>

          <p
            className={`${
              isMobile ? "text-lg" : "text-base sm:text-lg md:text-xl"
            } text-white/92 font-light leading-relaxed max-w-xl mx-auto`}
          >
            The pace can be too fast at times.
            <br />
            The load can get heavy.
            <br />
            <br />
            And sometimes, it feels like the bad news just keeps coming.
          </p>
        </div>
      </div>
    </section>;
}