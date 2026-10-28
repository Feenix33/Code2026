import time
import tkinter

class VoiceAnnouncerEngine:
    def __init__(self):
        # Initialize the native, built-in Tcl interpreter wrapper
        self.tcl = tkinter.Tcl()
        
        # Default internal state
        self.pitch = "Medium"
        self.gender = "Neutral"
        self.speed = 1.0
        
        # Bind the Python methods to Tcl commands
        self.tcl.createcommand("voice_config", self.cmd_voice_config)
        self.tcl.createcommand("read_passage", self.cmd_read_passage)
        self.tcl.createcommand("countdown", self.cmd_countdown)

    def cmd_voice_config(self, pitch, gender, speed):
        """Changes the voice attributes."""
        self.pitch = pitch
        self.gender = gender
        self.speed = float(speed)
        print(f"🔧 [Config Updated] Pitch: {self.pitch} | Gender: {self.gender} | Speed: {self.speed}x")

    def cmd_read_passage(self, text_block):
        """Processes and reads a potentially large, multiline text passage."""
        print(f"\n🎙️ [Announcer - {self.gender} Voice (Pitch: {self.pitch}, Speed: {self.speed}x)]:")
        
        # Clean up whitespace and process line by line
        lines = [line.strip() for line in text_block.splitlines() if line.strip()]
        for line in lines:
            print(f"   💬 \"{line}\"")
            time.sleep(0.4 / self.speed) # Simulate speech pacing
        print("🛑 [End of Passage]\n")

    def cmd_countdown(self, start_num):
        """Executes a loop-driven countdown sequence."""
        seconds = int(start_num)
        print(f"⏱️ Starting countdown from {seconds}...")
        for i in range(seconds, 0, -1):
            print(f"   🚨 {i}...")
            time.sleep(0.3)
        print("🎉 Blast off!\n")

    def run_script(self, script_text):
        """Executes a raw Tcl script string directly."""
        try:
            self.tcl.eval(script_text)
        except tkinter.TclError as e:
            print(f"❌ Script Error: {e}")

# ==========================================
# 📜 Tcl Script Definition
# ==========================================
tcl_script = """
# 1. Configure the initial voice engine state
voice_config High Female 1.2

# 2. Pass a massive multi-line text block using Tcl curly brace wrappers
read_passage {
    ⚠️ ATTENTION ALL PERSONNEL ⚠️
    Automated sequence breakdown initiated.
    Please clear the launch pad immediately.
    Secure all loose equipment and report to bunker bravo.
}

# 3. Change configurations on the fly
voice_config Deep Male 0.8

# 4. Read a second short text chunk
read_passage {
    T-Minus ten seconds to system evaluation.
}

# 5. Use native Tcl control loops to execute a countdown
set remaining 5
while {$remaining > 0} {
    countdown $remaining
    set remaining [expr {$remaining - 1}]
}

# 6. Final announcement
voice_config Medium Neutral 1.0
read_passage {
    Sequence complete.
}
"""

# ==========================================
# 🚀 Execution
# ==========================================
if __name__ == "__main__":
    engine = VoiceAnnouncerEngine()
    engine.run_script(tcl_script)

