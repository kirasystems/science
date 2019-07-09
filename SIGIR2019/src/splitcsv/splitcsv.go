package main

import "os"
import "encoding/csv"
import "bufio"
import "io"
import "io/ioutil"

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func main() { // usage -- ./splitcsv inputfile
	csvFile, error := os.Open(os.Args[1])
	check(error)

	reader := csv.NewReader(bufio.NewReader(csvFile))
	for {
		line, error := reader.Read()

		if error == io.EOF {
			break
		} else if error != nil {
			check(error)
		}

		document_id := line[0]
		filename := line[1]
		contents := []byte(line[2])

		// Open and write output file
		error = ioutil.WriteFile(document_id+"-"+filename+".raw", contents, 0644)
		check(error)
	}
}
