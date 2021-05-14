package main

import (
	"fmt"
	"image"
	"image/png"
	_ "io"
	"io/ioutil"
	"os"
	"path"

	"github.com/cheggaaa/pb/v3"
)

const MAX_DIST = 3 * 255 * 1000 * 1000
const WORKERS int = 8

var GEN_DIR string

type candidate_t struct {
	fname    string
	distance uint32
}

var candidates [WORKERS]candidate_t

func num_distance(x, y uint32) uint32 {
	if x < y {
		return y - x
	}

	return x - y
}

func read_image(filename string) (image.Image, error) {
	data, err := os.Open(filename)
	if err != nil {
		return nil, err
	}

	defer data.Close()

	image, err := png.Decode(data)
	if err != nil {
		return nil, err
	}

	return image, nil
}

func distance(a image.Image, b image.Image) uint32 {
	var distance uint32 = 0
	for i := 0; i < a.Bounds().Max.X; i++ {
		for j := 0; j < a.Bounds().Max.Y; j++ {
			a1, a2, a3, _ := a.At(i, j).RGBA()
			b1, b2, b3, _ := b.At(i, j).RGBA()
			distance += num_distance(a1, b1) + num_distance(a2, b2) + num_distance(a3, b3)
		}
	}

	return distance
}

func worker(input_image image.Image, file_c chan string, done_c chan bool, i int) {
	fmt.Fprintf(os.Stderr, "Worker %v started\n", i+1)
	for {
		file := <-file_c
		if file == "" {
			break
		}
		image, err := read_image(path.Join(GEN_DIR, file))
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error reading %v image: %v\n", file, err)
			continue
		}

		dist := distance(input_image, image)
		if dist < candidates[i].distance {
			candidates[i].distance = dist
			candidates[i].fname = file
		}
	}

	done_c <- true
}

func init_candidates() {
	for i := 0; i < WORKERS; i++ {
		candidates[i].distance = MAX_DIST
		candidates[i].fname = "/dev/null"
	}
}

func main() {
	args := os.Args

	if len(args) < 3 {
		fmt.Fprintf(os.Stderr, "Usage: %v {input file} {searching dir}\n", args[0])
		os.Exit(1)
	}

	GEN_DIR = args[2]

	init_candidates()
	input_image, err := read_image(args[1])
	if err != nil {
		fmt.Fprintf(os.Stderr, "Input image reading error: %v\n", err)
		os.Exit(1)
	}

	files, err := ioutil.ReadDir(GEN_DIR)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Reading searching directory error: %v\n", err)
		os.Exit(1)
	}

	bar := pb.StartNew(len(files))
	file_c := make(chan string, WORKERS)
	done_c := make(chan bool, WORKERS)

	for i := 0; i < WORKERS; i++ {
		go worker(input_image, file_c, done_c, i)
	}

	for _, f := range files {
		bar.Increment()
		file_c <- f.Name()
	}

	for i := 0; i < WORKERS; i++ {
		file_c <- ""
	}

	close(file_c)

	for i := 0; i < WORKERS; i++ {
		_ = <-done_c
	}

	bar.Finish()
	close(done_c)

	var best candidate_t
	best.distance = MAX_DIST

	for _, candidate := range candidates {
		if candidate.distance < best.distance {
			best = candidate
		}
	}

	fmt.Println(best.fname[:len(best.fname)-4]) // without .png
}
