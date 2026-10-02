"""Read text from a screenshot with the macOS Vision framework (no cloud, no extra install).
Usage: python3 tools/ocr.py <image.png> [regex]   -> prints recognised lines (filtered by regex)
Also used by ptreport.py to read "Item Count : a/b" and "Score : a/b" from Check Results screenshots,
because Packet Tracer's results pane does not expose those labels to the Accessibility API."""
import re, sys
import Quartz, Vision
from Foundation import NSURL

def observations(path, crop=None):
    """[(y, x, text)] in Vision's normalised coordinates (y grows upwards).
    crop = (x0, y0, w, h) as fractions of the image (top-left origin) to OCR only that region."""
    url = NSURL.fileURLWithPath_(path)
    src = Quartz.CGImageSourceCreateWithURL(url, None)
    img = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    if crop:
        W, H = Quartz.CGImageGetWidth(img), Quartz.CGImageGetHeight(img)
        x0, y0, w, h = crop
        img = Quartz.CGImageCreateWithImageInRect(img, Quartz.CGRectMake(x0 * W, y0 * H, w * W, h * H))
    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(img, None)
    handler.performRequests_error_([req], None)
    out = []
    for obs in req.results() or []:
        c = obs.topCandidates_(1)
        if c: out.append((obs.boundingBox().origin.y, obs.boundingBox().origin.x, c[0].string()))
    out.sort(key=lambda t: (-t[0], t[1]))      # top to bottom, left to right
    return out

def lines(path):
    return [t[2] for t in observations(path)]

def _value_right_of(obs, label):
    """The text on the same line to the right of the label (the values are separate boxes)."""
    for y, x, t in obs:
        if t.strip().rstrip(':').strip() == label:
            right = [(x2, t2) for y2, x2, t2 in obs if abs(y2 - y) < 0.012 and x2 > x]
            right.sort()
            joined = ' '.join(t2 for _, t2 in right)
            m = re.search(r'(\d+)\s*/\s*(\d+)', joined)
            if m: return f'{m.group(1)}/{m.group(2)}'
    return None

def totals(path):
    """{'score': 'a/b', 'items': 'c/d', 'completed': bool} from a Check Results screenshot."""
    obs = observations(path)
    txt = ' | '.join(t for _, _, t in obs)
    res = {}
    for crop in (None, (0.78, 0.0, 0.22, 0.3), (0.85, 0.05, 0.15, 0.2)):   # big windows: small text at top right
        o = obs if crop is None else observations(path, crop)
        v = _value_right_of(o, 'Item Count')
        if v and 'items' not in res: res['items'] = v
        v = _value_right_of(o, 'Score')
        if v and 'score' not in res: res['score'] = v
        if 'items' in res: break
    if 'completed the activity' in txt: res['completed'] = True
    if 'did not complete' in txt: res['completed'] = False
    return res

if __name__ == '__main__':
    pat = re.compile(sys.argv[2]) if len(sys.argv) > 2 else None
    for l in lines(sys.argv[1]):
        if pat is None or pat.search(l): print(l)
    print(totals(sys.argv[1]))
