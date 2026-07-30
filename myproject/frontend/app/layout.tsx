import {
  ClerkProvider,
  Show,
  UserButton,
} from "@clerk/nextjs";
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import AuthShortcutHandler from "./components/AuthShortcutHandler";
import LogoTapTrigger from "./components/LogoTapTrigger";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "God Blessed Me",
  description:
    "Drop us a line! Sign up for our email list for updates, promotions, and more.",
  icons: {
    icon: "/logo-og.png",
    shortcut: "/logo-og.png",
    apple: "/logo-og.png",
  },
  openGraph: {
    title: "God Blessed Me",
    description:
      "Drop us a line! Sign up for our email list for updates, promotions, and more.",
    images: [
      {
        url: "/logo-og.png",
        width: 1200,
        height: 630,
        alt: "God Blessed Me logo",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    images: ["/logo-og.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider afterSignOutUrl="/">
      <html lang="en">
        <body
          className={`${geistSans.variable} ${geistMono.variable} antialiased bg-[#0b3d2e] text-white`}
        >
          {/* Desktop: Ctrl+J / Cmd+J → opens Clerk sign-in modal */}
          <AuthShortcutHandler />

          <header className="site-navbar w-full fixed top-0 left-0 right-0 z-40 border-b border-white/10">
            <nav className="w-full px-4 sm:px-6 lg:px-8 py-5 sm:py-6 flex items-center justify-between bg-black/30 backdrop-blur-md">
              <div>
                {/* Mobile: tap logo 7× within 1.5s → opens Clerk sign-in modal */}
                <LogoTapTrigger />
              </div>

              <div className="flex items-center gap-4 sm:gap-6 text-xs sm:text-sm md:text-base ml-auto">
                <Link
                  href="/stories"
                  className="border border-[#F1F3E0] px-5 py-2 rounded-full text-xs sm:text-sm md:text-base bg-white/5 hover:bg-[#F1F3E0] hover:text-[#0b3d2e] transition whitespace-nowrap"
                >
                  Stories
                </Link>

                {/* Sign In / Sign Up buttons hidden */}
                {/* Desktop: Ctrl+J or Cmd+J  |  Mobile: tap logo 7× */}

                <Show when="signed-in">
                  <Link
                    href="/dashboard"
                    className="text-xs sm:text-sm md:text-base text-white/80 hover:text-white transition whitespace-nowrap"
                  >
                    Dashboard
                  </Link>

                  <UserButton
                    appearance={{
                      elements: {
                        avatarBox: "w-8 h-8",
                      },
                    }}
                  />
                </Show>
              </div>
            </nav>
          </header>

          <main className="pt-20">{children}</main>
        </body>
      </html>
    </ClerkProvider>
  );
}