"""
File: tts_engine.py
Purpose: Multilingual Text-to-Speech (TTS) engine for rural farmers supporting Marathi (mr),
         Hindi (hi), and English (en). Converts recommendation summaries into voice audio (using gTTS
         or graceful static localized speech templates with base64 audio fallback).
Inputs:  mandi_name (str), crop_name (str), net_price (float), language (str: 'en'|'hi'|'mr')
Outputs: dict with text, spoken_script, language, audio_base64 (if generated), and audio_url
Usage:   from services.tts_engine import generate_speech
         speech_data = generate_speech("Amravati", "Cotton", 7134.0, language="mr")
"""

import io
import base64

# Localized clean crop name extractors
def clean_crop_name(raw_name, lang="en"):
    """Extracts language-appropriate crop name."""
    if not raw_name:
        return "Crop"
    if "(" in raw_name and ")" in raw_name:
        parts = raw_name.split("(")
        eng = parts[0].strip()
        regional = parts[1].replace(")", "").strip()
        if lang == "en":
            return eng
        elif lang == "hi":
            # Hindi is usually the first part of regional (e.g. 'कपास / कापूस' -> 'कपास')
            subparts = regional.split("/")
            return subparts[0].strip()
        elif lang == "mr":
            subparts = regional.split("/")
            return subparts[-1].strip()
    return raw_name

def clean_mandi_name(raw_name, lang="en"):
    """Extracts language-appropriate mandi name."""
    if not raw_name:
        return "Mandi"
    if "(" in raw_name and ")" in raw_name:
        parts = raw_name.split("(")
        eng = parts[0].strip()
        regional = parts[1].replace(")", "").strip()
        if lang == "en":
            return eng
        return regional
    return raw_name

def get_speech_script(mandi_name, crop_name, net_price, language="en"):
    """Generates natural language script in chosen language."""
    clean_crop = clean_crop_name(crop_name, language)
    clean_mandi = clean_mandi_name(mandi_name, language)
    price_val = int(round(float(net_price)))

    if language == "mr":
        script = f"तुमच्या {clean_crop}साठी सर्वात उत्तम मंडी {clean_mandi} आहे. येथे सर्व वाहतूक आणि खर्च वजा करून निव्वळ नफा {price_val} रुपये प्रति क्विंटल मिळेल."
    elif language == "hi":
        script = f"आपकी {clean_crop} के लिए सबसे अच्छी मंडी {clean_mandi} है। यहाँ सभी परिवहन और खर्चे काटकर शुद्ध भाव {price_val} रुपये प्रति क्विंटल मिलेगा।"
    else:
        script = f"The best mandi for your {clean_crop} is {clean_mandi}, with a net price of {price_val} rupees per quintal after deducting all transport and mandi costs."

    return script

def generate_speech(mandi_name, crop_name, net_price, language="en"):
    """
    Synthesizes speech script into audio.

    Parameters:
        mandi_name (str): Name of winning mandi
        crop_name (str): Name of crop
        net_price (float): Realized net price in INR
        language (str): Language code ('en', 'hi', 'mr')

    Returns:
        dict: Audio metadata, localized text script, and base64 audio data
    """
    lang_code = language.lower()
    if lang_code not in ("en", "hi", "mr"):
        lang_code = "en"

    # Map language codes to gTTS supported codes
    gtts_lang = {
        "en": "en",
        "hi": "hi",
        "mr": "mr"
    }.get(lang_code, "en")

    script = get_speech_script(mandi_name, crop_name, net_price, lang_code)
    audio_base64 = None
    audio_format = "mp3"
    tts_engine_used = "none"

    # Attempt online gTTS synthesis
    try:
        from gtts import gTTS
        fp = io.BytesIO()
        tts = gTTS(text=script, lang=gtts_lang, slow=False)
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_base64 = base64.b64encode(fp.read()).decode("utf-8")
        tts_engine_used = "gTTS"
    except Exception as e:
        # Fallback gracefully if gTTS or network is unavailable
        tts_engine_used = f"browser_tts_fallback ({str(e)[:30]})"

    return {
        "status": "success",
        "language": lang_code,
        "script": script,
        "tts_engine": tts_engine_used,
        "audio_base64": audio_base64,
        "audio_mime": f"audio/{audio_format}" if audio_base64 else None
    }

if __name__ == "__main__":
    test_res = generate_speech("Amravati (अमरावती)", "Cotton (कपास / कापूस)", 7134, language="mr")
    print(f"TTS generated for Marathi:\n{test_res['script']}")
