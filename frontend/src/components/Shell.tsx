import type { ReactNode } from "react";
import { Contours } from "./Contours";

/** The sheet of paper every screen is drawn on. Phone-down mode becomes the night chart. */
export function Shell({ children, dim = false }: { children: ReactNode; dim?: boolean }) {
  return (
    <div className={dim ? "shell shell--dim" : "shell"}>
      <Contours />
      <div className="neatline" aria-hidden="true" />
      <main className="content">{children}</main>
      {!dim && (
        <footer className="credit">
          Made by <strong>Noorin Sakhi</strong> &middot; Hacktoberfest 2026 &middot; MIT licence
        </footer>
      )}
    </div>
  );
}
