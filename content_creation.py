# ------------------- Stand-Alone Content Creation -------------------
import streamlit as st
import os
import re
import datetime
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------

def get_api_key(provider: str) -> str | None:
    """Return the provider-specific key from the current browser session."""
    provider = provider.upper()
    if provider == "OPENAI":
        return st.session_state.get("openai_api_key")
    if provider == "ANTHROPIC":
        return st.session_state.get("anthropic_api_key")
    return None


def generate_content(prompt, service, model, temperature, max_tokens):
    """Direct REST calls to OpenAI or Anthropic."""
    import requests

    if service == "openai":
        api_key = get_api_key("OPENAI")
        if not api_key:
            st.error("Please supply an OpenAI key in **Settings**.")
            return None

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        if r.status_code != 200:
            st.error(f"OpenAI error {r.status_code}: {r.text}")
            return None
        return r.json()["choices"][0]["message"]["content"]

    elif service == "anthropic":
        api_key = get_api_key("ANTHROPIC")
        if not api_key:
            st.error("Please supply an Anthropic key in **Settings**.")
            return None

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=60,
        )
        if r.status_code != 200:
            st.error(f"Anthropic error {r.status_code}: {r.text}")
            return None
        return r.json()["content"][0]["text"]

    else:
        st.error("Unknown service (choose OpenAI or Anthropic).")
        return None


def generate_image(prompt, size):
    """DALL‑E 3 image generation (needs OpenAI key)."""
    import requests

    api_key = get_api_key("OPENAI")
    if not api_key:
        st.error("Please supply an OpenAI key in **Settings**.")
        return None

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "size": size,
        "quality": "standard",
        "n": 1,
    }

    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers=headers,
        json=payload,
        timeout=60,
    )
    if r.status_code != 200:
        st.error(f"DALL‑E error {r.status_code}: {r.text}")
        return None
    url = r.json()["data"][0]["url"]
    return requests.get(url, timeout=60).content

# -------------------------------------------------------------------
# UI
# -------------------------------------------------------------------

def content_creation_ui() -> None:
    st.set_page_config(page_title="Content Creation", layout="centered")

    st.markdown(
        """
        <style>
          .block-container{max-width:1100px;padding-top:3rem;}
          .stVerticalBlock{gap:0.75rem !important;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # session defaults
    st.session_state.setdefault("service", "OpenAI")
    st.session_state.setdefault("model", "gpt-3.5-turbo")
    st.session_state.setdefault("temperature", 0.7)
    st.session_state.setdefault("max_tokens", 500)

    tab_gen, tab_img, tab_set = st.tabs([
        "Generate Content", "Generate Image", "Settings"
    ])

    # ---------------------------------------------------------------
    # Tab 1 – Generate Content
    # ---------------------------------------------------------------
    with tab_gen:
        st.subheader("AI Content Generator")
        prompt = st.text_area("Prompt", height=150)

        cols = st.columns(2)
        with cols[0]:
            service = st.selectbox(
                "Service",
                ["OpenAI", "Anthropic"],
                index=["OpenAI", "Anthropic"].index(st.session_state.service),
            )
        with cols[1]:
            if service == "OpenAI":
                models = ["gpt-4o", "gpt-4-turbo-preview", "gpt-3.5-turbo"]
            else:
                models = [
                    "claude-3-opus-20240229",
                    "claude-3-sonnet-20240229",
                    "claude-3-haiku-20240307",
                ]
            model = st.selectbox(
                "Model",
                models,
                index=models.index(st.session_state.model)
                if st.session_state.model in models
                else 0,
            )

        with st.expander("Advanced"):
            st.session_state.temperature = st.slider(
                "Temperature", 0.0, 1.0, st.session_state.temperature, 0.1
            )
            st.session_state.max_tokens = st.slider(
                "Max tokens", 50, 4000, st.session_state.max_tokens, 50
            )

        if st.button("Generate Content", type="primary", disabled=not prompt):
            with st.spinner("Thinking…"):
                text = generate_content(
                    prompt,
                    service.lower(),
                    model,
                    st.session_state.temperature,
                    st.session_state.max_tokens,
                )
            if text:
                st.text_area("Result", text, height=300)

    # ---------------------------------------------------------------
    # Tab 2 – Generate Image
    # ---------------------------------------------------------------
    with tab_img:
        st.subheader("AI Image Generator (OpenAI DALL‑E 3)")
        img_prompt = st.text_area("Image prompt", height=100)
        size = st.selectbox("Size", ["1024x1024", "1024x1792", "1792x1024"])
        if st.button("Generate Image", type="primary", disabled=not img_prompt):
            with st.spinner("Painting…"):
                img_blob = generate_image(img_prompt, size)
            if img_blob:
                st.image(img_blob)

    # ---------------------------------------------------------------
    # Tab 3 – Settings
    # ---------------------------------------------------------------
    with tab_set:
        st.subheader("API Keys (browser session only)")
        openai = st.text_input(
            "OpenAI API Key", type="password", value=st.session_state.get("openai_api_key", "")
        )
        if openai:
            st.session_state.openai_api_key = openai
            st.success("OpenAI key set ✔️")

        anthropic = st.text_input(
            "Anthropic API Key", type="password", value=st.session_state.get("anthropic_api_key", "")
        )
        if anthropic:
            st.session_state.anthropic_api_key = anthropic
            st.success("Anthropic key set ✔️")

        st.divider()
        st.subheader("Defaults")
        st.session_state.service = st.selectbox(
            "Default service",
            ["OpenAI", "Anthropic"],
            index=["OpenAI", "Anthropic"].index(st.session_state.service),
        )
        st.session_state.model = st.text_input("Default model", st.session_state.model)


# -------------------------------------------------------------------
if __name__ == "__main__":
    content_creation_ui()
