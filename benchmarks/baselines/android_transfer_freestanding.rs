#![no_std]
#![no_main]
use core::arch::asm;

unsafe fn syscall3(number: i64, a: i64, b: i64, c: i64) -> i64 {
    let result: i64;
    unsafe {
        asm!("svc 0", inlateout("x0") a => result, in("x1") b, in("x2") c,
             in("x8") number, options(nostack));
    }
    result
}

#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    unsafe { syscall3(93, 4, 0, 0); }
    loop {}
}

#[unsafe(no_mangle)]
pub extern "C" fn _start() -> ! {
    let (mut source, mut result) = (0u8, 0u8);
    unsafe {
        let size = syscall3(63, 0, &mut source as *mut u8 as i64, 1);
        let status = if size != 0 && size != 1 { 4 } else {
            #[cfg(not(direct_echo))]
            {
            while source != 0 {
                result = result.wrapping_add(1);
                source -= 1;
            }
            }
            #[cfg(direct_echo)]
            let output = &source;
            #[cfg(not(direct_echo))]
            let output = &result;
            if syscall3(64, 1, output as *const u8 as i64, 1) == 1 { 0 } else { 3 }
        };
        syscall3(93, status, 0, 0);
    }
    loop {}
}
