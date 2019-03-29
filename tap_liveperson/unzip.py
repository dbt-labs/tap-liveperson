
import zlib
import json

def unzip(blob):
    extracted = zlib.decompress(blob, 16+zlib.MAX_WBITS)
    decoded = extracted.decode('utf-8')
    res = []
    for line in decoded.split("\n"):
        if len(line.strip()) > 0:
            res.append(json.loads(line))
    return res
