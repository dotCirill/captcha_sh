package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"strings"

	"github.com/cheggaaa/pb/v3"
	prmt "github.com/gitchander/permutation"
	fuzzy "github.com/paul-mannino/go-fuzzywuzzy"
)

const WORKERS = 8
const EMAILS_PATH = "emails.txt"

//const INPUT = "vla dls lev 189 9@g ma kf* com"
//const INPUT = "dan i* sem eno v@y an dex .ru"
const INPUT = "che bur asb ka@ hot nai l.* om"

var emails []string // emails from EMAILS_PATH
var parts []string

type candidate_t struct {
	email string
	ratio int
	perm  string
}

var candidates [WORKERS]candidate_t

func worker(i int, perm_c chan []uint8, done_c chan bool) {
	//fmt.Fprintf(os.Stderr, "Worker %v started\n", i+1)
	for {
		perm := <-perm_c
		if len(perm) != 8 {
			break
		}

		var email_builder strings.Builder
		for _, perm_number := range perm {
			email_builder.WriteString(parts[perm_number])
		}

		email := email_builder.String()
		// fuzzy.ExtractOne is extrimly slow (wtf?)
		// Using PartialRatio has some sence
		for _, real_email := range emails {
			ratio := fuzzy.Ratio(email, real_email)

			if ratio > candidates[i].ratio {
				candidates[i].ratio = ratio
				candidates[i].email = email
				var perm_string strings.Builder
				for _, perm_number := range perm {
					perm_string.WriteString(fmt.Sprintf("%v ", perm_number))
				}
				candidates[i].perm = perm_string.String()
			}
		}
	}

	done_c <- true
}

func main() {
	fmt.Fprintf(os.Stderr, "text2email\n")
	emails_txt, err := ioutil.ReadFile(EMAILS_PATH)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error reading %v\n", EMAILS_PATH)
		os.Exit(1)
	}

	emails = strings.Split(string(emails_txt), "\n")
	fmt.Fprintf(os.Stderr, "Read %v emails from %v\n", len(emails), EMAILS_PATH)

	parts = strings.Split(INPUT, " ")
	if len(parts) != 8 {
		fmt.Fprintf(os.Stderr, "Parts count is not 8\n")
		os.Exit(1)
	}

	perm_c := make(chan []uint8, WORKERS)
	done_c := make(chan bool, WORKERS)
	defer close(perm_c)
	defer close(done_c)

	for i := 0; i < WORKERS; i++ {
		go worker(i, perm_c, done_c)
	}

	bar := pb.StartNew(40320) // 8!
	perm := []int{0, 1, 2, 3, 4, 5, 6, 7}
	p := prmt.New(prmt.IntSlice(perm))
	for p.Next() {
		bar.Increment()
		perm_copy := make([]uint8, 8)
		for i, elem := range perm {
			perm_copy[i] = uint8(elem)
		}

		perm_c <- perm_copy
	}

	for i := 0; i < WORKERS; i++ {
		perm_c <- []uint8{}
	}

	for i := 0; i < WORKERS; i++ {
		_ = <-done_c
	}

	bar.Finish()
	var best candidate_t
	for _, candidate := range candidates {
		if candidate.ratio > best.ratio {
			best = candidate
		}
	}

	fmt.Fprintf(os.Stderr, "Candidate: %v\n", best)
	fmt.Println(best.perm)
}
