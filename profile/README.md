<p align="center"><img src="images/header.svg" alt="wasm-rtos: one .wasm file runs on an ESP32, an STM32 and in the browser" width="100%"></p>

A program is an ordinary `.wasm` file built from C, C++ or an Arduino
sketch, and the kernel runs it the way a desktop OS runs an executable. The same file runs on an
ESP32, on an STM32 and in the browser simulator at
<https://wasm-rtos.github.io>, and a program stopped on one of them can go
on on another.

It is written from scratch: a kernel and its own interpreter, both small
enough for chips with 128 KB of RAM (the interpreter alone fits an Arduino
Uno), both in plain C with no platform code.

## How it fits together

<p align="center"><img src="images/architecture.svg" alt="Programs, the kernel, the interpreter and the board, and what passes between them" width="100%"></p>

- A **program** calls the system through imports: WASI for files, time and
  output, and the wasm-rtos ABI (versioned, now 1.8) for kernel objects and
  devices. It never sees an address of the host.
- The **kernel** decides: which program runs next and for how long, who owns
  a pin or a bus, which frames of memory stay in RAM. It has no platform
  code: a board gives it a clock and its devices through small ports.
- The **interpreter** runs the program's own instructions, counts them and
  stops between any two of them, and pages the program's memory. It knows
  nothing of tasks or devices.

## What the interpreter does

<p align="center"><img src="images/fuel.svg" alt="Task A runs until its fuel is gone and stops between two instructions; task B gets a slice; later A goes on from the next instruction" width="100%"></p>

- **Fuel.** One unit is one WebAssembly instruction of the module, counted
  by the interpreter itself: programs are not rewritten or instrumented
  first. The same program uses the same fuel on every device (a test run
  takes 900013 on an ESP32, an STM32 and a computer alike).
- **A safe point at every instruction.** A call stops when its fuel runs
  out, when a host function asks, or when memory it touches is on its way
  from storage. Everything about the stopped program is plain data.
- **Portable snapshots.** A stopped program is saved by its position in the
  module, not by host addresses, and continues in another build, on another
  chip, with other pointer sizes.
- **MMU.** Programs' memory is paged in frames (4 KiB by default) through a
  TLB; a pager of the host moves frames to storage and back, in the
  background where the storage can. A memory in one block costs nothing on
  the fast path.
- **Code as a cache.** Functions are decoded into compact records for a fast
  loop at their first call; the records are dropped when memory is short and
  made again when needed, never those of a function on a call stack.
- **The full standard.** WebAssembly 2.0 without SIMD: the official test
  suite passes (27437 checks), also under the sanitizers, in every build.
- **dylink.0** shared libraries, traces after a trap, options to leave out
  validation, 64-bit integers, floats or reference types on small chips.

## What the kernel does

- **Preemption without a timer interrupt.** Each program gets a slice of
  fuel, so a plain `int main` with an endless loop still shares the
  processor, and a program cannot block the others.
- **Real-time objects** for the host and for programs: priorities with
  priority inheritance, queues, mutexes, semaphores, event groups, task
  notifications, software timers, waiting for several objects at once.
- **Processes.** Programs start other programs from memory or a file path
  with arguments, wait for their exit codes and stop them; libraries are
  shared, each process with its own copy of their data.
- **Isolation.** Each program has its own memory and reaches the kernel only
  through checked calls; a program that traps ends alone, and the pins and
  devices it held come back.
- **Devices for programs**, each lent to one program at a time: GPIO by pin
  name, displays, input devices, I2C, SPI and 1-Wire buses, analog inputs
  and outputs, PWM, serial ports, pulse trains (addressable LEDs, IR) and
  counters (encoders). Transfers can run in the background with DMA while
  only the calling program waits.
- **Memory larger than RAM.** With a page store, programs' memory is a cache
  in RAM; a waiting program can leave RAM altogether and come back when it
  runs.
- **A file system** behind the WASI file calls, with a read-only tar driver;
  programs start from files.

## Memory larger than RAM

<p align="center"><img src="images/memory.svg" alt="A program's memory in frames, some in RAM and some in a page store, and predecoded code as a cache" width="100%"></p>

The interpreter pages, the kernel decides. A frame comes into RAM when the
program touches it; while a slow store reads it, only that program waits.
When RAM is full the kernel sends a frame not touched lately to the page
store, writing it only if it was written. Decoded code is a cache in the
same RAM and gives way first: a program's memory is never refused while
records can be made again later.

## Measured

<p align="center"><img src="images/numbers.svg" alt="18 programs at once on an ESP32, 9 on an STM32, the interpreter in 34.7 KB on an Uno, 27437 spec checks" width="100%"></p>

- **CoreMark inside the OS**, among the other programs: 11.8 on an ESP32,
  5.84 on an STM32F411.
- **Memory larger than RAM:** on an ESP32 with 250 KB of free heap, a program
  with 640 KB of memory runs, paged from an SD card.
