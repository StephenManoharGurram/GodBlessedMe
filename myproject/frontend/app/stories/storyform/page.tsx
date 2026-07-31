"use client";

import { useState } from "react";
import { submitStory } from "@/app/stories/api/storiesApi";

type FormState = {
  title: string;
  content: string;
  author_name: string;
};

const initialForm: FormState = {
  title: "",
  content: "",
  author_name: "",
};

export default function StoryForm() {
  const [form, setForm] = useState<FormState>(initialForm);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"success" | "error">("success");

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSubmitting(true);
    setMessage("");
    try {
      const result = await submitStory(form);
      setMessage(result.message || "Your story has been submitted for review.");
      setMessageType("success");
      setForm(initialForm);
    } catch {
      setMessage("Something went wrong while submitting your story.");
      setMessageType("error");
    } finally {
      setSubmitting(false);
    }
  }

  function handleChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  return (
    <section>
      <div className="mb-8 border-b border-white/10 pb-5">
        <p
          className="uppercase tracking-[0.2em] text-white/40"
          style={{ fontSize: "clamp(0.65rem, 1.2vw, 0.75rem)" }}
        >
          Add a Story
        </p>
        <h2
          className="mt-1 font-semibold tracking-tight text-[#F1F3E0]"
          style={{ fontSize: "clamp(1.25rem, 3.5vw, 2rem)" }}
        >
          Submit Your Story
        </h2>
        <p
          className="mt-1 text-white/50"
          style={{ fontSize: "clamp(0.8rem, 1.6vw, 0.95rem)" }}
        >
          Your story will appear in the community section once approved.
        </p>
      </div>

      {message && (
        <div
          className={`mb-6 rounded-lg border px-5 py-4 ${
            messageType === "success"
              ? "border-[#F1F3E0]/20 bg-[#F1F3E0]/10 text-[#F1F3E0]"
              : "border-red-400/20 bg-red-400/10 text-red-300"
          }`}
          style={{ fontSize: "clamp(0.8rem, 1.5vw, 0.9rem)" }}
        >
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="grid gap-5 sm:grid-cols-2">
          <div>
            <label
              htmlFor="author_name"
              className="mb-2 block font-medium text-white/70"
              style={{ fontSize: "clamp(0.8rem, 1.5vw, 0.9rem)" }}
            >
              Your Name
            </label>
            <input
              id="author_name"
              name="author_name"
              value={form.author_name}
              onChange={handleChange}
              required
              placeholder="e.g. Jane Doe"
              style={{ fontSize: "clamp(0.8rem, 1.5vw, 0.95rem)" }}
              className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-white/30 outline-none transition focus:border-[#F1F3E0]/50 focus:bg-white/10"
            />
          </div>

          <div>
            <label
              htmlFor="title"
              className="mb-2 block font-medium text-white/70"
              style={{ fontSize: "clamp(0.8rem, 1.5vw, 0.9rem)" }}
            >
              Story Title
            </label>
            <input
              id="title"
              name="title"
              value={form.title}
              onChange={handleChange}
              required
              placeholder="Give your story a title"
              style={{ fontSize: "clamp(0.8rem, 1.5vw, 0.95rem)" }}
              className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-white/30 outline-none transition focus:border-[#F1F3E0]/50 focus:bg-white/10"
            />
          </div>
        </div>

        <div>
          <label
            htmlFor="content"
            className="mb-2 block font-medium text-white/70"
            style={{ fontSize: "clamp(0.8rem, 1.5vw, 0.9rem)" }}
          >
            Your Story
          </label>
          <textarea
            id="content"
            name="content"
            value={form.content}
            onChange={handleChange}
            required
            rows={10}
            placeholder="Write your story here..."
            style={{ fontSize: "clamp(0.8rem, 1.5vw, 0.95rem)" }}
            className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-white/30 outline-none transition focus:border-[#F1F3E0]/50 focus:bg-white/10 leading-relaxed"
          />
        </div>

        <button
          type="submit"
          disabled={submitting}
          style={{ fontSize: "clamp(0.8rem, 1.5vw, 0.9rem)" }}
          className="rounded-full border border-[#F1F3E0] bg-white/5 px-8 py-3 text-[#F1F3E0] transition hover:bg-[#F1F3E0] hover:text-[#1e2d4f] disabled:opacity-50"
        >
          {submitting ? "Submitting…" : "Submit Story"}
        </button>
      </form>
    </section>
  );
}