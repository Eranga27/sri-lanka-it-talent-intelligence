"use client";

import { useEffect, useRef } from "react";

interface Props {
  value: number;
  suffix?: string;
  className?: string;
}

/**
 * Animates a number counting up to `value`.
 * Respects prefers-reduced-motion — skips animation if user prefers it.
 */
export function CountUp({ value, suffix = "", className = "" }: Props) {
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) {
      ref.current.textContent = value.toLocaleString() + suffix;
      return;
    }

    const duration = 1200;
    const start = performance.now();
    const startVal = 0;

    function step(now: number) {
      if (!ref.current) return;
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(startVal + (value - startVal) * eased);
      ref.current.textContent = current.toLocaleString() + suffix;
      if (progress < 1) requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
  }, [value, suffix]);

  return (
    <span ref={ref} className={className} aria-live="polite">
      0{suffix}
    </span>
  );
}
