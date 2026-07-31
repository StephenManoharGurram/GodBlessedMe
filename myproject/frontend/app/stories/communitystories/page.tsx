"use client";

import { useEffect, useState } from "react";
import { fetchStories, PublicStory } from "@/app/stories/api/storiesApi";

export default function CommunityStories() {
  const [stories, setStories] = useState<PublicStory[]>([]);
  const [loadingStories, setLoadingStories] = useState(true);
  const [fetchError, setFetchError] = useState("");

  async function loadStories() {
    try {
      setLoadingStories(true);
      setFetchError("");
      const data = await fetchStories();
      setStories(data);
    } catch {
      setFetchError("Could not load stories right now.");
    } finally {
      setLoadingStories(false);
    }
  }

  useEffect(() => {
    loadStories();
  }, []);

  return (
    <>
      {/* ── Divider ── */}
      <div className="flex items-center gap-4">
        <div className="h-px flex-1 bg-white/10" />
        <span
          className="uppercase tracking-[0.2em] text-white/30"
          style={{ fontSize: "clamp(0.65rem, 1.2vw, 0.75rem)" }}
        >
          Community
        </span>
        <div className="h-px flex-1 bg-white/10" />
      </div>

      {/* ── Community Stories ── */}
      <section>
        <div className="mb-8 border-b border-white/10 pb-5">
          <h2
            className="font-semibold tracking-tight text-[#F1F3E0]"
            style={{ fontSize: "clamp(1.25rem, 3.5vw, 2rem)" }}
          >
            Community Stories
          </h2>
          <p
            className="mt-1 text-white/50"
            style={{ fontSize: "clamp(0.8rem, 1.6vw, 0.95rem)" }}
          >
            Approved stories from our community.
          </p>
        </div>

        {loadingStories ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="animate-pulse rounded-xl border border-white/10 bg-white/5 p-6"
              >
                <div className="mb-3 h-5 w-2/3 rounded bg-white/10" />
                <div className="mb-4 h-3 w-1/4 rounded bg-white/10" />
                <div className="space-y-2">
                  <div className="h-3 w-full rounded bg-white/10" />
                  <div className="h-3 w-5/6 rounded bg-white/10" />
                  <div className="h-3 w-4/6 rounded bg-white/10" />
                </div>
              </div>
            ))}
          </div>
        ) : fetchError ? (
          <div
            className="rounded-lg border border-red-400/20 bg-red-400/10 px-5 py-4 text-red-300"
            style={{ fontSize: "clamp(0.8rem, 1.5vw, 0.9rem)" }}
          >
            {fetchError}
          </div>
        ) : stories.length === 0 ? (
          <div className="rounded-xl border border-dashed border-white/10 px-8 py-14 text-center">
            <p
              className="text-white/40"
              style={{ fontSize: "clamp(0.8rem, 1.5vw, 0.9rem)" }}
            >
              No approved stories yet.
            </p>
            <p
              className="mt-1 text-white/25"
              style={{ fontSize: "clamp(0.7rem, 1.2vw, 0.8rem)" }}
            >
              Be the first to share yours above.
            </p>
          </div>
        ) : (
          <div className="space-y-5">
            {stories.map((story, index) => (
              <article
                key={story.id}
                className="rounded-xl border border-white/10 bg-white/5 p-7 transition hover:border-white/20 hover:bg-white/[0.07]"
              >
                <div className="mb-1 flex items-start justify-between gap-4">
                  <h3
                    className="font-semibold leading-snug text-[#F1F3E0]"
                    style={{ fontSize: "clamp(1rem, 2.5vw, 1.25rem)" }}
                  >
                    {story.title}
                  </h3>
                  <span
                    className="mt-1 shrink-0 text-white/30"
                    style={{ fontSize: "clamp(0.65rem, 1.2vw, 0.75rem)" }}
                  >
                    #{index + 1}
                  </span>
                </div>
                <p
                  className="mb-4 text-white/40"
                  style={{ fontSize: "clamp(0.7rem, 1.3vw, 0.8rem)" }}
                >
                  By{" "}
                  <span className="font-medium text-white/60">
                    {story.author_name}
                  </span>
                  {" · "}
                  {new Date(story.submitted_at).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </p>
                <p
                  className="whitespace-pre-line leading-relaxed text-white/70"
                  style={{ fontSize: "clamp(0.85rem, 1.6vw, 0.95rem)" }}
                >
                  {story.content}
                </p>
              </article>
            ))}
          </div>
        )}
      </section>
    </>
  );
}