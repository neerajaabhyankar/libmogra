# libmogra

A Python Toolbox for Indian (Classical) Music

## The Why

For playing around (understanding, modifying, etc.) with music & audio specifically in the Indian context. Music theory standardization as well as tool development has been done extensively for western music, but other music cultures lag behind. This library will start with small features, but the dream is to have a Photoshop for Indian music.

## The What

This is intended to be a higher-level layer on top of the widely used [librosa](https://github.com/librosa/librosa).
If you must have an acronym, here it is: a LIBrary for the Manipulation, Organization, Generation, and Raag-aware Analysis of music. If that's too much, think of [mogra](https://en.wikipedia.org/wiki/Jasminum_sambac) the flower `:)`

# mogra CLI

```
pip install libmogra
```
will also install the `mogra` command-line interface.


To find info about a raag
```
mogra info bairagi
```
To visualize its tonnetz diagram (if available)
```
mogra info bairagi --tonnetz=window
```
To look at just the Tonnetz diagram by itself
```
mogra info all --tonnetz=window
```

To search for a raag given its notes among SrRgGmMPdDnN (note: follow the convention m = shuddha and M = teevra)
```
mogra search SrmPn
```
