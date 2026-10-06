import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

// Note: no <StrictMode> on purpose. In development it runs effects twice, and
// we don't want to risk anything that would ask a slow local model twice.
createRoot(document.getElementById("root")!).render(<App />);
