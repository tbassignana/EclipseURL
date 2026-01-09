import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: Date | string): string {
  const now = new Date();
  const d = new Date(date);

  // Handle invalid dates
  if (isNaN(d.getTime())) {
    return String(date);
  }

  const diffMs = now.getTime() - d.getTime();
  const isFuture = diffMs < 0;
  const absDiffMs = Math.abs(diffMs);
  const absDiffSeconds = Math.floor(absDiffMs / 1000);
  const absDiffMinutes = Math.floor(absDiffSeconds / 60);
  const absDiffHours = Math.floor(absDiffMinutes / 60);
  const absDiffDays = Math.floor(absDiffHours / 24);

  // Future dates (e.g., expiration)
  if (isFuture) {
    if (absDiffDays >= 7) {
      return d.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    }
    if (absDiffDays >= 1) {
      return `in ${absDiffDays} ${absDiffDays === 1 ? "day" : "days"}`;
    }
    if (absDiffHours >= 1) {
      return `in ${absDiffHours} ${absDiffHours === 1 ? "hour" : "hours"}`;
    }
    return "soon";
  }

  // Past dates
  if (absDiffSeconds < 5) {
    return "just now";
  }
  if (absDiffSeconds < 60) {
    return `${absDiffSeconds} ${absDiffSeconds === 1 ? "second" : "seconds"} ago`;
  }
  if (absDiffMinutes < 60) {
    return `${absDiffMinutes} ${absDiffMinutes === 1 ? "minute" : "minutes"} ago`;
  }
  if (absDiffHours < 24) {
    return `${absDiffHours} ${absDiffHours === 1 ? "hour" : "hours"} ago`;
  }
  if (absDiffDays < 7) {
    return `${absDiffDays} ${absDiffDays === 1 ? "day" : "days"} ago`;
  }

  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatNumber(num: number): string {
  if (num >= 1000000) {
    const value = num / 1000000;
    return (value % 1 === 0 ? value.toString() : value.toFixed(1)) + "M";
  }
  if (num >= 1000) {
    const value = num / 1000;
    return (value % 1 === 0 ? value.toString() : value.toFixed(1)) + "K";
  }
  return num.toString();
}

export function copyToClipboard(text: string): Promise<void> {
  return navigator.clipboard.writeText(text);
}

export function isValidUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}
