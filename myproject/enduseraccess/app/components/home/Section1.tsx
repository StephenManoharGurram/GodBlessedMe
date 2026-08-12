"use client";

import { useEffect, useRef, useState } from "react";
import useIsMobile from "@/app/hooks/useIsMobile";

export default function section1(){
    const [scrollProgress, setScrollProgress] = useState(0);
    const videoRef = useRef<HTMLVideoElement | null>(null);
    const isMobile = useIsMobile(768);

  useEffect(() => {
    const handleScroll = () => {
      const viewportHeight = window.innerHeight || 1;
      const progress = Math.min(
        Math.max(window.scrollY / viewportHeight, 0),
        1
      );
      setScrollProgress(progress);
    };

    window.addEventListener("scroll", handleScroll);
    handleScroll();

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    video.muted = true;

    const playPromise = video.play();
    if (playPromise && typeof playPromise.then === "function") {
      playPromise
        .then(() => video.removeAttribute("controls"))
        .catch(() => video.removeAttribute("controls"));
    } else {
      video.removeAttribute("controls");
    }
  }, [isMobile]);

  return <section id="section1">
      {/* === SECTION 1 === */}
      <section
        id="section1"
        className="
          relative w-full
          min-h-dvh sm:min-h-screen
          overflow-hidden
          opacity-0 animate-fadeIn
          bg-[#020617]
        "
      >
        <div
          className="absolute inset-0 z-0"
          style={{
            opacity: 1 - scrollProgress * 0.85,
            transform: `scale(${1 + scrollProgress * 0.08})`,
            transition: "opacity 0.1s linear, transform 0.1s linear",
          }}
        >
         <video
            className="hero-video absolute inset-0 w-full h-full object-cover"
            src="/home-bg.mp4"
            autoPlay
            loop
            muted
            playsInline
            controls={false}
            preload="auto"
            aria-hidden="true"
          />

          {/* slightly lighter overlay on mobile so the river shows more */}
          <div className="absolute inset-0 bg-black/10 sm:bg-black/20" />
        </div>

        {/* HERO CARD – positioned higher, shorter & wider on mobile, no scrolling */}
        <div
          className={`absolute inset-0 z-30 flex flex-col items-center text-center px-4 ${
            isMobile ? "justify-start pt-16" : "justify-center pt-0"
          }`}
        >
          <div
            className={`
              mx-auto
              rounded-2xl 
              bg-white/6 sm:bg-white/10 backdrop-blur-xl 
              border border-white/25 sm:border-white/30 
              shadow-xl 
              text-center
              floating-card glow-card
              ${
                isMobile
                  ? "w-[90vw] max-w-md p-4"
                  : "w-auto max-w-xl lg:max-w-2xl p-6 md:p-8"
              }
            `}
          >
            <h1 className="text-3xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white drop-shadow-[0_0_18px_rgba(255,255,255,0.6)]">
              God Blessed Me
            </h1>

            {/* MAIN HERO TEXT – bigger on mobile, but still compact */}
            <p
              className={`mt-4 font-light leading-relaxed text-white/95 drop-shadow-[0_0_12px_rgba(0,0,0,0.8)] ${
                isMobile ? "text-lg" : "text-base sm:text-xl md:text-2xl"
              }`}
            >
              If you found this website, I have to ask…
              <br className="hidden sm:block" />
              Did God bless you somehow this week?
            </p>

            <p
              className={`mt-3 text-white/90 leading-relaxed drop-shadow-[0_0_12px_rgba(0,0,0,0.8)] ${
                isMobile ? "text-base" : "text-sm sm:text-lg md:text-xl"
              }`}
            >
              If so, go tell somebody about it,
              <br className="hidden sm:block" /> and then find a way to bless
              somebody else.
              <br />
              Kindness. Goodness. Joy. It’s your turn.
            </p>
          </div>
        </div>

        {/* scroll hint */}
        <div className="absolute bottom-6 left-0 right-0 z-30 flex flex-col items-center">
          <span className="text-[0.65rem] sm:text-xs tracking-[0.3em] uppercase text-white/70">
            Scroll
          </span>
          <span className="mt-2 text-xl sm:text-2xl text-white/90 animate-bounce">
            ⌄
          </span>
        </div>

        {/* Bridge into green tones of section 2 – shorter on mobile so river is visible */}
        <div className="pointer-events-none absolute bottom-0 left-0 w-full h-16 sm:h-32 bg-linear-to-b from-transparent via-[#020617]/60 to-[#0b3d2e] z-20" />
      </section>
    </section>
}