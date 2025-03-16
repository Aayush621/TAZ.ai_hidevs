# TAZ.ai - Your AI-Powered Travel Buddy ✈️

TAZ.ai is an innovative travel planning platform that leverages artificial intelligence to provide end-to-end trip planning solutions. From initial planning to booking transportation, accommodations, and activities, TAZ.ai creates personalized travel experiences with hassle-free itineraries.

---

## 🌟 Features

### Core Functionality
- **Intelligent Trip Planning**: AI-powered travel agent that understands and adapts to your preferences.
- **Complete Itinerary Creation**: Detailed day-by-day planning, including flights, accommodations, and activities.
- **Interactive Chat Interface**: Natural conversation-based travel planning.
- **Real-time Updates**: Dynamic itinerary adjustments and travel recommendations.

### Multi-Device Integration Vision
- **Smartwatch Integration**: Plan your trips hands-free while on the go.
- **VR Experience**: Visualize destinations in immersive 3D environments before booking.
- **Smart Home Integration**: Voice-commanded travel planning through devices like Alexa.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Groq API Key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/TAZ.ai.git
   cd TAZ.ai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory and add:
   ```plaintext
   GROQ_API_KEY=your_groq_api_key
   ```

4. Run the application:
   ```bash
   uvicorn api:app --reload
   ```

---

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **AI/ML**: 
  - LangChain
  - Groq LLM (llama3-70b-8192 model)
  - LangGraph for agent creation
- **Frontend**: HTML5, CSS3, JavaScript
- **API**: RESTful architecture

---

## 📚 API Documentation

### Endpoints

#### `POST /travel/chat`
Start or continue a conversation with the travel agent.

#### `GET /travel/conversations/{conversation_id}`
Retrieve the full conversation history.

#### `DELETE /travel/conversations/{conversation_id}`
Delete a specific conversation.

---

## 🔮 Future Roadmap

### 1️⃣ Device Integration
- Smartwatch apps for real-time travel updates.
- VR integration for immersive destination previews.
- Voice assistant compatibility.

### 2️⃣ Enhanced Features
- Real-time booking integration.
- Multi-language support.
- Personalized travel recommendations.
- Group travel coordination.

### 3️⃣ Platform Expansion
- Mobile applications.
- Browser extensions.
- Integration with major travel platforms.

---

## 📄 License
This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
