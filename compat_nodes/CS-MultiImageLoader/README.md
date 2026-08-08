# CS-MultiImageLoader compatibility package

The supplied `MiniMax+H3多条件参考低显存加速版工作流.json` includes a `CS-MultiImageLoader` node but its package identifier is absent from the ComfyUI-Manager local catalogue and a GitHub exact code search returned no source. This minimal compatibility package is scoped to that node only:

- preserves its existing node type, seven inputs and five `IMAGE` outputs;
- reads up to four newline-separated files from ComfyUI's input directory;
- supports its documented crop/stretch and interpolation choices;
- does not alter the supplied workflow graph.

Remove this package if the original upstream node is later identified and validated against the workflow.
