import StoryForm from "@/app/components/stories/storyform/page";
import CommunityStories from "@/app/components/stories/communitystories/page";

export default function StoriesPage() {
  return (
    <main
      className="min-h-screen text-white"
      style={{
        background: "linear-gradient(135deg, #1e2d4f 0%, #1a2744 50%, #0f1b36 100%)",
      }}
    >
      {/* ── Page Header ── */}
      <header
        className="border-b border-white/10 px-6 text-center"
        style={{ padding: "clamp(2.5rem, 8vw, 5rem) 1.5rem" }}
      >
        <p
          className="mb-3 uppercase tracking-[0.25em] text-white/40"
          style={{ fontSize: "clamp(0.65rem, 1.2vw, 0.8rem)" }}
        >
          Stories
        </p>
        <h1
          className="mx-auto max-w-2xl font-semibold leading-tight tracking-tight text-[#F1F3E0]"
          style={{ fontSize: "clamp(1.8rem, 5vw, 3.25rem)" }}
        >
          Share Your Story
        </h1>
        <p
          className="mx-auto mt-4 max-w-xl text-white/60"
          style={{ fontSize: "clamp(0.85rem, 1.8vw, 1.05rem)" }}
        >
          Every voice matters. Submit your story for review and read what the
          community has shared.
        </p>
      </header>

      <div
        className="mx-auto w-full max-w-3xl space-y-16"
        style={{ padding: "clamp(2.5rem, 6vw, 4rem) clamp(1rem, 4vw, 2rem)" }}
      >
        {/* ── Submit a Story ── */}
        <StoryForm />

        {/* ── Community Stories ── */}
        <CommunityStories />
      </div>
    </main>
  );
}