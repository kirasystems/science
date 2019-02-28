package main

import (
	"math"
)

// This follows the macro-averaged versions of Recall, Precision, and the
// plagdet measure from
// Martin Potthast, Benno Stein, Alberto Barrón-Cedeño, and Paolo Rosso. 2010.
// An evaluation framework for plagiarism detection. In Proceedings of the 23rd
// International Conference on Computational Linguistics: Posters (COLING '10).
// Association for Computational Linguistics, Stroudsburg, PA, USA, 997-1005.

func granularity(gold, pred []span) (float64, float64) {
	detections := 0
	multipleHits := 0
	for _, g := range gold {
		overlaps := multipleOverlaps(pred, g)
		if len(overlaps) > 0 {
			detections++
		}
		multipleHits += len(overlaps)
	}
	return float64(detections), float64(multipleHits)
}

func recallMacro(gold, pred []span) float64 {
	recall := float64(0.0)
	for _, g := range gold {
		length := g.end - g.start
		overlap := uint64(0)
		for _, p := range pred {
			if g.overlaps(p) {
				start := max(p.start, g.start)
				end := min(p.end, g.end)
				overlap += end - start
			}
		}
		recall += float64(overlap) / float64(length)
	}
	return recall
}

func precisionMarco(gold, pred []span) float64 {
	return recallMacro(pred, gold)
}

func plagdet(docs map[string]string, gold map[string][]span, pred map[string][]span) (float64, float64, float64) {
	detections := float64(0.0)
	hits := float64(0.0)
	numGold := 0
	numPred := 0
	recall := float64(0.0)
	precision := float64(0.0)
	for doc1, doc2 := range docs {
		goldSpans := gold[doc1]
		predSpans := pred[doc2]
		newDet, newMulti := granularity(goldSpans, predSpans)
		detections += newDet
		hits += newMulti
		p := recallMacro(predSpans, goldSpans)
		precision += p
		r := recallMacro(goldSpans, predSpans)
		recall += r
		numGold += len(goldSpans)
		numPred += len(predSpans)
	}
	recall /= float64(numGold)
	precision /= float64(numPred)
	gran := hits / detections
	f1 := (2 * recall * precision) / (recall + precision)
	return recall, precision, f1 / math.Log2(1.0+gran)
}
