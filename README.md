# vivaldi-arc-setup

Makes Vivaldi on macOS look and behave like Arc: VivalArc mod, sage-green sidebar with grain,
auto-hiding sidebar with the URL bar inside it, Arc-style ⌘T command bar, automatic
picture-in-picture, Google search, and ad/tracker blocking with uBlock Origin's lists.

```bash
bash setup.sh
```

Instructions in French: [LISEZMOI.md](LISEZMOI.md).

## Credits

- [tovifun/VivalArc](https://github.com/tovifun/VivalArc) provides the base mod (`vivalarc.css`) and the
  ArcLight/ArcDark themes. They aren't redistributed here: `setup.sh` downloads them from that repo,
  pinned to a known commit.
- Filter lists are downloaded at setup time from [uBlockOrigin/uAssets](https://github.com/uBlockOrigin/uAssets).
