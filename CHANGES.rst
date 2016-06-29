
Changelog
=========

v0.2.0
------

*Released: 2016-06-29*

- Rename ``nodejs_upstream_repo`` to ``nodejs_upstream_repository``
  for consistency with other ``debops`` roles. [patrickheeney]

- Rename ``nodejs_npm_packages`` to ``nodejs_npm_global_packages``
  to better reflect their purpose. [patrickheeney]

- Rename ``nodejs_packages`` to ``nodejs_base_packages`` to allow
  ``nodejs_packages`` to be used for user packages. [patrickheeney]

- Remove npm installer as it is now bundled with node.js.
  [patrickheeney]

- Remove npm /tmp directory override. It will now use npm defaults.
  [patrickheeney]

- Refactor apt keys and apt repositories. [patrickheeney]

v0.1.0
------

*Released: 2015-09-20*

- Initial release. [drybjed]

