"""Set overlap flags from filled outlines, including intermediate weights."""
import pathops
from fontTools.pens.recordingPen import DecomposingRecordingPen

def set_overlap_flags(font):
    glyf=font['glyf']
    pending=set()
    for name in font.getGlyphOrder():
        glyph=glyf[name]
        if glyph.isComposite():
            for component in glyph.components: component.flags &= ~0x0400
            pending.add(name)
        elif glyph.numberOfContours>0:
            for i in range(len(glyph.flags)): glyph.flags[i] &= ~0x40
            if glyph.numberOfContours>1: pending.add(name)
    overlaps=set()
    for weight in range(100,901,10):
        glyphset=font.getGlyphSet(location={'wght':weight})
        for name in sorted(pending-overlaps):
            record=DecomposingRecordingPen(glyphset)
            glyphset[name].draw(record)
            path=pathops.Path();record.replay(path.getPen())
            path.fillType=pathops.FillType.WINDING
            nonzero=pathops.simplify(path)
            path.fillType=pathops.FillType.EVEN_ODD
            evenodd=pathops.simplify(path)
            difference=pathops.op(nonzero,evenodd,pathops.PathOp.XOR)
            if difference.area>0.01: overlaps.add(name)
    for name in overlaps:
        glyph=glyf[name]
        if glyph.isComposite():glyph.components[0].flags |= 0x0400
        else:glyph.flags[0] |= 0x40
