# Data model

## Overall

The canonical model closely follows the [TTML 2](https://www.w3.org/TR/ttml2) data model, as constrained by the [IMSC 1.1 Text Profile](https://www.w3.org/TR/ttml-imsc1.1/#text-profile) specification. This includes both the static structure of the model as well as temporal, layout and style processing. The objective is for a valid IMSC 1.1 Text Profile document to be mapped into a canonical model instance such that presenting instance results in the same outout as the input IMSC document.

The canonical model is specified in `ttconv.model`.

The class hierarchy of the canonical model is summarized the following figure:

```txt
  Document
    : Region* Body?

  Body
    : Div*
  
  Div
    : (P | Div)*
  
  P
    : (Span | Ruby | Br)*
  
  Span
    : (Span | Br | Text)*
  
  Ruby
    : Rb? Rt?
    | Rb? Rp Rt? Rp
    | Rbc Rtc Rtc?
  
  Rbc
    : Rb*
  
  Rtc
  : Rt*
  | Rp Rt* Rp

  Rb, Rt, Rp
    : Span*
```

where:

* the `Document` class corresponds to the `tt` element
* the `Body`, `Div`, `P`, `Span`, `Br` and `Region` classes corresponds to the TTML content element of the same name, respectively
* the `Text` class corresponds to a TTML text node
* the `Ruby`, `Rt`, `Rb`, `Rtc`, `Rbc`, `Rp` classes correspond to the TTML `span` element with the computed value of `tts:ruby` attribute specified in the following table

| Canonical model class | Computed value of `tts:ruby` attribute |
|-----------------------|----------------------------------------|
| `Ruby`                | `container`                            |
| `Rt`                  | `text`                                 |
| `Rb`                  | `base`                                 |
| `Rtc`                 | `textContainer`                        |
| `Rbc`                 | `baseContainer`                        |
| `Rp`                  | `delimiter`                            |

## Basic operation

The canonical model allows content elements (instances of `ttconv.model.ContentElement`) to be arranged in a hierarchical structures (using the `ttconv.model.ContentElement.push_child()` and `ttconv.model.ContentElement.remove_child()`) that are associated with a single document (using the `ttconv.model.ContentElement.set_doc()` method with an instance of `ttconv.model.Document`).

## Divergences with the TTML data model

### Initial values

The TTML `initial` elements are accessed using the `Document.set_initial_value()` and `Document.get_initial_value()` method.

### Styling

Style properties are access using the `ContentElement.get_style()` and `ContentElement.set_style()` methods.

The style properties themselves are defined in `ttconv.style_properties`, where the lower camel case names used in TTML are replaced by their equivalent in upper camel case. Deprecated style properties, e.g. `tts:zIndex` are not supported.

Only _inline styling_ of content elements is supported, and neither _referential sytling_ nor _chained referential styling_ nor _nested styling_ are supported.

### Metadata

TTML `metadata` elements are not supported.

### Timing

Only _parallel time container_ semantics are supported and temporal offsets are expressed as `fractions.Fraction` instances in seconds. As a result, the following parameters are not supported: `ttp:frameRate`, `ttp:frameRateMultiplier`, `ttp:subFrameRate`, `ttp:tickRate`.

Writer module can express temporal offsets in units of ticks, frames, etc. as demanded by the output format or configured by the user.

The `dur` timing attribute is not supported.

### Position

The `tts:position` style property is not supported and `tts:origin` is used instead.

### Lengths

The constraints against length units specified in IMSC are relaxed, and lengths can be expressed in `c`, `%`, `rh`, `rw`, `em` and `px` units.