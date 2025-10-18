// frontend/src/App.jsx
import React from "react";
import Chat from "./pages/Chat.jsx";
import Analytics from "./pages/Analytics.jsx";

function Router() {
  const path = window.location.pathname;
  if (path.startsWith("/analytics")) return <Analytics />;
  return <Chat />;
}

export default function App() {
  return <Router />;
}
