# ISD

An Intermediate Synchronic Document (ISD) represents a snapshot of a `ContentDocument` at specified moment in time.

The ISD model is specified in `ttconv.isd`.

The class hierarchy of the canonical model is summarized the following figure:

```txt
  ISD
    : ISD.Region*

  ISD.Region:
    : Body
```

where `Body` is an instance of the `Body` class of the data model. In other words, each region of an ISD contains a copy of all the
elements of the source ContentDocument that are active within the region.

For example, the ISD at t=2s of the document:

```xml
  <region xml:id="r1" tts:showBackground="always"/>
  <region xml:id="r2" begin="2s" end="9s">
    <set tts:color="red"/>
  </region>
  ...
  <body begin="1s" end="10s">
    <div begin="3s" region="r1">
      <set begin="1s" tts:color="green"/>
    </div>
    <div end="12s" region="r2">
      <p>
        <span>hello</span>
      </p>
    </div>
  </body>
```

is:

```xml
  <region xml:id="r1" tts:showBackground="always"/>
  <region xml:id="r2" tts:color="red">
    <body >
      <div>
        <p>
          <span>hello</span>
        </p>
      </div>
    </body>
  </region>
```

An ISD contains no timing information, i.e. no `begin` or `end` properties, or animation steps.

Both the `Origin` and `Position` style properties are always equal.

All lengths are expressed in root-relative units `rh` and `rw`.
