import React from "react";

export default function MessageBubble({ role, text }) {
  if (role === "user") return <div className="chat-bubble">{text}</div>;
  return <div className="assistant-note">{text}</div>;
}
