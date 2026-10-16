use std::io::{self, Read, Write};

fn main() -> io::Result<()> {
    let mut input = [0u8];
    io::stdin().read(&mut input)?;
    let (mut source, mut result) = (input[0], 0u8);
    while source != 0 {
        result = result.wrapping_add(1);
        source -= 1;
    }
    io::stdout().write_all(&[result])
}
