use std::env;
use std::fs::File;
use std::io::prelude::*;
use std::process;

fn main() -> std::io::Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 5 {
        println!("Not enough arguments");
        process::exit(-1);
    }
    let mut file = File::open(&args[1])?;
    let interval: f64 = args[2].parse().unwrap();
    let from_ts: f64 = args[3].parse().unwrap();
    let to_ts: f64 = args[4].parse().unwrap();

    let mut content = String::new();
    file.read_to_string(&mut content)?;

    let mut out = String::with_capacity(25);
    let mut last_ts = 0.0;
    for line in content.lines() {
        let ts: f64 = line.split(" ").collect::<Vec<&str>>()[0].parse().unwrap();
        if from_ts < ts && ts < to_ts && ts - last_ts > interval {
            out.push_str(line);
            out.push_str("\n");
            last_ts = ts
        }
    }
    println!("total capacity: {}", out.capacity());
    println!("{}", out);
    Ok(())
}
