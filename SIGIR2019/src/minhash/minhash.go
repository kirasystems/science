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
	hashes      map[string]string
	time        int64
	count       int64
	corpusCount int64
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

func loadVectors(databaseFile string, size int, ngrams []string) (map[string]ngramVector, int64, int64) {
	// Load database
	database, error := sql.Open("sqlite3", databaseFile)
	check(error)
	// Make generic statement for fetching random vectors from database
	statement, error := database.Prepare("SELECT count, md5_hash, md5_time, sha1_hash, sha1_time, sha256_hash, sha256_time, sha512_hash, sha512_time FROM hashes WHERE ngram=?")
	check(error)

	// Make map
	ngramsVectorMap := make(map[string]ngramVector)

	// Count document ngrams
	count := int64(0)
	// Read ngrams
	for _, ngram := range ngrams {
		count++
		if result, ok := ngramsVectorMap[ngram]; !ok {
			row := statement.QueryRow(ngram)

			var md5_hash string
			var md5_time int64
			var sha1_hash string
			var sha1_time int64
			var sha256_hash string
			var sha256_time int64
			var sha512_hash string
			var sha512_time int64
			var corpusCount int64
			error := row.Scan(&corpusCount, &md5_hash, &md5_time, &sha1_hash, &sha1_time, &sha256_hash, &sha256_time, &sha512_hash, &sha512_time)
			check(error)

			hashes := make(map[string]string)
			hashes["md5"] = md5_hash
			hashes["sha1"] = sha1_hash
			hashes["sha256"] = sha256_hash
			hashes["sha512"] = sha512_hash
			time := md5_time + sha1_time + sha256_time + sha512_time
			ngramsVectorMap[ngram] = ngramVector{corpusCount: corpusCount, hashes: hashes, time: time, count: 1}
		} else {
			result.count += 1
			ngramsVectorMap[ngram] = result
		}
	}

	// Count corpus ngrams
	/*
	statement, error = database.Prepare("SELECT SUM(count) FROM hashes")
	check(error)
	row := statement.QueryRow()
	var corpusCount int64
	error = row.Scan(&corpusCount)
	check(error) */
	corpusCount := int64(7156001173)

	return ngramsVectorMap, count, corpusCount
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func sumVectors(size int, vectorMap map[string]ngramVector, documentCount int64, corpusCount int64) (*big.Int, int64) {
	minHashes := make(map[string]*big.Int)
	hashFunctions := []string{"md5", "sha1", "sha256", "sha512"}
	hashLen := make(map[string]int)
	totalTime := int64(0)

	// Get hash of each ngram
	for _, vectorData := range vectorMap {
		remainingBits := size

		for idx, hashfn := range hashFunctions {
			// Compute bits to take
			hashValue := vectorData.hashes[hashfn]
			bitsInHash := len(hashValue) * 8
			sliceToTake := min(bitsInHash, remainingBits/(len(hashFunctions)-idx))
			hashLen[hashfn] = sliceToTake
			remainingBits -= sliceToTake
			// Get hash and slice
			hashInt := big.NewInt(0)
			hashInt, _ = hashInt.SetString(hashValue, 16)
			hashBits := hashInt.Text(2)
			// Actually make sure that sliceToTake doesn't run into a OOB error
			sliceToTake = min(len(hashBits), sliceToTake)
			hashBits = hashBits[len(hashBits)-sliceToTake : len(hashBits)]
			hashInt, _ = hashInt.SetString(hashBits, 2)
			// Sort
			if currentHash, ok := minHashes[hashfn]; ok {
				if currentHash.Cmp(hashInt) == 1 {
					minHashes[hashfn] = hashInt
				}
			} else {
				minHashes[hashfn] = hashInt
			}
			// Add time
			totalTime += vectorData.time
		}
	}

	// Add all hashes, making sure padding correctly.
	digestRaw := ""
	digest := big.NewInt(0)
	for _, hashfn := range hashFunctions {
		digestRaw += fmt.Sprintf("%0"+strconv.Itoa(hashLen[hashfn])+"b", minHashes[hashfn])
	}
	digest, _ = digest.SetString(digestRaw, 2)

	return digest, totalTime
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
	vectorMap, count, corpusCount := loadVectors(databaseFile, size, ngrams)
	start := time.Now()
	digest, hashTime := sumVectors(size, vectorMap, count, corpusCount)
	end := time.Now()
	elapsed := end.Sub(start).Nanoseconds() + hashTime

	bitcount := BitCount(digest)

	fmt.Printf("%d %s %d %d\n", count, digest.Text(10), bitcount, elapsed)
}
