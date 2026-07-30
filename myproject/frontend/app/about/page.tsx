// app/about/page.tsx

export default function AboutPage() {
  return (
    <div className="min-h-[calc(100vh-5rem)] bg-[#F1F3E0] text-[#778873] flex items-center">
      <section className="max-w-4xl mx-auto px-6 py-16 space-y-8">
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-semibold tracking-tight">
          About This Space
        </h1>

        <p className="text-lg leading-relaxed">
          This website is a quiet corner of the internet, built to help you slow
          down and remember the moments when God blessed you. It&apos;s not about
          noise, likes, or trends — it&apos;s about gratitude, reflection, and
          simple goodness.
        </p>

        <p className="text-lg leading-relaxed">
          My friend shares messages, stories, and small reminders here. Each
          one is meant to nudge you gently toward kindness: toward God, toward
          others, and toward yourself.
        </p>

        <p className="text-lg leading-relaxed">
          Over time, this space will grow with reflections, blessings, and
          stories — but the design will stay simple, quiet, and honest. Just
          like the moments it celebrates.
        </p>
      </section>
    </div>
  );
}
