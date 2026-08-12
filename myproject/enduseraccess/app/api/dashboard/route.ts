import { auth, currentUser } from "@clerk/nextjs/server";
import { NextRequest, NextResponse } from "next/server";

const BACKEND = (process.env.BACKEND_URL ?? "http://127.0.0.1:8000").replace(/\/+$/, "");
const SECRET = process.env.DASHBOARD_SECRET ?? "";

async function djangoFetch(path: string, options: RequestInit = {}) {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;

  const res = await fetch(`${BACKEND}${normalizedPath}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Dashboard-Secret": SECRET,
      ...(options.headers ?? {}),
    },
    cache: "no-store",
    redirect: "manual",
  });

  if (res.status >= 300 && res.status < 400) {
    const location = res.headers.get("location");
    return NextResponse.json(
      {
        error: "Backend redirect detected",
        status: res.status,
        location,
        requestedUrl: `${BACKEND}${normalizedPath}`,
      },
      { status: 502 }
    );
  }

  return res;
}

async function requireAdmin() {
  const { userId } = await auth();

  if (!userId) {
    return {
      error: NextResponse.json({ error: "Unauthorized" }, { status: 401 }),
    };
  }

  const user = await currentUser();
  const role = (user?.publicMetadata?.role ?? user?.privateMetadata?.role) as string | undefined;

  if (role !== "admin") {
    return {
      error: NextResponse.json({ error: "Forbidden" }, { status: 403 }),
    };
  }

  return { userId };
}

export async function GET() {
  const authResult = await requireAdmin();
  if ("error" in authResult) return authResult.error;

  try {
    const res = await djangoFetch("/api/stories/admin/");
    if (res instanceof NextResponse) return res;

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
        error: "Failed to load dashboard data",
        detail: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}

export async function PATCH(req: NextRequest) {
  const authResult = await requireAdmin();
  if ("error" in authResult) return authResult.error;

  try {
    const body = await req.json();
    const id = body?.id;
    const status = body?.status;

    if (!id || !status) {
      return NextResponse.json(
        { error: "Missing id or status" },
        { status: 400 }
      );
    }

    const res = await djangoFetch(`/api/stories/admin/${id}/`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
    if (res instanceof NextResponse) return res;

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
        error: "Failed to update story",
        detail: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}

export async function DELETE(req: NextRequest) {
  const authResult = await requireAdmin();
  if ("error" in authResult) return authResult.error;

  try {
    const body = await req.json();
    const id = body?.id;

    if (!id) {
      return NextResponse.json(
        { error: "Missing id" },
        { status: 400 }
      );
    }

    const res = await djangoFetch(`/api/stories/admin/${id}/`, {
      method: "DELETE",
    });
    if (res instanceof NextResponse) return res;

    if (!res.ok && res.status !== 204) {
      const data = await res.text();
      return new NextResponse(data, {
        status: res.status,
        headers: {
          "Content-Type": res.headers.get("Content-Type") ?? "application/json",
        },
      });
    }

    return new NextResponse(null, { status: res.status });
  } catch (error) {
    return NextResponse.json(
      {
        error: "Failed to delete story",
        detail: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}