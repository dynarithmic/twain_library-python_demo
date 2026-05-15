# twain_library-python_demo
`dtwdemo.py` is a python demo program using the <a href="https://github.com/dynarithmic/twain_library" target="_blank">DTWAIN Library</a>.

To run `dtwdemo.py`, the following requirements are needed:

1. Python

   * Python 3.10 or higher is recommended.
   * The Python interpreter bitness must match the DTWAIN DLL:

     * 32-bit Python ? `dtwain32u.dll`
     * 64-bit Python ? `dtwain64u.dll`

2. Required Python Modules

   * `tkinter`

     * Normally included with standard Windows Python installations.
   * `Pillow` (PIL)

     * Used for displaying acquired DIB images.

Install Pillow using:

```bash id="j29t6k"
pip install pillow
```

If multiple Python versions are installed, ensure Pillow is installed for the same interpreter used to run `dtwdemo.py`.

Example:

```bash id="8rj6gm"
C:\Python313-32\python.exe -m pip install pillow
```

3. DTWAIN DLLs

   * Place the following files in the same directory as `dtwdemo.py`:

     * `dtwain32u.dll`
     * `dtwain64u.dll`

4. DTWAIN Text Resource Files

   * The DTWAIN language/text resource files are also required.

   * These files are located here:

     [DTWAIN Text Resources](https://github.com/dynarithmic/twain_library/tree/master/text_resources?utm_source=chatgpt.com)

   * Normally, users who installed DTWAIN already have these files.

   * The text resource files should reside in the same directory as the DTWAIN DLLs.

5. TWAIN Driver / Scanner

   * A TWAIN-compatible scanner driver must already be installed.

6. Running the Program

```bash id="0p67ki"
python dtwdemo.py
```

or run directly from Visual Studio / VS Code using the correct Python interpreter.

