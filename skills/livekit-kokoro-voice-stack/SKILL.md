---
name: livekit-kokoro-voice-stack
description: Zero-token real-time voice architecture (LiveKit WebRTC + Silero VAD v5 + faster-whisper + Kokoro-82M + F5-TTS Voice Cloning + Wav2Vec2-GOP Pronunciation Coach) for all 18 SYNDICATE agents and Kira's Live Psychotherapy & English Coaching modes.
---

# SYNDICATE Skill: LiveKit + Silero VAD v5 + Kokoro-82M Zero-Token Voice Stack

## 1. Архітектура Голосового Конвеєра ($0.00 / хв)
Замість комерційних Realtime API ($0.06–$0.24 за хвилину розмови), SYNDICATE використовує власний локальний стек на сервері **Contabo Cloud VPS 12** (12 vCPU, 48 GB RAM, 400 GB SSD):

1. **Транспорт (`LiveKit Server` WebRTC):** двосторонній аудіоканал із затримкою `<100 мс` (порти `7880/tcp`, `7881/tcp`, `7882/udp`).
2. **Детектор мовлення та Barge-in (`Silero VAD v5`):**
   - Працює локально на CPU (~50 МБ RAM, `<30 мс` на фрейм).
   - Відсікає тишу та фоновий шум (економія 100% ресурсів у паузах).
   - **Barge-In (перебивання):** щойно Андрій починає говорити, Silero VAD миттєво зупиняє відтворення голосу агента.
3. **Розпізнавання мовлення (`faster-whisper large-v3-int8`):** локальний STT на CPU (~2.5 ГБ RAM, 2–3x швидше реального часу, висока точність для української та англійської мов).
4. **Синтез мовлення (`Kokoro-82M` ONNX/FastAPI):**
   - 82 мільйони параметрів, якість рівня ElevenLabs, споживає ~500 МБ RAM, працює у 5–10 разів швидше реального часу без GPU.
   - **Математичний блендинг голосів (`Voice Blending`):** змішування векторів стилів (наприклад, `0.70*af_heart + 0.30*af_nicole` для Кіри, `0.65*af_bella + 0.35*bf_emma` для Єви) забезпечує 18 унікальних тембрів для всіх директорів холдингу.
5. **Zero-Shot Клонування Голосів (`F5-TTS` / `XTTS-v2`):**
   - Клонування будь-якого голосу за 15–30 секундним референсним `.wav` файлом у `/data/voices/clones/`, включаючи **Цифровий Двійник Андрія (`andrii_twin`)**.

## 2. Спеціальні Режими Кіри (Поверх 8 — Академія та Психотерапія)
- **Live-Психотерапія (`live_therapy_session`):**
  - Емпатичний тембр `Kokoro-82M` зі швидкістю `0.90x–0.94x`.
  - **100% приватність:** голос обробляється виключно всередині контейнера на сервері SYNDICATE.
- **Фонетичний Тренер Англійської Мови (`PronunciationCoach` / `english_pronunciation_assessment`):**
  - Вирішує проблему автокорекції Whisper (який виправляє неправильну вимову у правильно написані слова).
  - Використовує акустичний аналіз фонем (`Wav2Vec2-GOP` / IPA) для виявлення типових помилок (`/θ/` та `/ð/` проти `/s/`, `/z/`, `/w/` проти `/v/`, довжина голосних `/ɪ/` проти `/iː/`) та `Gemini 2.5 Flash Native Audio` для оцінки інтонації.
