A Network of Ideas
==================

A stab in the dark towards concept oriented programming combined with a
semantic wiki.  Original proposal: https://wildideas.org/anoi/

ANOI Design
-----------

### Types

Types have the following properties:
- Type -> Type (Type)
- Name -> String (Is this strictly necessary?)
- Properties -> List of Property

#### Properties

- Type -> Type (Property)
- Name -> String (Again, might this be optional?)

### Strings

Strings are just vectors of UIDs which are constrained to map 1:1 with Unicode
code points (in the range 0-0x10ffff).

Strings have the following properties:
- Type -> Type (String)

### Media

Media refers to raw binary data.  A byte array of the media data is "punned" as
a vector of UIDs (in the range 0-255).

Media atoms have the following properties:
- Type -> Type (Media)
- Name -> String
- Author(s)?
- MIME Type -> String

### Articles

Articles have the following properties:
- Type -> Type (Article)
- Title -> String
- Author(s)? -> List of People, FIXME: Need parametric types.
- Date -> Date
- Origin -> Media
- Lexicon -> List (stack) of Tries

#### Article Creation Workflow

- Article written as markdown, submitted via form (or just POST method to edit
  endpoint)
- Validate markdown
- Create origin atom and store original input string as Unicode vector.
- Create article atom
- Create title atom and store original title string as Unicode vector.
- (?) Add title to top of lexicon stack
- Create timestamp atom and store UTC string as Unicode vector.
- Convert wiki links to corresponding UIDs, then compress the remainder using
  subsequent tries in the lexicon stack.  Warnings:
  - This may screw things up if the lexicon doesn't have a 1:1 correspondence
    with titles.  Possible fix: add alias dimension to lexicon keys.

Design Internals
----------------

"Boot" trie @ ROOT.  What does "boot" mean in this context?

TODO's
------
- [ ] Port to Unicode
  - [x] Trie implementation
  - [ ] Decompressor
  - [ ] Unit tests of port
- [ ] Loaders
  - [ ] Markdown
  - [ ] Media
  - [ ] HTML: via markdownify
  - [ ] Jupyter notebooks: via nbconvert (to markdown)
  - [ ] Latex: via LaTeX2HTML
  - [ ] PDF
  - [ ] WordNet
  - [ ] Dbpedia
  - [ ] Wikipedia
- [ ] Web application
  - [ ] Markdown translator

Notes
-----

### 2021.10.21

In an attempt to reinvent the wheel, I'm trying to come up with my own document
markup language for the ANOI internal representation.  Well, actually I want to
support easy ingestion and rendering of the following (which is redundant in
light of the TODO's):

* HTML 5
* Markdown
* Latex

I'm feeling somewhat inspired by [JSONML](http://www.jsonml.org/).  The
resulting JSON format could be rendered in YAML.  For example, this paragraph
would look like the following:

```yaml
- p
- 'I''m feeling somewhat inspired by '
- - a
  - href: http://www.jsonml.org/
  - JSONML
- '.  The resulting JSON format could be rendered in YAML.  For example, this paragraph would look like the following:'
```

Though, I don't like the quote for strings with spaces, which also requires
too much escaping to be efficient with the crazy automated linking in ANOI.  I
guess for that reason, I should strongly consider just using markdown...

There is a decent HTML to markdown story using the `markdownify` module (see
the [Github repo](https://github.com/matthewwithanm/python-markdownify)).  This
could be a gateway to LaTeX by way of
[LaTeX2HTML](https://www.latex2html.org/)....

This kinda sidesteps the issue of serializing tree data in ANOI, but I would
consider that a separate issue.  If I'm dying to do that, I can always use
markdown trees:

```markdown
- p
- I'm feeling somewhat inspired by
  - a
  - @attributes
    - href
    - http://www.jsonml.org/
  - JSONML
- .  The resulting...
```

*Shudder*...

### 2021.10.24

I'm breaking the design into two pieces:
* ANOI Design, which gives an _external_ design of spatial characteristics.
* Design Internals, which specifies the _internal_ design of support software.

Ideally, we'd like to bootstrap this into it's own domain-specific language and
self host via some predefined "boot" sequence, but that's going to require
some infrastructure first.

That kinda leads me in some weird directions.  For example, how do you code a
presentation layer in the DSL without some notion of a byte?  Maybe we should
have a UID range or set for the various "puns" that already exist in the ANOI
design.

```
BYTE := 0 <= UID < 256
CODE_POINT := 0 <= UID < 0x110000
MEDIA := vec<BYTE>
STRING := vec<CODE_POINT>
```

### 2021.10.27

Today's plan:

1. ✔ Download WordNet 3.1 [here](https://wordnet.princeton.edu/download/current-version)
2. Write loader
3. Load into a test space
4. Initial article loader, which is a simple compress call on the input string
5. Verify compression (and linking) is happening

#### Aside:

* How can I store UTF-8 strings in a binary space without using all 4 bytes
  per code point (which ANOIRedis32Space does)?  One possibility is to "pun"
  since bytes are valid code points, but even then, any code point above 127
  would incur a double encoding penalty, creating a possible 8 byte worst case
  size. ATF? ANOI transfer format (ATF-8), which follows UTF-8 rules taken to
  arbitrary bit depth.

| First UID | Last UID | Byte 1   | Byte 2   | Byte 3 | Byte 4 | Byte 5 | Byte 6 | Byte 7 |Bits |
|----------:|---------:|----------|----------|--------|--------|--------|--------|--------|----:|
| 0         | 0x7f     | 0xxxxxxx |          |        |        |        |        |        | 7   |
| 0x80      | 0x7ff    | 110xxxxx | 10xxxxxx |        |        |        |        |        | 11  |
| 0x800     | 0xffff   | 1110xxxx | 10xxxxxx | 10xxxxxx |      |        |        |        | 16  |
| 0x10000   | 0x1fffff | 11110xxx | 10xxxxxx | 10xxxxxx | 10xxxxxx |    |        |        | 21  |
| 0x200000  | 0x3ffffff| 111110xx | 10xxxxxx | 10xxxxxx | 10xxxxxx | 10xxxxxx|   |        | 26  |
| 0x4000000 |0x7fffffff| 1111110x | 10xxxxxx | 10xxxxxx | 10xxxxxx | 10xxxxxx | 10xxxxxx| | 31  |
| 0x80000000|0xfffffffff|11111110 | 10xxxxxx | 10xxxxxx | 10xxxxxx | 10xxxxxx | 10xxxxxx | 10xxxxxx |36|
|0x1000000000|2\*\*41-1 |11111111 | 100xxxxx | ...      |          |          |          |          |41|
| 2\*\*41    |2\*\*46-1 |11111111 | 1010xxxx | ...      |          |          |          |          |46|

So for _n_ bytes, _n >= 2_, there are _11 + 5 \* (n - 2)_ bits available,
meaning 64-bit integers can blow up to 13 bytes under this encoding (12 bytes,
61 bits -> (2\*\*62-1) < (2\*\*64-1) < (2\*\*66-1) <- 13 bytes, 66 bits).

### 2021.11.04

So after bootstrapping a root trie, we need a "type module"...or do we?  It
almost seems like too much complexity.  I'm not for polluting the builtin
names, but when I start mapping reflective types to ANOI, I get in deep water
quickly.  Parametric/generic types?  Enumerations?  Types versus type
instances?  A lot of these notions weren't present in Python when I wrote the
original proposal, but now I rely on them, and I'd like to see them reflected
into ANOI.

What is a "module" anyway?  How does it differ from a "namespace"?
