package main

import (
	"bufio"
	"fmt"
	"log"
	"math/big"
	"math/bits"
	"os"
	"strconv"
	"time"

	"golang.org/x/crypto/sha3"
)

const (
	// Size is the size, in bytes, of the hash.
	Size = 16

	// BlockSize is mostly irrelevent for us.
	BlockSize = 64

	// featureSize is the size of the hash features.
	featureSize = 4

	// sizeBits is the size of the hash in bits.
	sizeBits = 1024
)

// digest represents the partial evaluation of hash
type digest struct {
	hashBitCounts [sizeBits]int
	last3Bits     []byte
	size          int
}

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

// New returns a new Hash128 computing the simhash
func new(size int) *digest {
	return &digest{size: size}
}

// Write implements the io.Writer interface
func (d *digest) Write(p []string) (n int, err error) {
	i := 0
	for ; i < len(p); i++ {
		b := make([]byte, d.size)
		sha3.ShakeSum256(b, []byte(p[i]))

		for i := 0; i < d.size; i++ {
			reverseIndex := 127 - i
			for j := 0; j < 8; j++ {
				if b[reverseIndex]&(1<<uint8(j)) == 0 {
					d.hashBitCounts[i*8+j]--
				} else {
					d.hashBitCounts[i*8+j]++
				}
			}
		}
	}

	return len(p), nil
}

// Sum returns the current hash as a big integer
func (d *digest) Sum() (digest *big.Int) {
	d1 := *d // copy - don't update underlying state
	digest = big.NewInt(0)

	for k := (sizeBits) - 1; k >= 0; k-- {
		if d1.hashBitCounts[k] > 0 {
			digest.SetBit(digest, k, 1)
		} else {
			digest.SetBit(digest, k, 0)
		}
	}
	return digest
}

func countLength(bi *big.Int) int {
	count := 0
	for _, b := range bi.Bytes() {
		count += bits.OnesCount(uint(b))
	}
	return count
}

func makeSimhash(inFile string, hashLength int) {
	file, err := os.Open(inFile)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	scanner := bufio.NewReader(file)
	vals := []string{}
	t, e := scanner.ReadString('\n')
	for e == nil {
		vals = append(vals, t[:len(t)-1])
		t, e = scanner.ReadString('\n')
	}
	d := new(hashLength)
	s := time.Now()
	d.Write(vals)
	v := d.Sum()
	elapsed := time.Now().Sub(s).Seconds()
	fmt.Println(len(vals), v, countLength(v), elapsed)
}
func main() {
	fileOfFiles := os.Args[1]
	hashLength, _ := strconv.Atoi(os.Args[2])
	hashLength /= 8
	file, err := os.Open(fileOfFiles)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		makeSimhash(scanner.Text(), hashLength)
	}

	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}
}
