# Champion Photos

Add one image per fighter using the fighter database ID as the filename:

```text
public/champions/<fighter-id>.jpg
```

Example: `public/champions/12.jpg`.

The API `fighter.photo_url` takes priority when it is populated. Local ID-based images are the fallback, so adding a new champion does not require a frontend code change.
