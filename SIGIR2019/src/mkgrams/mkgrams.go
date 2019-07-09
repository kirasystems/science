package main

import "os"
import "bufio"
import "strconv"
import "fmt"
import "io"

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func main() { // usage -- mkgrams k <stdin >stdout
	in := bufio.NewReader(os.Stdin)
	grams, error := strconv.Atoi(os.Args[1])
	check(error)
	runes := make([]rune, 0)

	for {
		rune, _, error := in.ReadRune()

		if error == io.EOF {
			break
		} else if error != nil {
			panic(error)
		}

		// Reslice if we need to
		if len(runes) == grams {
			runes = runes[1:]
		}
		// Add rune to buffer
		runes = append(runes, rune)
		// Write runes then
		if (len(runes) == grams) {
			fmt.Printf("%s\n", string(runes))
		}
	}

	// Flush buffer if we need to
	if len(runes) < grams {
		fmt.Printf("%s\n", string(runes))
	}
}
