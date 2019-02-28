package main

import (
	"bufio"
	"fmt"
	"io"
	"log"
	"math"
	"os"
	"strings"

	"gonum.org/v1/gonum/stat"
)

type mv struct {
	m float64
	v float64
}

func parseDocList(filename string) map[string]string {
	ret := map[string]string{}
	file, err := os.Open(filename)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	reader := bufio.NewReader(file)
	line, _, err := reader.ReadLine()
	for {

		if err == io.EOF {
			break
		}
		splits := strings.Split(string(line), "\t")
		ret[splits[0]] = splits[1]
		line, _, err = reader.ReadLine()
	}
	return ret
}

func computeMeanStdDev(formatter string, vals []float64) {
	mean, stdev := stat.MeanStdDev(vals, nil)
	fmt.Printf("%.02f (%.02f) %s ", mean, stdev, formatter)
}

func computeFixedEffects(formatter string, vals []mv) {
	totalVar := 0.0
	d := 0.0
	for _, val := range vals {
		totalVar += (1.0 / val.v)
		d += val.m * (1.0 / val.v)
	}
	d /= totalVar
	se := math.Sqrt(1.0 / totalVar)
	fmt.Printf("%.02f (%.02f) %s ", d, se, formatter)
}
func main() {
	docListFile := os.Args[1]
	dir := os.Args[2]
	fields := []string{"Change of Control", "Assignment", "Most Favoured Nation", "Exclusivity", "Indemnity"}
	// Use fields from the command line instead of default
	if len(os.Args) > 3 {
		fields = make([]string, len(os.Args)-3)
		for i := range fields {
			fields[i] = os.Args[3+i]
		}
	}
	docList := parseDocList(docListFile)

	annotators := []string{"gold", "ann1", "ann2", "ann3", "ann4", "ann5", "ann6", "ann7", "ann8", "ann9"}
	quality := map[string]string{"gold": "g", "ann1": "h", "ann2": "h", "ann3": "l", "ann5": "l", "ann6": "h", "ann4": "h",
		"ann9": "l", "ann7": "l", "ann8": "l"}
	granOverlap := map[string][]float64{"gl": []float64{}, "gh": []float64{}, "lh": []float64{}, "hl": []float64{}, "hh": []float64{}, "ll": []float64{}}
	genOverlap := map[string][]float64{}
	recalls := map[string][]float64{}
	precisions := map[string][]float64{}
	kappas := map[string][]float64{}
	gRecalls := map[string][]float64{}
	gPrecisions := map[string][]float64{}
	var val float64
	mirrors := map[string]bool{}
	feOverlap := map[string][]mv{}
	feKappa := map[string][]mv{}
	fegOverlap := map[string][]mv{}
	feRecall := map[string][]mv{}
	fegRecall := map[string][]mv{}
	fegPrecision := map[string][]mv{}
	fePrecision := map[string][]mv{}
	for _, ann1 := range annotators {
		goldMap := parseCsv(dir + "/" + ann1 + "-results-formatted.csv")
		for _, ann2 := range annotators[1:] {
			// Skip self and avoid do computation of mirror cases for efficiency
			if ann2 == ann1 {
				continue
			} else if _, ok := mirrors[ann1+ann2]; ok {
				continue
			} else if _, ok := mirrors[ann2+ann1]; ok {
				continue
			} else if quality[ann1] == "l" && quality[ann2] == "h" {
				continue
			} else {
				mirrors[ann1+ann2] = true
			}
			predMap := parseCsv(dir + "/" + ann2 + "-results-formatted.csv")
			aKappa := []float64{}
			agOverlap := []float64{}
			agRecall := []float64{}
			agPrecision := []float64{}
			aRecall := []float64{}
			aPrecision := []float64{}
			aOverlap := []float64{}
			for _, field := range fields {
				aKappa = append(aKappa, kappa(docList, goldMap[field], predMap[field]))
				val = overlap(docList, goldMap[field], predMap[field])
				if !math.IsNaN(val) {
					aOverlap = append(aOverlap, val)
				}
				val = recall(docList, goldMap[field], predMap[field])
				if !math.IsNaN(val) {
					aRecall = append(aRecall, val)
				}
				val = precision(docList, goldMap[field], predMap[field])
				if !math.IsNaN(val) {
					aPrecision = append(aPrecision, val)
				}
				r, p, _ := plagdet(docList, goldMap[field], predMap[field])
				if !math.IsNaN(r) {
					agRecall = append(agRecall, r)
				}
				if !math.IsNaN(p) {
					agPrecision = append(agPrecision, p)
				}
				val = granularOverlap(docList, goldMap[field], predMap[field])
				if !math.IsNaN(val) {
					agOverlap = append(agOverlap, val)
				}

			}
			m, v := stat.MeanVariance(aOverlap, nil)
			feOverlap[quality[ann1]+quality[ann2]] = append(feOverlap[quality[ann1]+quality[ann2]], mv{m, v})
			genOverlap[quality[ann1]+quality[ann2]] = append(genOverlap[quality[ann1]+quality[ann2]], aOverlap...) //stat.Mean(aOverlap, nil))
			aOverlap = []float64{}

			m, v = stat.MeanVariance(agOverlap, nil)
			fegOverlap[quality[ann1]+quality[ann2]] = append(fegOverlap[quality[ann1]+quality[ann2]], mv{m, v})
			granOverlap[quality[ann1]+quality[ann2]] = append(granOverlap[quality[ann1]+quality[ann2]], agOverlap...) // stat.Mean(agOverlap, nil))
			agOverlap = []float64{}

			m, v = stat.MeanVariance(aKappa, nil)
			feKappa[quality[ann1]+quality[ann2]] = append(feKappa[quality[ann1]+quality[ann2]], mv{m, v})
			kappas[quality[ann1]+quality[ann2]] = append(kappas[quality[ann1]+quality[ann2]], aKappa...) //stat.Mean(aKappa, nil))
			aKappa = []float64{}

			m, v = stat.MeanVariance(agRecall, nil)
			fegRecall[quality[ann1]+quality[ann2]] = append(fegRecall[quality[ann1]+quality[ann2]], mv{m, v})
			gRecalls[quality[ann1]+quality[ann2]] = append(gRecalls[quality[ann1]+quality[ann2]], agRecall...) //stat.Mean(agRecall, nil))
			agRecall = []float64{}

			m, v = stat.MeanVariance(agPrecision, nil)
			fegPrecision[quality[ann1]+quality[ann2]] = append(fegPrecision[quality[ann1]+quality[ann2]], mv{m, v})
			gPrecisions[quality[ann1]+quality[ann2]] = append(gPrecisions[quality[ann1]+quality[ann2]], agPrecision...) //stat.Mean(agPrecision, nil))
			agPrecision = []float64{}

			m, v = stat.MeanVariance(aRecall, nil)
			feRecall[quality[ann1]+quality[ann2]] = append(feRecall[quality[ann1]+quality[ann2]], mv{m, v})
			recalls[quality[ann1]+quality[ann2]] = append(recalls[quality[ann1]+quality[ann2]], aRecall...) //stat.Mean(aRecall, nil))
			aRecall = []float64{}

			m, v = stat.MeanVariance(aPrecision, nil)
			fePrecision[quality[ann1]+quality[ann2]] = append(fePrecision[quality[ann1]+quality[ann2]], mv{m, v})
			precisions[quality[ann1]+quality[ann2]] = append(precisions[quality[ann1]+quality[ann2]], aPrecision...) //stat.Mean(aPrecision, nil))
			aPrecision = []float64{}

		}
	}
	idMap := map[string]string{"gl": "Gold & Lo", "gh": "Gold & Hi", "ll": "Lo & Lo", "hl": "Hi & Lo", "hh": "Hi & Hi"}
	for _, config := range []string{"gl", "gh", "ll", "hl", "hh"} {
		fmt.Printf("%s & ", idMap[config])
		computeFixedEffects("&", feRecall[config])
		computeFixedEffects("&", fePrecision[config])
		computeFixedEffects("&", feKappa[config])
		computeFixedEffects("&", feOverlap[config])
		computeFixedEffects("&", fegRecall[config])
		computeFixedEffects("&", fegPrecision[config])
		computeFixedEffects("\\\\", fegOverlap[config])
		fmt.Println()
	}

}
