use std::io::{self, Read, Write};
#[cfg(not(bf_stress))] const A: u8 = 15;
#[cfg(not(bf_stress))] const B: u8 = 17;
#[cfg(bf_stress)] const A: u8 = 100;
#[cfg(bf_stress)] const B: u8 = 101;
fn main() -> io::Result<()> {
    let mut input = [0u8; 1];
    let size = io::stdin().read(&mut input)?;
    let mut outer = if size == 1 { input[0] } else { 0 };
    let (mut middle, mut inner, mut result) = (0u8, 0u8, 0u8);
    while outer != 0 {
        middle = middle.wrapping_add(A);
        while middle != 0 {
            inner = inner.wrapping_add(B);
            while inner != 0 {
                result = result.wrapping_add(1);
                inner = inner.wrapping_sub(1);
            }
            middle = middle.wrapping_sub(1);
        }
        outer = outer.wrapping_sub(1);
    }
    io::stdout().write_all(&[result])
}
