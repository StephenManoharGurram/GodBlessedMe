import { NextResponse } from "next/server";

const BACKEND = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

export async function GET() {
  try {
    const res = await fetch(`${BACKEND}/api/stories/`, {
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });

    const data = await res.text();

    return new NextResponse(data, {
      status: res.status,
      headers: {
        "Content-Type": res.headers.get("Content-Type") ?? "application/json",
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        detail: "Failed to fetch stories",
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}