"use client";

import { useEffect, useRef, useState } from "react";

type UseInViewOptions = {
  threshold?: number | number[];
};

export default function useInView<T extends HTMLElement>({
  threshold = [0.2, 0.4],
}: UseInViewOptions = {}) {
  const ref = useRef<T | null>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        const inView = entry.isIntersecting && entry.intersectionRatio > 0.25;
        setIsVisible(inView);
      },
      { threshold }
    );

    observer.observe(el);

    return () => observer.disconnect();
  }, [threshold]);

  return { ref, isVisible };
}