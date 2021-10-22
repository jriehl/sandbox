A Network of Ideas
==================

A stab in the dark towards concept oriented programming.
Original proposal: https://wildideas.org/anoi/

Design
------

### Types

TODO.

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
  subsequent lexicon stacks.  Warnings:
  - This may screw things up if the lexicon doesn't have a 1:1 correspondence
    with titles.  Possible fix: add alias dimension to lexicon keys.

TODO's
------
- [ ] Port to Unicode
  - [x] Trie implementation
  - [ ] Decompressor
  - [ ] Unit tests of port
- [ ] Loaders
  - [ ] Markdown
  - [ ] HTML
  - [ ] Latex
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
