package main

import (
	"encoding/csv"
	"io"
	"log"
	"os"
	"sort"
	"strconv"
	"strings"
)

type span struct {
	start uint64
	end   uint64
}

func (s *span) overlaps(o span) bool {
	return !(s.end <= o.start || s.start >= o.end)
}

func parseCsv(filename string) map[string]map[string][]span {
	ret := map[string]map[string][]span{}
	file, err := os.Open(filename)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Fatal(err)
		}
		if len(record) != 4 {
			log.Fatalln("Record of wrong length", record)
		}
		doc := record[0]
		field := strings.Trim(record[1], " ")
		start, _ := strconv.ParseUint(record[2], 10, 32)
		end, _ := strconv.ParseUint(record[3], 10, 32)
		if fieldMap, ok := ret[field]; ok {
			if _, ok := fieldMap[doc]; ok {
				fieldMap[doc] = append(fieldMap[doc], span{start, end})
			} else {
				fieldMap[doc] = []span{span{start, end}}
			}
		} else {
			ret[field] = map[string][]span{}
			fieldMap = ret[field]
			fieldMap[doc] = []span{span{start, end}}
		}

	}
	return ret
}

func anyOverlaps(a []span, b span) bool {
	for _, s := range a {
		if s.overlaps(b) {
			return true
		}
	}
	return false
}

func multipleOverlaps(a []span, b span) (ret []span) {
	for _, s := range a {
		if s.overlaps(b) {
			ret = append(ret, s)
		}
	}
	return ret
}

func alreadySeen(a, b []span) bool {
	for _, s1 := range a {
		for _, s2 := range b {
			if s1 == s2 {
				return true
			}
		}
	}
	return false
}

func mergeSeen(seen, new []span) []span {
	ret := seen
	for _, s1 := range new {
		distinct := true
		for _, s2 := range seen {
			if s1 == s2 {
				distinct = false
				break
			}
		}
		if distinct {
			ret = append(ret, s1)
		}
	}
	return ret
}
func spanUniqueTP(gold []span, pred []span) uint32 {
	count := uint32(0)
	seen := []span{}
	for _, s := range gold {
		newlySeen := multipleOverlaps(pred, s)
		if !alreadySeen(newlySeen, seen) && len(newlySeen) != 0 {
			count++
		}
		seen = mergeSeen(seen, newlySeen)
	}
	return count
}

func spanTP(gold []span, pred []span) uint32 {
	count := uint32(0)
	for _, s := range gold {
		if anyOverlaps(pred, s) {
			count++
		}
	}
	return count
}

func spanFN(gold []span, pred []span) uint32 {
	count := uint32(0)
	for _, s := range gold {
		if !anyOverlaps(pred, s) {
			count++
		}
	}
	return count
}

func spanFP(gold []span, pred []span) uint32 {
	count := uint32(0)
	for _, s := range pred {
		if !anyOverlaps(gold, s) {
			count++
		}
	}
	return count
}

func spanTN(gold []span, pred []span) uint32 {
	mergedSpans := []span{}
	for _, g := range gold {
		for _, p := range pred {
			if g.overlaps(p) {
				g.start = min(g.start, p.start)
				g.end = max(g.end, p.end)
			}
		}
		mergedSpans = append(mergedSpans, g)
	}
	predUn := []span{}
	for _, p := range pred {
		if !anyOverlaps(mergedSpans, p) {
			predUn = append(predUn, p)
		}
	}
	mergedSpans = append(mergedSpans, predUn...)
	sort.Slice(mergedSpans, func(i, j int) bool {
		return mergedSpans[i].start < mergedSpans[j].start || (mergedSpans[i].start == mergedSpans[j].start && mergedSpans[i].end <= mergedSpans[j].end)
	})
	finalSpans := []span{}
	for i, s := range mergedSpans {
		for _, ms := range mergedSpans[i+1:] {
			if s.overlaps(ms) {
				s = mergeSpans(s, ms)
			}
		}
		finalSpans = append(finalSpans, s)
	}
	return uint32(len(finalSpans) + 1)
}

func min(a, b uint64) uint64 {
	if a < b {
		return a
	}
	return b
}
func max(a, b uint64) uint64 {
	if a > b {
		return a
	}
	return b
}
func mergeSpans(g, p span) span {
	g.start = min(g.start, p.start)
	g.end = max(g.end, p.end)
	return g
}

func spanCompare(a, b span) bool {
	return a.start < b.start || (a.start == b.start && a.end <= b.end)
}
