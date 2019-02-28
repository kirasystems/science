package main

func overlap(docs map[string]string, gold map[string][]span, pred map[string][]span) float64 {
	tpi, tpu := uint32(0), uint32(0)
	for doc1, doc2 := range docs {
		goldSpans := gold[doc1]
		predSpans := pred[doc2]
		tpi += spanUniqueTP(goldSpans, predSpans)
		tpu += spanUniqueTP(goldSpans, predSpans) + spanFN(goldSpans, predSpans) + spanFP(goldSpans, predSpans)
	}
	return float64(tpi) / float64(tpu)
}

func granularIntersection(gold, pred []span) uint32 {
	inter := uint32(0)
	for _, g := range gold {
		for _, p := range pred {
			if g.overlaps(p) {
				start := max(g.start, p.start)
				end := min(g.end, p.end)
				inter += uint32(end - start)
			}
		}
	}
	return inter
}

func granularUnion(gold, pred []span) uint32 {
	union := uint32(0)
	for _, g := range gold {
		if !anyOverlaps(pred, g) {
			union += uint32(g.end - g.start)
		}
	}
	for _, p := range pred {
		if !anyOverlaps(gold, p) {
			union += uint32(p.end - p.start)
		}
	}
	mergedSpans := []span{}
	for _, g := range gold {
		overlaps := multipleOverlaps(pred, g)
		if len(overlaps) == 0 {
			continue
		}
		for _, o := range overlaps {
			g.start = min(g.start, o.start)
			g.end = max(g.end, o.end)
		}
		mergedSpans = append(mergedSpans, g)
	}
	final := []span{}
	for i, m := range mergedSpans {
		// Already accounted for
		if anyOverlaps(final, m) {
			continue
		}
		// Merge any overlapping spans
		for _, n := range mergedSpans[i+1:] {
			if m.overlaps(n) {
				m.start = min(m.start, n.start)
				m.end = max(m.end, n.end)
			}
		}
		final = append(final, m)
	}
	for _, f := range final {
		union += uint32(f.end - f.start)
	}
	return union
}

func granularOverlap(docs map[string]string, gold map[string][]span, pred map[string][]span) float64 {
	tpi, tpu := uint32(0), uint32(0)
	for doc1, doc2 := range docs {
		goldSpans := gold[doc1]
		predSpans := pred[doc2]
		tpi += granularIntersection(goldSpans, predSpans)
		tpu += granularUnion(goldSpans, predSpans)
	}

	return float64(tpi) / float64(tpu)
}
