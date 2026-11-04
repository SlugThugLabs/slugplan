# slugplan

A tiny Rust library that creates a project's `.planning/` folder and
`.planning/README.md` the same way in every slug tool. If either already
exists it is left alone; slugplan never overwrites or reads an existing file.

## Use

```toml
slugplan = { git = "https://github.com/SlugThugLabs/slugplan", tag = "v0.1.0" }
```

```rust
let report = slugplan::ensure(root)?;
```

`root` must already exist. The returned `Report` says which of the two
were created.

The README text lives in `src/planning_readme.md`.

## License

PolyForm Noncommercial 1.0.0 with a tool-use permission, the same terms as
SlugAudit. See `LICENSE`.
