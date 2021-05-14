Changelog is normally kept [here](https://github.com/Cervi-Robotics/interceptor/releases).

This is only for new-version changes:

# v2.0

* major refactor
* `reset` will tell you if the configuration was a symlink
* merged the role of `check` and `status` into a single `status` command
* added the support for recognizing partial interceptions,
  where not all executables of given file were patched
* fixed a bug wherein interceptor would try to intercept directories
* can skip intercept check with `--force`
* `status` will also check for existence of -intercepted files
* fixed logic of determining whether an app is intercepted
