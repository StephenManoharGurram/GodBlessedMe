const API_BASE = "/api";

export type PublicStory = {
  id: number;
  title: string;
  content: string;
  author_name: string;
  submitted_at: string;
};

export type StorySubmitPayload = {
  title: string;
  content: string;
  author_name: string;
};

export async function fetchStories(): Promise<PublicStory[]> {
  const res = await fetch(`${API_BASE}/stories/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch stories.");
  }

  return res.json();
}

export async function submitStory(
  data: StorySubmitPayload
): Promise<{ message: string }> {
  const res = await fetch(`${API_BASE}/stories/submit/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  const result = await res.json();

  if (!res.ok) {
    throw new Error(result?.message || "Failed to submit story.");
  }

  return result;
}