#!/bin/bash

urls=('http://172.16.16.101:8889/rfc2616.pdf' 'http://172.16.16.101:8889/pokijan.jpg' 'http://172.16.16.101:8889/testing.txt')
requests=(10 50 100 500)
concurency_levels=(1 5 10 20 25)

for url in "${urls[@]}"; do
    for con in "${concurency_levels[@]}"; do
        for req in "${requests[@]}"; do
            if [ $con -gt $req ]; then
                continue
            fi

            echo "Benchmarking $url using $req request(s) and $con concurency level..."
            ab -n $req -c $con $url > "results/${url##*/}/ab-${req}-${con}-${url##*/}.txt" 2>&1 || sleep 60
        done

        echo ""
    done
done