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
                                """


with open(html_file, 'w', encoding='utf-8') as f:
    f.write(new_content)
