## The Phantom Refund 


Contestants are given a fragment of raw bytecode, something between a contract init and a runtime, and want to know what value ends up in storage slot 0x42 after the code finishes running.

You are free to use:
- Manual EVM reasoning
- Custom mini-EVM interpreters
- Foundry, hevm, evm.codes, etc.
- LLMs as assistants

Only the **final value in slot `0x42`** matters for correctness.


---

### 🧱 Runtime Bytecode (hex)

```
0x6000356042146018576000604255609960425560006000fd5b6000604255602a604255731111111111111111111111111111111111111111ff
```

---

### 📥 Calldata

```
0x0000000000000000000000000000000000000000000000000000000000000042
```

(A single 32-byte word = `0x42`)

---

### 🗄 Initial Storage

| Slot   | Value        |
|--------|--------------|
| `0x42` | `0xdeadbeef` |

(All other slots = `0x00`)

---

### 🎯 Task

After executing this bytecode with the calldata above, **what is the final value stored at slot `0x42`?**

Let's call that final value `ANSWER` (a hex string like `0x...`).

You **must not** put `ANSWER` in your PR anywhere.

Instead, you'll submit an encrypted commitment to your answer and send your reasoning privately. 

---

### 🔐 How to Submit Your Encrypted Answer

To avoid leaking the answer publicly, you will submit a hash commitment.

**1. Compute the Hash**
    
The string to hash is:

```
STRING_TO_HASH = "<handle>-<ANSWER>"
```

Where `<handle>` is your GitHub username exactly as it appears on GitHub (lowercase).

For example, if your handle is `alice` and you think the answer is `0x1234`, the string is: 

```
alice-0x1234
```

**2. Generate the SHA-256 Hash**

Make sure you use echo -n (no newline):

macOS / Linux
```
echo -n "alice-0x1234" | sha256sum
```

macOS with `shasum`:
```
echo -n "alice-0x1234" | shasum -a 256
```

Copy only the 64-hex-character digest.

**3. Create a Submission File**

In your fork:

```
submissions/<handle>.txt
```

Examples for `alice`:
```
submissions/alice.txt
```

The file must contain exactly one line: 
```
<handle> <sha256(handle-ANSWER)>
```
Example (fake hash):
```
alice 736342f9c0b4d2e57b6c0a9c9e0b0f4dc1c6c6a2d0b8f8d6c2c3e5d7f9a1b2c
```
**4. Open a PR** 

Include:
- Your `submissions/<handle>.txt` file
- (Optional) solver code in your fork under `solutions/<handle>/`
(Do not include the raw ANSWER in tests or comments.)

I will verify your hash locally against the true answer. The actual `ANSWER` is never stored in this repo. 

---

### 🤫 Submit Your Reasoning Privately (Review-Only Comment)


I also want to understand your approach, but this must remain private.

GitHub review comments are only visible to:

- You (the commenter)
- Repo maintainers (me)


**How to Submit Reasoning:**
1. After opening your PR, go to the “**Files changed**” tab.
2. Click “**Review changes**” (top-right).
3. Select “**Comment**” (not “Approve” or “Request changes”).
4. In the review comment box, write your reasoning:
    - Tools you used (Foundry, Rust mini-EVM, manual opcode tracing, LLM, etc.)
    - How you traced the control flow
    - How you arrived at your final value
    - Anything interesting you learned / mistakes you made

Please do not write the raw `ANSWER` (e.g. `0x...`) in your reasoning — describe it indirectly if needed (e.g. “a small nonzero constant” is fine).

---

### 🏅 Hall of Fame (Verified Solvers)

These folks have submitted a correct encrypted answer and private reasoning.
Approach tags are self-reported (add yours in your PR description or reasoning).

| Handle       | Approach Tag (self-reported)           |
|-------------|-----------------------------------------|
| `gpt5` | LLM |
