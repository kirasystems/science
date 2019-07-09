// usage: topsig ngram-database size < ngrams > timing | signature
package main

import (
	"bufio"
	"bytes"
	"compress/zlib"
	"database/sql"
	"fmt"
	_ "github.com/mattn/go-sqlite3"
	"io"
	"io/ioutil"
	"math/big"
	"os"
	"strconv"
	"time"
)

type ngramVector struct {
	vector string
	time   int64
	count  int64
}

func check(err error) {
	if err != nil {
		panic(err)
	}
}

func decompressBytes(bytestring []byte) string {
	buf := bytes.NewBuffer(bytestring)
	reader, error := zlib.NewReader(buf)
	decomp, error := ioutil.ReadAll(reader)
	check(error)
	return string(decomp)
}

func readTokens() []string {
	reader := bufio.NewReader(os.Stdin)
	ngrams := []string{}

	for {
		term, error := reader.ReadString('\n')
		if error == io.EOF {
			break
		}
		check(error)
		ngrams = append(ngrams, term[:len(term)-1])
	}

	return ngrams
}

func loadVectors(databaseFile string, size int, ngrams []string) (map[string]ngramVector, int) {
	// Load database
	database, error := sql.Open("sqlite3", databaseFile + "?immutable=true")
	check(error)
	// Make generic statement for fetching random vectors from database
	sizeString := strconv.Itoa(size)
	statement, error := database.Prepare("SELECT topsig_" + sizeString + "," + "topsig_" + sizeString + "_time FROM hashes WHERE ngram=?")
	check(error)

	// Make map
	ngramsVectorMap := make(map[string]ngramVector)

	count := 0
	// Read ngrams
	for _, ngram := range ngrams {
		count++
		if result, ok := ngramsVectorMap[ngram]; !ok {
			row := statement.QueryRow(ngram)

			var vectorblob []byte
			var time int64
			error := row.Scan(&vectorblob, &time)
			check(error)

			// Vectorblob is compressed +/-/0 vector -- decompress it
			vector := decompressBytes(vectorblob)
			ngramsVectorMap[ngram] = ngramVector{vector: vector, time: time, count: 1}
		} else {
			result.count += 1
			ngramsVectorMap[ngram] = result
		}
	}

	return ngramsVectorMap, count
}

func sumVectors(size int, vectorMap map[string]ngramVector) *big.Int {
	counts := make([]int64, size)

	for _, vectorData := range vectorMap {
		vector := vectorData.vector
		for index := 0; index < size; index++ {
			if vector[index] == '+' {
				counts[index] += vectorData.count
			} else if vector[index] == '-' {
				counts[index] -= vectorData.count
			}
		}
	}

	digest := big.NewInt(0)
	for index := size - 1; index >= 0; index-- {
		if counts[size-1-index] > 0 {
			digest.SetBit(digest, index, 1)
		} else {
			digest.SetBit(digest, index, 0)
		}
	}

	return digest
}

func BitCount(n *big.Int) int {
	count := 0
	for _, v := range n.Bits() {
		count += popcount(uint64(v))
	}
	return count
}

// Straight and simple C to Go translation from https://en.wikipedia.org/wiki/Hamming_weight
func popcount(x uint64) int {
	const (
		m1  = 0x5555555555555555 //binary: 0101...
		m2  = 0x3333333333333333 //binary: 00110011..
		m4  = 0x0f0f0f0f0f0f0f0f //binary:  4 zeros,  4 ones ...
		h01 = 0x0101010101010101 //the sum of 256 to the power of 0,1,2,3...
	)
	x -= (x >> 1) & m1             //put count of each 2 bits into those 2 bits
	x = (x & m2) + ((x >> 2) & m2) //put count of each 4 bits into those 4 bits
	x = (x + (x >> 4)) & m4        //put count of each 8 bits into those 8 bits
	return int((x * h01) >> 56)    //returns left 8 bits of x + (x<<8) + (x<<16) + (x<<24) + ...
}

func main() {
	databaseFile := os.Args[1]
	size, error := strconv.Atoi(os.Args[2])
	check(error)

	ngrams := readTokens()
	start := time.Now()
	vectorMap, count := loadVectors(databaseFile, size, ngrams)
	digest := sumVectors(size, vectorMap)
	end := time.Now()
	elapsed := end.Sub(start).Nanoseconds()

	bitcount := BitCount(digest)

	fmt.Printf("%d %s %d %d\n", count, digest.Text(10), bitcount, elapsed)
}
