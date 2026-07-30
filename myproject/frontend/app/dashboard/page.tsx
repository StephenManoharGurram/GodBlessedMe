"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth, UserButton } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import Link from "next/link";

type StoryStatus = "pending" | "approved" | "denied";
type FilterTab = "all" | StoryStatus;

type Story = {
  id: number;
  title: string;
  author_name: string;
  content: string;
  status: StoryStatus;
  submitted_at: string;
  ip_address?: string;
};

type Toast = { msg: string; type: "success" | "error" };

export default function DashboardPage() {
  const { isLoaded, isSignedIn } = useAuth();
  const router = useRouter();

  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<FilterTab>("pending");
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [toast, setToast] = useState<Toast | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.replace("/sign-in");
    }
  }, [isLoaded, isSignedIn, router]);

  const showToast = useCallback((msg: string, type: Toast["type"]) => {
    setToast({ msg, type });
    window.setTimeout(() => setToast(null), 3500);
  }, []);

  const loadStories = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/dashboard");
      if (!res.ok) throw new Error("Failed to load stories");
      const data: Story[] = await res.json();
      setStories(data);
    } catch {
      showToast("Failed to load stories.", "error");
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    if (isSignedIn) {
      loadStories();
    }
  }, [isSignedIn, loadStories]);

  async function updateStatus(id: number, status: "approved" | "denied") {
    setActionLoading(id);
    try {
      const res = await fetch("/api/dashboard", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, status }),
      });
      if (!res.ok) throw new Error("Failed to update");
      setStories((prev) => prev.map((s) => (s.id === id ? { ...s, status } : s)));
      showToast(status === "approved" ? "Story approved." : "Story denied.", "success");
    } catch {
      showToast("Action failed. Try again.", "error");
    } finally {
      setActionLoading(null);
    }
  }

  async function deleteStory(id: number) {
    const confirmed = window.confirm("Permanently delete this story?");
    if (!confirmed) return;

    setActionLoading(id);
    try {
      const res = await fetch("/api/dashboard", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      if (!res.ok) throw new Error("Failed to delete");
      setStories((prev) => prev.filter((s) => s.id !== id));
      showToast("Story deleted.", "success");
    } catch {
      showToast("Delete failed. Try again.", "error");
    } finally {
      setActionLoading(null);
    }
  }

  const filtered =
    filter === "all" ? stories : stories.filter((story) => story.status === filter);

  const counts: Record<FilterTab, number> = {
    all: stories.length,
    pending: stories.filter((s) => s.status === "pending").length,
    approved: stories.filter((s) => s.status === "approved").length,
    denied: stories.filter((s) => s.status === "denied").length,
  };

  if (!isLoaded || !isSignedIn) {
    return null;
  }

  return (
    <main
      className="min-h-screen text-white"
      style={{
        background:
          "linear-gradient(160deg, #0b3d2e 0%, #092f23 50%, #061e17 100%)",
      }}
    >
      {toast && (
        <div
          className={`fixed top-5 right-5 z-50 rounded-xl px-5 py-3 text-sm font-medium shadow-xl ${
            toast.type === "success"
              ? "bg-[#F1F3E0] text-[#0b3d2e]"
              : "bg-red-500/90 text-white"
          }`}
        >
          {toast.msg}
        </div>
      )}

      <header className="sticky top-0 z-40 border-b border-white/10 bg-black/30 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="text-xs uppercase tracking-[0.25em] text-white/40 transition hover:text-white/70"
            >
              ← Home
            </Link>
            <span className="text-white/20">|</span>
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-white/40">
                God Blessed Me
              </p>
              <h1 className="text-base font-semibold leading-tight text-[#F1F3E0]">
                Stories Dashboard
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={loadStories}
              className="rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-xs text-white/60 transition hover:bg-white/10 hover:text-white"
            >
              Refresh
            </button>
            <UserButton
              appearance={{
                elements: {
                  avatarBox: "w-9 h-9",
                },
              }}
            />
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-6xl space-y-8 px-4 py-10">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {(["all", "pending", "approved", "denied"] as FilterTab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={`rounded-xl border px-5 py-4 text-left transition ${
                filter === tab
                  ? "border-[#F1F3E0]/40 bg-[#F1F3E0]/10 shadow-lg"
                  : "border-white/10 bg-white/5 hover:bg-white/[0.07]"
              }`}
            >
              <p
                className={`text-2xl font-bold ${
                  tab === "pending"
                    ? "text-yellow-300"
                    : tab === "approved"
                    ? "text-green-300"
                    : tab === "denied"
                    ? "text-red-300"
                    : "text-[#F1F3E0]"
                }`}
              >
                {counts[tab]}
              </p>
              <p className="mt-1 text-xs uppercase tracking-widest text-white/40">
                {tab}
              </p>
            </button>
          ))}
        </div>

        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-36 animate-pulse rounded-xl border border-white/10 bg-white/5 p-6"
              />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="rounded-xl border border-dashed border-white/10 px-8 py-16 text-center">
            <p className="text-sm text-white/40">
              No {filter === "all" ? "" : filter} stories yet.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filtered.map((story) => (
              <article
                key={story.id}
                className="rounded-xl border border-white/10 bg-white/5 transition hover:border-white/20"
              >
                <div className="flex items-start justify-between gap-4 p-6 pb-4">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-3">
                      <h2 className="truncate text-base font-semibold leading-snug text-[#F1F3E0]">
                        {story.title}
                      </h2>
                      <span
                        className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          story.status === "approved"
                            ? "bg-green-500/20 text-green-300"
                            : story.status === "denied"
                            ? "bg-red-500/20 text-red-300"
                            : "bg-yellow-500/20 text-yellow-300"
                        }`}
                      >
                        {story.status}
                      </span>
                    </div>
                    <p className="mt-1.5 text-xs text-white/40">
                      By{" "}
                      <span className="font-medium text-white/60">
                        {story.author_name}
                      </span>
                      {" · "}
                      {new Date(story.submitted_at).toLocaleDateString("en-US", {
                        year: "numeric",
                        month: "short",
                        day: "numeric",
                      })}
                      {story.ip_address ? (
                        <span className="ml-2 font-mono text-white/25">
                          IP: {story.ip_address}
                        </span>
                      ) : null}
                    </p>
                  </div>
                </div>

                <div className="px-6">
                  <p
                    className={`whitespace-pre-line text-sm leading-relaxed text-white/60 ${
                      expandedId === story.id ? "" : "line-clamp-3"
                    }`}
                  >
                    {story.content}
                  </p>
                  {story.content.length > 200 ? (
                    <button
                      onClick={() =>
                        setExpandedId(expandedId === story.id ? null : story.id)
                      }
                      className="mb-2 mt-1.5 text-xs text-white/30 transition hover:text-white/60"
                    >
                      {expandedId === story.id ? "Show less" : "Read more"}
                    </button>
                  ) : null}
                </div>

                <div className="mt-3 flex items-center gap-3 border-t border-white/5 px-6 pb-5 pt-3">
                  {story.status !== "approved" ? (
                    <button
                      onClick={() => updateStatus(story.id, "approved")}
                      disabled={actionLoading === story.id}
                      className="rounded-full border border-green-400/40 bg-green-400/10 px-4 py-1.5 text-xs text-green-300 transition hover:bg-green-400/20 disabled:opacity-50"
                    >
                      {actionLoading === story.id ? "..." : "Approve"}
                    </button>
                  ) : null}

                  {story.status !== "denied" ? (
                    <button
                      onClick={() => updateStatus(story.id, "denied")}
                      disabled={actionLoading === story.id}
                      className="rounded-full border border-red-400/40 bg-red-400/10 px-4 py-1.5 text-xs text-red-300 transition hover:bg-red-400/20 disabled:opacity-50"
                    >
                      {actionLoading === story.id ? "..." : "Deny"}
                    </button>
                  ) : null}

                  <button
                    onClick={() => deleteStory(story.id)}
                    disabled={actionLoading === story.id}
                    className="ml-auto rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-xs text-white/40 transition hover:border-red-400/30 hover:bg-red-500/10 hover:text-red-300 disabled:opacity-50"
                  >
                    {actionLoading === story.id ? "..." : "Delete"}
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}