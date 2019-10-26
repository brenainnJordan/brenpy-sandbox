Archived at a point where I think we've more or less reached the reasonable limits of attempting to link everything with persistant models.

There's a ton of interconnectivity and dependencies on other models, and cache states etc.
Which I think is just going to lead towards too much instability, and convuluted structures,
and just generally not particularly easiliy maintainable.

Next attempt I think will return to the idea of "on-demand" temporary models.

Models such as property models will be created only when we need to display/edit/select properties,
for example when selecting an object from the scene, or selecting a property for a new connection.

In both cases (and other similar cases) this frees us up from the need to keep models in sync,
or the need to rely on a source model and somewhat clunky proxy models, we can simply create a
new property cache in the structure we need for that particular use case, in a simple and easily
maintainable isolated environment.

This all stems from the inability to connect directly to fbx objects, given their volatile nature.

As such this approach reflects the limits of the fbx sdk, rather than trying to work around them.

One consequence of this is that models will likely become out of date, this is no different to how
proxy model caches can get out of date, however in this case the responsibility of "refreshing"
models will fall to a single python object that can manage and recache models on demand,
for example if a view has a method to create a new property, then it can either connect to or call
directly the refresh method.

Also worth exposing a mechanism to the user to refresh all models.

I think we can still keep the tab idea, but again, refreshing where neccesary.