- **The same work, the same fuel:** a test program takes 900013 units on an
  ESP32, an STM32 and a computer alike.

The board checks also cover traps, sleeping on time, fair shares between
equal programs, priorities, wake-up latency, queues between programs and
that every byte comes back after shutdown.

## Repositories

| Repository | What is in it |
|---|---|
| [wasm-rtos](https://github.com/wasm-rtos/wasm-rtos) | The kernel: scheduler, objects, processes, files, drivers, paging policy, the guest ABI (`include/wasm-rtos.h`, `wit/kernel.wit`). |
| [wasm-rtos-vm](https://github.com/wasm-rtos/wasm-rtos-vm) | The interpreter: fuel, MMU, code cache, snapshots, dylink.0. Usable on its own. |
| [wasm-rtos-libraries](https://github.com/wasm-rtos/wasm-rtos-libraries) | Libraries inside programs: the Arduino core (`Serial`, `Wire`, `SPI`) and ports of Arduino libraries for 1-Wire sensors, encoders and addressable LEDs. |
| [wasm-rtos-tests](https://github.com/wasm-rtos/wasm-rtos-tests) | One test per feature, run on every change of the kernel, also under the sanitizers. |
| [wasm-rtos.github.io](https://github.com/wasm-rtos/wasm-rtos.github.io) | The browser simulator: the same kernel compiled to WebAssembly, a dev board with devices, a bus analyzer. |

## Roadmap

Where the project stands, kept up to date with every merged change. Ideas
and questions: [Discussions](https://github.com/orgs/wasm-rtos/discussions).

**Now: programs that live through deep sleep**

- [x] The kernel saves the whole system before the RAM is lost and restores
  it after: tasks with their waits, queues, mutexes, semaphores, events,
  timers, children, open files; the clock goes on with the time slept
  ([wasm-rtos#69](https://github.com/wasm-rtos/wasm-rtos/pull/69))
- [x] Drivers save and restore their devices, so programs that hold pins,
  buses, serial ports or a display can be saved too
  ([wasm-rtos#70](https://github.com/wasm-rtos/wasm-rtos/pull/70), in review)
- [x] Waking by a pin a sleeping program waits on (#70)
- [x] On boards: an ESP32 in deep sleep woken by its timer and by a pin, the
  system on its SD card (saved in 0.1 to 0.24 s, restored in 61 to 73 ms);
  a Black Pill reset, the system in flash (restored in 40 ms) (#70)

**Then: 1.0**

- [ ] The guest ABI 1.x frozen
- [ ] Every repository explains its design in `docs/decisions.md` (the
  interpreter and the kernel do)
- [ ] The simulator on the current kernel: page store, saved systems
- [ ] Changelogs, tags and the 1.0 release

**After 1.0**

- [ ] Moving a running program to another device or into the browser
- [ ] dylink.0 programs in snapshots
- [ ] More from the MMU: compressed frames in RAM, reading ahead, storage
  drivers with DMA, blocks written out in the background
- [ ] A faster interpreter: operands inside records, code records in flash
- [ ] Programs in more languages: a Rust crate for the ABI
- [ ] Programs that state what they need, power management, windows for
  programs with a display, graphics libraries
- [ ] A redesigned simulator with components and chip models

## Timeline

<p align="center"><img src="images/timeline.svg" alt="Timeline from July to November 2026" width="100%"></p>

| When | What |
|---|---|
| July 2026 | The kernel starts: synchronization objects, queues, software timers and a tickless clock, on a third-party interpreter patched for fuel and snapshots. A browser dashboard shows the scheduler live. |
| August 2026 | Shared WebAssembly libraries and programs loaded at run time. |
| Late October 2026 | Processes (spawn, wait, kill), a virtual file system, entry points found and imports checked at load. |
| 1–2 November 2026 | Guest ABI 1.0 and the device interfaces in a few days: GPIO, display and input, I2C and SPI with background transfers, analog inputs, PWM, serial ports, pulse trains. The Arduino core: sketches and libraries become programs. Swapping and portable snapshots. |
| 7 November 2026 | ABI 1.6–1.8: 1-Wire, counters and encoders, analog outputs. First runs on a real ESP32. |
| 9 November 2026 | Our own interpreter, wasm-rtos-vm, becomes the engine: faster than the patched one on the boards (CoreMark on a bare ESP32 13.1 against 4.0), with the same API to the kernel. Drivers become pluggable modules. Records packed into 32-bit cells. |
| 11 November 2026 | The MMU: paged memory, a TLB, a page store with dirty frames written like a log, frames read and written in the background, whole tasks swapped out through it. |
| 12 November 2026 | Code as a cache: 50% more programs at once on an ESP32 and a Black Pill. Memory before code. CI builds the interpreter and the kernel in every configuration and runs the whole suite on every change. |

All of it is public domain.
