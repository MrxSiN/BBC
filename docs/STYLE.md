# Writing style

This project should sound like a person who has actually debugged Brainfuck. Not a quarterly earnings call.

The reference is the public [MrxSiN profile README](https://github.com/MrxSiN/MrxSiN), with technical context from [GmailHideAds](https://github.com/MrxSiN/GmailHideAds) and [XAX](https://github.com/MrxSiN/XAX). The voice is direct, technically precise, informal when it helps, and occasionally dry. This is an editorial reference, not a claim that the author endorsed these specific sentences.

## Do

- Say what works, what fails, and how it was tested. Exact limits and hashes beat adjectives.
- Use small headings, clear tables when they help, and normal sentences rather than inflated status language.
- Explain why an odd decision exists. Fixed 32-byte slots waste space, but make pure-BF branch relocation manageable.
- Use a joke when it actually fits. One per document is plenty; a failing syscall isn't the place to get cute.
- Keep `EXECUTED`, `STRUCTURAL`, `MEASURED` and `UNIMPLEMENTED` separate.
- Update README, state, handoff, issue list and evidence together when behavior changes.

## Don't

- Write 'revolutionary', 'synergy', 'leverage' or 'enterprise-grade' for ordinary code.
- Pretend a reference interpreter is a compiler, or testing is formal verification.
- Rephrase the user-supplied original requirement as if it were completed work.
- Hide errors, unsupported systems or dependencies behind a confidence-filled paragraph.
- Claim ignored comments are absent from `.bf` files. Six small safe annotations exist in the authoritative file. They remain ordinary ignored source bytes; after Iteration 19 they are removed inside the native BF compiler and do not consume native slots.

`docs/PROJECT_REQUIREMENTS.md` mirrors the latest supplied requirements. Historical evidence and archived documentation should remain historically accurate rather than being rewritten to make old releases look better. Maintained documentation and notes follow this style.
