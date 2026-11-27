# CareCall — Voice AI Doctor Appointment Assistant

Assignment scaffold based on **SDE Intern – Round 1 Assignment**.

## Included
- FastAPI REST backend with SQLite, mock doctors and appointment slots
- Appointment availability, booking and cancellation endpoints
- React dashboard with doctors, slot picker, appointment list, search and demo transcript
- Pipecat voice pipeline scaffold using ElevenLabs STT/TTS and Gemini

> Important: The dashboard's call button is currently a demo state and the transcript input is a manual test control. The Pipecat pipeline is scaffolded but the WebRTC signaling + LLM function-call callbacks must be wired for a genuine browser voice call. Do not present the demo call button as a fully connected live voice agent.

## 1. Requirements
- Python 3.11+
- Node.js 18+
- Gemini API key
- ElevenLabs API key and voice ID

## 2. Run backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in API keys in .env
uvicorn main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

## 3. Run frontend
Open another terminal:
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

## 4. Test API
- `GET /api/doctors`
- `GET /api/availability?doctor_id=1&date=2026-12-01`
- `GET /api/appointments`
- `POST /api/book` JSON: `{"phone":"9876543210","doctor_id":1,"date":"2026-12-01","time":"09:30"}`
- `POST /api/cancel` JSON: `{"phone":"9876543210"}`

## 5. Finish the real Pipecat voice connection
Use the official Pipecat SmallWebRTC quickstart matching your installed version:
https://github.com/pipecat-ai/docs/blob/main/pipecat/get-started/quickstart.mdx

Use the Small WebRTC transport and connect the browser with the official Pipecat client SDK / Small WebRTC transport. Configure:
1. Browser mic audio -> WebRTC -> Pipecat transport
2. ElevenLabs STT -> context -> Gemini LLM -> ElevenLabs TTS -> WebRTC audio
3. Register function-call tools in the LLM context:
   - `check_doctor_availability(doctor_id, date)` -> GET `/api/availability`
   - `book_appointment(phone, doctor_id, date, time)` -> POST `/api/book`
   - `cancel_appointment(phone)` -> POST `/api/cancel`
4. Use the returned API JSON as the tool result. Do not tell the caller success until the API returns success.
5. Send user/assistant transcript events to the dashboard and refresh appointments after tool execution.

Function tool descriptions should tell the agent to collect the spoken phone number, read it back digit-by-digit and get explicit confirmation before booking or cancelling. Never use browser account details, login, OTP or caller-ID as identity.

## 6. Before submitting
- Test availability, booking and cancellation with Swagger
- Confirm booking rejects an already-booked slot
- Confirm cancellation only affects the matching spoken phone number
- Add real Pipecat WebRTC signaling and tools (not the demo button)
- Record a short booking video and write your own pipeline description
- Add a `.env.example`; never commit `.env` or API keys

## Architecture
```text
Browser microphone
    ↓ WebRTC
Pipecat transport
    ↓
ElevenLabs STT → Gemini + appointment tools → ElevenLabs TTS
    ↓ WebRTC audio + transcript events
Browser dashboard

Dashboard → FastAPI → SQLite
                 ├─ doctors / slots
                 └─ appointments
```
