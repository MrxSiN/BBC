#![no_std]
#![no_main]
use core::arch::asm;

unsafe fn call(number: i64, a: i64, b: i64, c: i64) -> i64 {
    let result;
    unsafe { asm!("svc 0", inlateout("x0") a => result, in("x1") b, in("x2") c,
                 in("x8") number, options(nostack)); }
    result
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    unsafe { call(93, 4, 0, 0); }
    loop {}
}
#[unsafe(no_mangle)]
pub extern "C" fn _start() -> ! {
    let mut byte = 0u8;
    let mut status = 0;
    unsafe {
        loop {
            let mut size;
            loop { size = call(63, 0, &mut byte as *mut u8 as i64, 1); if size != -4 { break; } }
            if size != 0 && size != 1 { status = 4; break; }
            if size == 0 || byte == 0 { break; }
            loop { size = call(64, 1, &byte as *const u8 as i64, 1); if size != -4 { break; } }
            if size != 1 { status = 3; break; }
        }
        call(93, status, 0, 0);
    }
    loop {}
}
