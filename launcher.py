#!/usr/bin/env python3
"""
Lucy Launcher - Dynamic entry point based on LUCY_MODE

LUCY_MODE values:
- orchestrator: Main coordinator
- assistant: Domain specialist (set LUCY_ASSISTANT to domain)
- voice: Voice interface
- aquarium: Monitoring UI
"""

import os
import sys

LUCY_MODE = os.getenv("LUCY_MODE", "orchestrator")

if LUCY_MODE == "orchestrator":
    print("🎯 Starting Lucy Orchestrator...")
    from lucy_orchestrator import app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

elif LUCY_MODE == "assistant":
    assistant_domain = os.getenv("LUCY_ASSISTANT", "unknown")
    print(f"🤖 Starting Lucy Assistant: {assistant_domain}")
    from assistants.assistant_server import app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

elif LUCY_MODE == "voice":
    print("🎤 Starting Lucy Voice Interface...")
    from voice.voice_server import app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

elif LUCY_MODE == "aquarium":
    print("🐠 Starting Lucy Aquarium...")
    from aquarium.aquarium_server import app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

else:
    print(f"❌ Unknown LUCY_MODE: {LUCY_MODE}")
    sys.exit(1)
