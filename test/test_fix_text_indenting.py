from fing.fix_text_indenting import fix_text_indenting


def test_fix_text_indenting():
    assert EXPECTED == fix_text_indenting(LINES)


LINES = """
<?xml version='1.0' encoding='utf-8'?>
<svg viewBox="0 0 2970 3735" xmlns="http://www.w3.org/2000/svg">
  <svg class="body" x="30" y="30" width="2850" height="3615">
    <svg class="page" x="30" y="30" width="2910" height="3675">
      <text x="80" y="45">D♯/E♭1</text>
      <svg>
        <text font-size="60" x="1000" y="100">
        Fingering chart for the Baroque family of recorders
  </text>
        <text font-size="30" x="1000" y="170">
      Copyleft <tspan fill="transparent">©</tspan> 2026. No rights reserved.
  </text>
        <use href="#copyleft" x="232" y="48" transform="scale(3, 3)" />
      </svg>
"""

EXPECTED = """
<?xml version='1.0' encoding='utf-8'?>
<svg viewBox="0 0 2970 3735" xmlns="http://www.w3.org/2000/svg">
  <svg class="body" x="30" y="30" width="2850" height="3615">
    <svg class="page" x="30" y="30" width="2910" height="3675">
      <text x="80" y="45">D♯/E♭1</text>
      <svg>
        <text font-size="60" x="1000" y="100">
          Fingering chart for the Baroque family of recorders
        </text>
        <text font-size="30" x="1000" y="170">
          Copyleft <tspan fill="transparent">©</tspan> 2026. No rights reserved.
        </text>
        <use href="#copyleft" x="232" y="48" transform="scale(3, 3)" />
      </svg>
"""
