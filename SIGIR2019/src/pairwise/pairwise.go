package main

import (
	"bufio"
	"fmt"
	"log"
	"math/big"
	"math/bits"
	"os"
	"strconv"
)

// HammingDistance returns the number of bits in which the two ints
// (bit strings) differ
func HammingDistance(a, b *big.Int) int {
	diff := big.NewInt(0)
	diff.Xor(a, b)
	count := 0
	for _, b := range diff.Bytes() {
		count += bits.OnesCount(uint(b))
	}
	return count
}

func countLength(bi *big.Int) int {
	count := 0
	for _, b := range bi.Bytes() {
		count += bits.OnesCount(uint(b))
	}
	return count
}

func doPairwise(hashes []*big.Int, threshold int, l int, u int) {
	counts := map[int]int{}
	if u > len(hashes) {
		u = len(hashes)
	}
	for i := l; i < u; i++ {
		for i := 0; i <= threshold; i++ {
			counts[i] = 0
		}
		for j := 0; j < len(hashes); j++ {
			if i == j {
				continue
			}
			dist := HammingDistance(hashes[i], hashes[j])
			for k := dist; k <= threshold; k++ {
				counts[k]++
			}
		}
		fmt.Print(hashes[i], " ")
		for k := 0; k <= threshold; k++ {
			fmt.Print(counts[k], " ")
		}
		fmt.Println()
	}
}
func main() {
	fileOfFiles := os.Args[1]
	threshold, _ := strconv.Atoi(os.Args[2])
	upper, _ := strconv.Atoi(os.Args[4])
	lower, _ := strconv.Atoi(os.Args[3])
	file, err := os.Open(fileOfFiles)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	vals := []*big.Int{}
	for scanner.Scan() {
		b := big.NewInt(0)
		b.SetString(scanner.Text(), 10)
		vals = append(vals, b)
	}

	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}
	doPairwise(vals, threshold, lower, upper)
}
