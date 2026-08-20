import re

html_file = 'index.html'

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# The replacement HTML string
new_html = """                <div class="armory-segments">
                    <div class="armory-top-row">
                        <!-- Left Segment -->
                        <div class="armory-segment">
                            <h3 class="segment-title">Left Hand Gestures (System Controls)</h3>
                            <div class="segment-grid">
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">Make a closed fist with your left hand for more than 0.6 seconds to show the desktop.</div>
                                    <div class="showcase-header"><h3>Minimize Windows (Boss Key)</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HAND</span><div class="visual-placeholder loop-fist"><div class="fist-shape"></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder loop-boss"><div class="mock-windows"><div class="win window-1"></div><div class="win window-2"></div></div><div class="mock-desktop"></div></div></div>
                                    </div>
                                </div>
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">Show an open palm with your left hand for more than 0.6 seconds to restore the windows.</div>
                                    <div class="showcase-header"><h3>Maximize Windows</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HAND</span><div class="visual-placeholder loop-pinch-pinky"><div class="hand-shape-pinky" style="animation: none; transform: none;"></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder loop-boss" style="animation-direction: reverse;"><div class="mock-windows"><div class="win window-1"></div><div class="win window-2"></div></div><div class="mock-desktop"></div></div></div>
                                    </div>
                                </div>
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">Make a "phone" gesture with your left hand (only thumb and pinky up). It saves screenshots to a screenshots directory.</div>
                                    <div class="showcase-header"><h3>Take a Screenshot</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HAND</span><div class="visual-placeholder loop-spiderman"><div class="spiderman-hand"></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder loop-flash"><div class="mock-flash"></div><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="var(--accent-cyan)" stroke-width="1.5" style="width: 24px; height: 24px; position: absolute; z-index: 1;"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" /><circle cx="12" cy="13" r="4" /></svg></div></div>
                                    </div>
                                </div>
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">Make a closed fist with your left thumb pointing straight up.</div>
                                    <div class="showcase-header"><h3>Volume Up</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HAND</span><div class="visual-placeholder loop-pinch-pinky"><div class="hand-shape-pinky" style="transform: rotate(0); animation: none; border-radius: 8px 8px 14px 14px;"><div style="position:absolute;top:-10px;left:5px;width:6px;height:12px;background:var(--accent-yellow);border-radius:2px;"></div></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder loop-vol"><div class="vol-slider-mock"><div class="vol-fill" style="width: 80%; animation: none;"></div></div><span class="vol-label" style="animation: none; color: var(--accent-yellow);">VOL: UP</span></div></div>
                                    </div>
                                </div>
                   
