
Changelog
=========

v0.1.x

*Unreleased*

- Rename ``nodejs_upstream_repo`` to ``nodejs_upstream_repository``
  for consistency with other ``debops`` roles. [patrickheeney]

- Rename ``nodejs_npm_packages`` to ``nodejs_global_packages`` to
  better reflect their purpose. [patrickheeney]

- Remove npm installer as it is now bundled with node.js.
  [patrickheeney]

- Rename ``nodejs_packages`` to ``nodejs_base_packages`` to allow
  ``nodejs_packages`` to be used for user packages. [patrickheeney]

- Refactor apt keys and apt repositories. [patrickheeney]

v0.1.0
------

*Released: xxx*

- Initial release. [drybjed]

