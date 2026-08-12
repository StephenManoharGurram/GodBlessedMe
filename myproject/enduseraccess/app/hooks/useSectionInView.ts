"use client";

import { RefObject, useEffect, useState } from "react";

type UseSectionInViewOptions = {
  threshold?: number[];
  minRatio?: number;
};

export default function useSectionInView<T extends HTMLElement>(
  ref: RefObject<T | null>,
  options: UseSectionInViewOptions = {}
): boolean {
  const { threshold = [0.2, 0.4], minRatio = 0.25 } = options;
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        const inView =
          entry.isIntersecting && entry.intersectionRatio > minRatio;
        setIsVisible(inView);
      },
      { threshold }
    );

    observer.observe(el);

    return () => {
      observer.disconnect();
    };
  }, [ref, threshold, minRatio]);

  return isVisible;
}