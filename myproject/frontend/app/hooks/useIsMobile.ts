"use client";

/* === HOOK: Detect mobile screens === */
import { useEffect, useRef, useState } from "react";

export default function useIsMobile(breakpoint: number = 768): boolean {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkSize = () => {
      if (typeof window !== "undefined") {
        setIsMobile(window.innerWidth < breakpoint);
      }
    };

    checkSize(); // run once on mount
    window.addEventListener("resize", checkSize);

    return () => window.removeEventListener("resize", checkSize);
  }, [breakpoint]);

  return isMobile;
}