package main

func kappa(docs map[string]string, gold map[string][]span, pred map[string][]span) float64 {
	tp := uint32(0)
	fp := uint32(0)
	fn := uint32(0)
	tn := uint32(0)
	for doc1, doc2 := range docs {
		goldSpans := gold[doc1]
		predSpans := pred[doc2]
		tpt := spanUniqueTP(goldSpans, predSpans)
		fpt := spanFP(goldSpans, predSpans)
		fnt := spanFN(goldSpans, predSpans)
		tp += tpt
		fp += fpt
		fn += fnt
		tn += 1 + tpt + fpt + fnt
	}
	pa := float64(tp+tn) / float64(tp+tn+fp+fn)
	denom := float64((tp + fp + fn + tn) * (tp + fp + fn + tn))
	pe := float64((tp+fp)*(tp+fn)+(tn+fp)*(tn+fn)) / denom
	return (pa - pe) / (1 - pe + 0.000001)
}
