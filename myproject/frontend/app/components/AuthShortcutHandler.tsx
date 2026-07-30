"use client";

import { useClerk } from "@clerk/nextjs";
import { useEffect } from "react";

export default function AuthShortcutHandler() {
  const { openSignIn } = useClerk();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "j") {
        e.preventDefault();
        openSignIn();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [openSignIn]);

  return null;
}