"use client";

import { useClerk } from "@clerk/nextjs";
import Link from "next/link";
import { useRef } from "react";

export default function LogoTapTrigger() {
  const { openSignIn } = useClerk();
  const tapCount = useRef(0);
  const tapTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleTap = () => {
    tapCount.current += 1;

    // Reset the countdown timer on every tap
    if (tapTimer.current) clearTimeout(tapTimer.current);

    if (tapCount.current >= 7) {
      // 🎯 7 taps reached — open auth
      tapCount.current = 0;
      openSignIn();
      return;
    }

    // Auto-reset if the user stops tapping within 1.5s
    tapTimer.current = setTimeout(() => {
      tapCount.current = 0;
    }, 1500);
  };

  return (
    <Link
      href="/"
      onClick={handleTap}
      className="text-sm sm:text-base tracking-[0.25em] uppercase whitespace-nowrap"
    >
      God Blessed Me
    </Link>
  );
}