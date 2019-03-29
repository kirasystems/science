package main

func recall(docs map[string]string, gold map[string][]span, pred map[string][]span) float64 {
	agrees := uint32(0)
	total := uint32(0)
	for doc1, doc2 := range docs {
		goldSpans := gold[doc1]
		predSpans := pred[doc2]
		agrees += spanTP(goldSpans, predSpans)
		total += uint32(len(goldSpans))
	}
	return float64(agrees) / float64(total)
}

func precision(docs map[string]string, gold map[string][]span, pred map[string][]span) float64 {
	tp := uint32(0)
	fp := uint32(0)
	for doc1, doc2 := range docs {
		goldSpans := gold[doc1]
		predSpans := pred[doc2]
		tp += spanTP(goldSpans, predSpans)
		fp += spanFP(goldSpans, predSpans)
	}
	return float64(tp) / float64(tp+fp)
}
