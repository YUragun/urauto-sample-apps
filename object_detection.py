# ------------------- Stand‑Alone Object Detection -------------------
import streamlit as st
import os
import numpy as np
import logging
import json
import base64
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------

def get_api_key(provider: str) -> str | None:
    """Return the provider‑specific key from session_state or env‑vars."""
    provider = provider.upper()
    if provider == "OPENAI":
        return st.session_state.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
    if provider == "ANTHROPIC":
        return st.session_state.get("anthropic_api_key") or os.getenv("ANTHROPIC_API_KEY")
    return None


def _pil_to_b64_jpeg(im: Image.Image) -> str:
    if im.mode == "RGBA":
        im = im.convert("RGB")
    buf = BytesIO()
    im.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()


def detect_objects_with_openai(image_array, api_key=None):
    """Call OpenAI Vision and return narrative + JSON (if parsable)."""
    import requests

    api_key = api_key or get_api_key("OPENAI")
    if not api_key:
        st.error("Please supply an OpenAI API key in **Settings**.")
        return None, None

    b64_img = _pil_to_b64_jpeg(Image.fromarray(image_array))
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analyze this image and identify all objects. "
                            "Provide a narrative plus JSON as "
                            '{"detected_objects":[{"label":"","description":"","confidence":""}]}'
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"},
                    },
                ],
            }
        ],
        "max_tokens": 500,
    }

    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    if resp.status_code != 200:
        st.error(f"OpenAI error {resp.status_code}: {resp.text}")
        return None, None

    txt = resp.json()["choices"][0]["message"]["content"]
    try:
        js_start, js_end = txt.find("{"), txt.rfind("}") + 1
        js = json.loads(txt[js_start:js_end]) if js_start >= 0 else None
    except Exception:
        js = None
    return txt, js


def detect_objects_with_anthropic(image_array, api_key=None):
    """Call Claude 3 Vision and return narrative + JSON (if parsable)."""
    import requests

    api_key = api_key or get_api_key("ANTHROPIC")
    if not api_key:
        st.error("Please supply an Anthropic API key in **Settings**.")
        return None, None

    b64_img = _pil_to_b64_jpeg(Image.fromarray(image_array))
    payload = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analyze this image and identify all objects. "
                            "Provide a narrative plus JSON as "
                            '{"detected_objects":[{"label":"","description":"","confidence":""}]}'
                        ),
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": b64_img,
                        },
                    },
                ],
            }
        ],
    }

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    if resp.status_code != 200:
        st.error(f"Anthropic error {resp.status_code}: {resp.text}")
        return None, None

    txt = resp.json()["content"][0]["text"]
    try:
        js_start, js_end = txt.find("{"), txt.rfind("}") + 1
        js = json.loads(txt[js_start:js_end]) if js_start >= 0 else None
    except Exception:
        js = None
    return txt, js

# -------------------------------------------------------------------
# UI
# -------------------------------------------------------------------

def object_detection_ui() -> None:
    # Keep centred layout but allow extra width
    st.set_page_config(page_title="Object Detection", layout="centered")

    # Gentle whitespace tuning
    st.markdown(
        """
        <style>
          /* widen the main block a bit beyond Streamlit default (≈700px) */
          .block-container{max-width:1100px;padding-top:3rem;}
          /* tighten vertical spacing */
          .stVerticalBlock{gap:0.75rem !important;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Session defaults
    st.session_state.setdefault("detection_model", "OpenAI Vision")
    st.session_state.setdefault("box_color", "Green")

    tab_detect, tab_settings = st.tabs(["Object Detection", "Settings"])

    # ---------------------------------------------------------------
    # Tab 1 – Object Detection
    # ---------------------------------------------------------------
    with tab_detect:
        col_left, col_right = st.columns([3, 4], gap="medium")  # a touch wider than 2/3

        # ---------- left controls ----------
        with col_left:
            st.subheader("Image Source")
            source = st.radio("Choose", ["Upload", "URL", "Camera"], horizontal=True)

            img_np = None
            if source == "Upload":
                up = st.file_uploader("Upload image", ["jpg", "jpeg", "png"], label_visibility="collapsed")
                if up:
                    img_np = np.array(Image.open(up))
            elif source == "URL":
                url = st.text_input("Image URL")
                if url:
                    try:
                        import requests
                        img_np = np.array(Image.open(BytesIO(requests.get(url).content)))
                    except Exception as e:
                        st.error(f"Failed to load: {e}")
            else:
                cap = st.camera_input("Take a picture")
                if cap:
                    img_np = np.array(Image.open(cap))

            run_btn = st.button("Detect Objects", type="primary")

        # ---------- right preview/results ----------
        with col_right:
            if img_np is not None:
                st.image(img_np, caption="Input image", use_column_width=True, clamp=True)

            if run_btn and img_np is not None:
                with st.spinner("Analyzing…"):
                    if st.session_state.detection_model == "OpenAI Vision":
                        txt, js = detect_objects_with_openai(img_np)
                    else:
                        txt, js = detect_objects_with_anthropic(img_np)

                if txt:
                    st.markdown("#### Analysis")
                    st.write(txt)

                if js and "detected_objects" in js:
                    st.markdown("#### Detected Objects")
                    try:
                        import pandas as pd
                        st.dataframe(pd.DataFrame(js["detected_objects"]), hide_index=True)
                    except ImportError:
                        for o in js["detected_objects"]:
                            st.write(f"- **{o['label']}**: {o['description']} ({o['confidence']})")

    # ---------------------------------------------------------------
    # Tab 2 – Settings
    # ---------------------------------------------------------------
    with tab_settings:
        st.subheader("Detection Settings")
        st.session_state.detection_model = st.selectbox(
            "Select model",
            ["OpenAI Vision", "Anthropic Claude Vision"],
            index=["OpenAI Vision", "Anthropic Claude Vision"].index(
                st.session_state.detection_model
            ),
        )

        st.divider()
        st.subheader("API Keys (browser‑session only)")
        openai_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.get("openai_api_key", ""))
        if openai_key:
            st.session_state["openai_api_key"] = openai_key
        anthropic_key = st.text_input("Anthropic API Key", type="password", value=st.session_state.get("anthropic_api_key", ""))
        if anthropic_key:
            st.session_state["anthropic_api_key"] = anthropic_key
        if st.session_state.get("openai_api_key"):
            st.success("OpenAI key set ✔️")
        if st.session_state.get("anthropic_api_key"):
            st.success("Anthropic key set ✔️")

        st.divider()
        st.subheader("Appearance")
        colors = ["Green", "Red", "Blue", "Yellow", "Purple", "Cyan"]
        st.session_state.box_color = st.selectbox("Bounding‑box color", colors, index=colors.index(st.session_state.box_color))
        rgb = {
            "Green": (0, 255, 0), "Red": (255, 0, 0), "Blue": (0, 0, 255),
            "Yellow": (255, 255, 0), "Purple": (128, 0, 128), "Cyan": (0, 255, 255),
        }[st.session_state.box_color]
        st.markdown(f"<div style='width:80px;height:24px;background-color:rgb{rgb};border-radius:4px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------------
if __name__ == "__main__":
    object_detection_ui()
