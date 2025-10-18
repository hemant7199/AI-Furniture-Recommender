# app/services/genai.py
from typing import Optional
import textwrap

try:
    from transformers import pipeline
except Exception:
    pipeline = None

_SYSTEM_STYLE = (
    "Write a concise, vivid, benefit-focused product blurb (45–65 words). "
    "Prefer active voice. Start with a hook. Mention material/color if relevant. "
    "End with a short use-case. No hashtags. No URLs."
)

class DescriptionGenerator:
    def __init__(self, model_name: str = "gpt2"):
        self.model_name = model_name
        self.pipe = None
        if pipeline is not None:
            try:
                self.pipe = pipeline(
                    "text-generation",
                    model=model_name,
                    trust_remote_code=True
                )
            except Exception:
                self.pipe = None

    def generate(self, prompt: str) -> str:
        prompt = f"{_SYSTEM_STYLE}\n\nContext:\n{prompt}\n\nBlurb:"
        if self.pipe is None:
            # graceful fallback
            return ("Clean, modern design built for everyday comfort. Durable materials, easy to maintain, "
                    "and sized to fit most rooms. A versatile piece that elevates your space without fuss.")
        try:
            out = self.pipe(
                prompt,
                max_new_tokens=70,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1,
            )[0]["generated_text"]
            # return the new tail after "Blurb:"
            tail = out.split("Blurb:", 1)[-1].strip()
            return textwrap.shorten(tail, width=420, placeholder="…")
        except Exception:
            return ("Comfort-forward build with a refined silhouette and practical finish. "
                    "Pairs well with modern and minimalist décor for daily use.")
