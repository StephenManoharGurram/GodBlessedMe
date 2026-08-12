"use client";

import { useEffect } from "react";

export default function useHideNavbar(shouldHide: boolean) {
  useEffect(() => {
    if (shouldHide) {
      document.body.classList.add("hide-navbar");
    } else {
      document.body.classList.remove("hide-navbar");
    }

    return () => {
      document.body.classList.remove("hide-navbar");
    };
  }, [shouldHide]);
}