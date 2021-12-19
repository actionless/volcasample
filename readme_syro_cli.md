Building Syro CLI only
======================

```
    $ ./build_syro_cli.sh
```


Using Syro CLI only
===================

!! only 16bit mono wav samples are supported !!

To convert it::

```
   $ ffmpeg -i original_sample.wav -acodec pcm_s16le -ac 1 -ar 16000 out.wav
```

## Usage examples:

 - `Sample(Compress bit=16), number = 81, file = test2/81/m81_202109.wav`:

```
    $ ./syro_build/syro test_output_sample81.wav 's81c:test2/81/m81_202109.wav'
```

 - `Sample erase, number = 135`:

```
    $ ./syro_build/syro test_output_erase_135.wav 'e135:'
```

 - `Sample(Compress bit=12), number = 181, file = test2/81/m81_202109.wav`:

```
    $ ./syro_build/syro test_output_sample181.wav 's181c12:test2/81/m81_202109.wav'
```

See `readme_en.markdown -> ####SourceFile` for more.
